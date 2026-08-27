"""Motor determinista de generación de casos de prueba según reglas."""

import random
import string
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from tyrell.core.models import DatasetSpec, DatasetRule, GeneratedTestCase


def generate_value(rule: DatasetRule, rng: random.Random, is_edge_case: bool = False) -> Any:
    """Genera un valor individual según el tipo y límites de la regla."""
    t = rule.type.lower()

    if t in ("integer", "int"):
        min_v = rule.min_val if rule.min_val is not None else -1000
        max_v = rule.max_val if rule.max_val is not None else 1000
        if is_edge_case:
            return rng.choice([min_v, max_v, 0, -1, 1, 2147483647, -2147483648])
        return rng.randint(min_v, max_v)

    elif t in ("float", "double"):
        min_v = rule.min_val if rule.min_val is not None else -1000.0
        max_v = rule.max_val if rule.max_val is not None else 1000.0
        if is_edge_case:
            return rng.choice([0.0, -0.0, 1.0, -1.0, 1e-6, float(min_v), float(max_v)])
        return round(rng.uniform(min_v, max_v), 4)

    elif t == "string":
        chars = rule.charset or (string.ascii_letters + string.digits)
        length = rule.length or 10
        if is_edge_case:
            return rng.choice(["", " ", "\n", "A" * length, "0", "\t\t"])
        return "".join(rng.choice(chars) for _ in range(length))

    elif t == "array":
        min_v = rule.min_val if rule.min_val is not None else 0
        max_v = rule.max_val if rule.max_val is not None else 100
        length = rule.length or 5
        if is_edge_case:
            return [0] * length
        return [rng.randint(min_v, max_v) for _ in range(length)]

    return str(rng.randint(1, 100))


def generate_dataset(
    spec: DatasetSpec,
    output_dir: Optional[Path] = None,
    reference_binary: Optional[Path] = None
) -> List[GeneratedTestCase]:
    """Genera una colección completa de casos de prueba deterministas."""
    rng = random.Random(spec.seed)
    testcases: List[GeneratedTestCase] = []

    for i in range(1, spec.count + 1):
        # Primeros casos son casos borde extremos si include_extremes está activo
        is_edge = (i <= 2)
        values: Dict[str, Any] = {}

        if not spec.rules:
            # Regla por defecto (entero)
            val = generate_value(DatasetRule(name="x", type="integer", min_val=1, max_val=100), rng, is_edge)
            content = f"{val}\n"
        else:
            for r in spec.rules:
                val = generate_value(r, rng, is_edge)
                if isinstance(val, list):
                    values[r.name] = " ".join(str(x) for x in val)
                else:
                    values[r.name] = val

            content = spec.format_template.format(**values)
            if not content.endswith("\n"):
                content += "\n"

        in_name = f"{i:02d}_{spec.name}.in"
        out_name = f"{i:02d}_{spec.name}.out" if reference_binary else None
        output_str = None

        if reference_binary and reference_binary.exists():
            try:
                res = subprocess.run(
                    [str(reference_binary)],
                    input=content,
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False
                )
                output_str = res.stdout
            except Exception:
                output_str = ""

        tc = GeneratedTestCase(
            index=i,
            input_content=content,
            output_content=output_str,
            in_filename=in_name,
            out_filename=out_name
        )
        testcases.append(tc)

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / in_name).write_text(content, encoding="utf-8")
            if output_str is not None:
                (output_dir / out_name).write_text(output_str, encoding="utf-8")

    return testcases
