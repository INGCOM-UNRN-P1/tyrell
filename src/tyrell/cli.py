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


@app.command()
def generate(
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
    """Genera casos de prueba .in (y .out con binario de referencia) deterministas."""
    if spec_file and spec_file.exists():
        raw_yaml = yaml.safe_load(spec_file.read_text(encoding="utf-8"))
        spec = DatasetSpec(**raw_yaml)
    else:
        spec = DatasetSpec(
            name="case",
            count=count,
            seed=seed,
            format_template="{val}\n",
            rules=[DatasetRule(name="val", type=type_name, min_val=min_val, max_val=max_val)]
        )

    testcases = generate_dataset(spec, output_dir=output_dir, reference_binary=reference_binary)

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


if __name__ == "__main__":
    app()
