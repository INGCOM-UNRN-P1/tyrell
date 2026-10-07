"""Motor determinista de generación de casos de prueba según reglas."""

import random
import string
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from tyrell.core.models import DatasetRule, DatasetSpec, GeneratedTestCase

INT_MAX = 2147483647
INT_MIN = -2147483648

# Bordes de las cadenas (QoL #974, #976): vacía, solo espacios, espacios repetidos o al borde,
# tabulaciones y saltos de línea consecutivos. El parsing de tokens del estudiante falla ahí.
_BORDES_CADENA = ["", " ", "a  b", "  al borde  ", "\t", "\t\tx", "a\n\nb"]


def bordes(rule: DatasetRule) -> List[Any]:
    """Los casos de borde de una regla, en un orden fijo, para que todos aparezcan (QoL #974–#976)."""
    t = rule.type.lower()
    if t in ("integer", "int"):
        acotada = rule.min_val is not None or rule.max_val is not None
        min_v = rule.min_val if rule.min_val is not None else -1000
        max_v = rule.max_val if rule.max_val is not None else 1000
        candidatos = [min_v, max_v, 0, -1, 1, min_v + 1, max_v - 1]
        if not acotada:
            # Sin límites declarados también los del tipo int: desbordes en sumas y productos.
            candidatos += [INT_MAX, INT_MIN]
        else:
            candidatos = [v for v in candidatos if min_v <= v <= max_v]
        return list(dict.fromkeys(candidatos))
    if t in ("float", "double"):
        min_f = float(rule.min_val) if rule.min_val is not None else -1000.0
        max_f = float(rule.max_val) if rule.max_val is not None else 1000.0
        return list(dict.fromkeys([min_f, max_f, 0.0, -1.0, 1.0, 1e-6]))
    if t == "string":
        return _BORDES_CADENA + ["A" * (rule.length or 10)]
    if t == "array":
        min_v = rule.min_val if rule.min_val is not None else 0
        max_v = rule.max_val if rule.max_val is not None else 100
        largo = max(rule.length or 5, 2)
        ascendente = [min_v + (max_v - min_v) * k // (largo - 1) for k in range(largo)]
        # Vacío, un solo elemento, todos iguales, ordenado y en orden inverso.
        return [[], [min_v], [max_v] * largo, ascendente, list(reversed(ascendente))]
    return ["1"]


def _ordenar(valores: List[int], orden: str, rng: random.Random) -> List[int]:
    """`ordenado`, `inverso` o `casi_ordenado` (ordenado con ~5 % de pares intercambiados, QoL #977)."""
    if orden == "aleatorio":
        return valores
    valores = sorted(valores, reverse=(orden == "inverso"))
    if orden == "casi_ordenado" and len(valores) > 1:
        for _ in range(max(1, len(valores) // 20)):
            i = rng.randrange(len(valores) - 1)
            valores[i], valores[i + 1] = valores[i + 1], valores[i]
    return valores


def generate_value(rule: DatasetRule, rng: random.Random, is_edge_case: bool = False, largo: Optional[int] = None) -> Any:
    """Genera un valor individual según el tipo y límites de la regla.

    `largo` reemplaza la longitud de la regla (cadenas y arreglos): lo usa el caso de estrés."""
    t = rule.type.lower()
    if is_edge_case:
        return rng.choice(bordes(rule))

    if t in ("integer", "int"):
        min_v = rule.min_val if rule.min_val is not None else -1000
        max_v = rule.max_val if rule.max_val is not None else 1000
        return rng.randint(min_v, max_v)

    elif t in ("float", "double"):
        min_f = rule.min_val if rule.min_val is not None else -1000.0
        max_f = rule.max_val if rule.max_val is not None else 1000.0
        return round(rng.uniform(min_f, max_f), 4)

    elif t == "string":
        chars = rule.charset or (string.ascii_letters + string.digits)
        length = largo or rule.length or 10
        return "".join(rng.choice(chars) for _ in range(length))

    elif t == "array":
        min_v = rule.min_val if rule.min_val is not None else 0
        max_v = rule.max_val if rule.max_val is not None else 100
        length = largo or rule.length or 5
        return _ordenar([rng.randint(min_v, max_v) for _ in range(length)], rule.orden, rng)

    return str(rng.randint(1, 100))


def _contenido(spec: DatasetSpec, valores_por_regla: Dict[str, Any]) -> str:
    values: Dict[str, Any] = {}
    for r in spec.rules:
        val = valores_por_regla[r.name]
        if isinstance(val, list):
            values[r.name] = " ".join(str(x) for x in val)
            values[f"{r.name}_n"] = len(val)  # la cantidad de elementos, para "{v_n}\n{v}"
        else:
            values[r.name] = val
    content = spec.format_template.format(**values)
    return content if content.endswith("\n") else content + "\n"


def _corromper(contenido: str, k: int, rng: random.Random) -> str:
    """Entradas corruptas (QoL #973): truncada, con bytes no imprimibles, sin el salto de línea
    final, con letras donde van números o vacía. El programa no debería colgarse ni romperse."""
    tipo = k % 5
    if tipo == 0:
        return contenido[: max(1, len(contenido) // 2)]
    if tipo == 1:
        i = rng.randrange(len(contenido) + 1)
        return contenido[:i] + "\x01\x7f" + contenido[i:]
    if tipo == 2:
        return contenido.rstrip("\n")
    if tipo == 3:
        digitos = [i for i, c in enumerate(contenido) if c.isdigit()]
        if digitos:
            i = rng.choice(digitos)
            return contenido[:i] + "x" + contenido[i + 1:]
        return "x" + contenido
    return ""


def _salida_de_referencia(reference_binary: Path, content: str, timeout: float):
    try:
        res = subprocess.run(
            [str(reference_binary)],
            input=content,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        return res.stdout, None
    except Exception as exc:
        # No se inventa un `.out` vacío: el caso queda sin salida esperada y se avisa.
        return None, f"la referencia falló para este caso ({type(exc).__name__}); no se escribió el .out"


def generate_dataset(
    spec: DatasetSpec,
    output_dir: Optional[Path] = None,
    reference_binary: Optional[Path] = None
) -> List[GeneratedTestCase]:
    """Genera una colección completa de casos de prueba deterministas.

    Los primeros casos son de borde (cada regla recorre sus bordes en orden, así que con
    suficientes casos aparecen todos); después, aleatorios. Con `corruptos` y `estres_longitud`
    se suman casos corruptos y uno de estrés al final.
    """
    if reference_binary is not None and not reference_binary.exists():
        # Antes no se escribía ningún `.out` y nada lo avisaba.
        raise FileNotFoundError(f"El binario de referencia no existe: {reference_binary}")
    rng = random.Random(spec.seed)
    reglas = spec.rules or [DatasetRule(name="x", type="integer", min_val=1, max_val=100)]
    if not spec.rules:
        spec = spec.model_copy(update={"rules": reglas, "format_template": "{x}\n"})
    con_bordes = [r for r in reglas if r.include_extremes]
    cantidad_bordes = min(spec.count, max((len(bordes(r)) for r in con_bordes), default=0))

    casos: List[tuple] = []  # (contenido, tipo)
    for i in range(spec.count):
        valores = {}
        for r in reglas:
            if i < cantidad_bordes and r.include_extremes:
                lista = bordes(r)
                valores[r.name] = lista[i % len(lista)]
            else:
                valores[r.name] = generate_value(r, rng)
        casos.append((_contenido(spec, valores), "borde" if i < cantidad_bordes and con_bordes else "normal"))

    for k in range(spec.corruptos):
        base = _contenido(spec, {r.name: generate_value(r, rng) for r in reglas})
        casos.append((_corromper(base, k, rng), "corrupto"))

    if spec.estres_longitud:
        valores = {r.name: generate_value(r, rng, largo=spec.estres_longitud) for r in reglas}
        casos.append((_contenido(spec, valores), "estres"))

    testcases: List[GeneratedTestCase] = []
    for i, (content, tipo) in enumerate(casos, 1):
        sufijo = "" if tipo in ("normal", "borde") else f"_{tipo}"
        in_name = f"{i:02d}_{spec.name}{sufijo}.in"
        out_name: Optional[str] = f"{i:02d}_{spec.name}{sufijo}.out" if reference_binary else None
        output_str = None
        advertencia = None
        if reference_binary:
            output_str, advertencia = _salida_de_referencia(reference_binary, content, 10 if tipo == "estres" else 2)
            if output_str is None:
                out_name = None

        testcases.append(GeneratedTestCase(
            index=i,
            input_content=content,
            output_content=output_str,
            in_filename=in_name,
            out_filename=out_name,
            advertencia=advertencia,
            tipo=tipo,
        ))

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / in_name).write_text(content, encoding="utf-8")
            if output_str is not None and out_name:
                (output_dir / out_name).write_text(output_str, encoding="utf-8")

    return testcases
