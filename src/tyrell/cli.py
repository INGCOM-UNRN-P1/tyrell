"""CLI principal de TYRELL."""

import json
from pathlib import Path
from typing import Optional
import typer
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from tyrell.core.models import DatasetSpec, DatasetRule
from tyrell.core.generator_engine import generate_dataset

app = typer.Typer(
    name="tyrell",
    help="Generador sintético y determinista de datasets y casos de prueba (.in/.out)",
    add_completion=True
)
console = Console()
err_console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        from tyrell import __version__
        typer.echo(f"TYRELL versión {__version__}")
        raise typer.Exit(code=0)


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="Muestra la versión y termina.",
        callback=_version_callback, is_eager=True,
    ),
) -> None:
    """Opciones globales."""


@app.command()
def generate(
    ctx: typer.Context,
    spec_file: Optional[Path] = typer.Argument(None, help="Archivo YAML de especificación de dataset"),
    count: int = typer.Option(10, "--count", "-n", help="Cantidad de casos de prueba a generar"),
    seed: int = typer.Option(42, "--seed", "-s", help="Semilla para reproducibilidad"),
    type_name: str = typer.Option("integer", "--type", "-t", help="Tipo de dato si no se pasa YAML (integer, float, string, array)"),
    min_val: int = typer.Option(0, "--min", help="Valor mínimo"),
    max_val: int = typer.Option(100, "--max", help="Valor máximo"),
    output_dir: Path = typer.Option(Path("tests"), "--output", "-o", help="Directorio de destino de los archivos .in/.out"),
    reference_binary: Optional[Path] = typer.Option(None, "--reference", "-r", help="Binario ejecutable de referencia para generar los .out"),
    json_output: bool = typer.Option(False, "--json", help="Emitir salida en formato JSON estructurado")
):
    """Genera casos de prueba .in (y .out con binario de referencia) deterministas.

    Con un YAML, la especificación manda: `--count`, `--seed`, `--type`, `--min`
    y `--max` se ignoran (se avisa cuáles). Sin YAML se usan esas opciones.
    """
    if spec_file is not None:
        if not spec_file.is_file():
            # Antes caía al dataset por defecto con exit 0, y el usuario creía
            # haber generado desde su YAML.
            err_console.print(f"[bold red]No existe el archivo de especificación:[/bold red] {spec_file}")
            raise typer.Exit(code=2)

        try:
            raw_yaml = yaml.safe_load(spec_file.read_text(encoding="utf-8"))
            if not isinstance(raw_yaml, dict):
                raise ValueError("el YAML debe ser un mapa con las claves de la especificación")
            spec = DatasetSpec(**raw_yaml)
        except (yaml.YAMLError, ValueError, TypeError) as exc:
            err_console.print(f"[bold red]Especificación inválida en {spec_file}:[/bold red]\n{exc}")
            raise typer.Exit(code=2)

        ignoradas = [
            f"--{nombre}"
            for nombre in ("count", "seed", "type_name", "min_val", "max_val")
            # Se compara por nombre para no depender de importar `click`, que
            # typer trae integrado y no es una dependencia declarada de tyrell.
            if getattr(ctx.get_parameter_source(nombre), "name", "") == "COMMANDLINE"
        ]
        if ignoradas:
            err_console.print(
                f"[yellow]Aviso:[/yellow] con un YAML la especificación tiene precedencia; "
                f"se ignoran {', '.join(ignoradas).replace('type_name', 'type').replace('min_val', 'min').replace('max_val', 'max')}."
            )
    else:
        spec = DatasetSpec(
            name="case",
            count=count,
            seed=seed,
            format_template="{val}\n",
            rules=[DatasetRule(name="val", type=type_name, min_val=min_val, max_val=max_val)]
        )

    try:
        testcases = generate_dataset(spec, output_dir=output_dir, reference_binary=reference_binary)
    except FileNotFoundError as exc:
        err_console.print(f"[bold red]{exc}[/bold red]")
        raise typer.Exit(code=2)
    for tc in testcases:
        if tc.advertencia:
            err_console.print(f"[yellow]Aviso caso {tc.index}:[/yellow] {tc.advertencia}")

    if json_output:
        data = [tc.model_dump() for tc in testcases]
        print(json.dumps({"count": len(testcases), "testcases": data}, indent=2, ensure_ascii=False))
        return

    table = Table(title=f"Casos de Prueba Generados ({len(testcases)} archivos)", show_header=True, header_style="bold green")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Archivo .in", style="yellow")
    table.add_column("Payload (preview)", style="white")
    table.add_column("Archivo .out", style="blue")

    for tc in testcases:
        preview = repr(tc.input_content[:30])
        out_col = tc.out_filename if tc.out_filename else "[dim]N/A (sin binario)[/dim]"
        table.add_row(str(tc.index), tc.in_filename, preview, out_col)

    console.print(table)
    console.print(f"\n[bold green]✓ {len(testcases)} testcases guardados exitosamente en:[/bold green] {output_dir}")


@app.command()
def version():
    """Muestra la versión de TYRELL."""
    from tyrell import __version__
    console.print(f"[bold cyan]TYRELL[/bold cyan] versión [green]{__version__}[/green]")


@app.command("doctor")
def doctor_cmd(
    json_output: bool = typer.Option(False, "--json", help="Emitir diagnóstico en formato JSON estructurado."),
) -> None:
    """Verifica el estado del entorno de TYRELL (Python, GCC opcional)."""
    import shutil
    import sys
    diagnostico = []

    py_ok = sys.version_info >= (3, 10)
    diagnostico.append({
        "componente": "Python Runtime",
        "estado": "OK" if py_ok else "ERROR",
        "requerido": True,
        "detalle": f"Python {sys.version.split()[0]}",
    })

    gcc_path = shutil.which("gcc")
    diagnostico.append({
        "componente": "Compilador GCC",
        "estado": "OK" if gcc_path else "ADVERTENCIA",
        "requerido": False,
        "detalle": gcc_path or "No encontrado (opcional, para compilar binarios de referencia)",
    })

    todo_ok = py_ok

    if json_output:
        payload = {
            "schema_version": "1.0.0",
            "herramienta": "tyrell",
            "ok": todo_ok,
            "componentes": diagnostico,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        raise typer.Exit(code=0 if todo_ok else 1)

    tabla = Table(title="🏥 Diagnóstico del Entorno TYRELL (doctor)", border_style="cyan")
    tabla.add_column("Componente", style="bold white")
    tabla.add_column("Estado", justify="center")
    tabla.add_column("Detalle")

    for c in diagnostico:
        color = "bold green" if c["estado"] == "OK" else ("bold yellow" if c["estado"] == "ADVERTENCIA" else "bold red")
        simbolo = "✓" if c["estado"] == "OK" else ("⚠️" if c["estado"] == "ADVERTENCIA" else "✗")
        tabla.add_row(c["componente"], f"[{color}]{simbolo} {c['estado']}[/{color}]", c["detalle"])

    console.print(tabla)
    if not todo_ok:
        raise typer.Exit(code=1)



if __name__ == "__main__":
    app()
