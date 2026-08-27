"""Plugin de TYRELL para el microkernel RIPLEY."""

from pathlib import Path
from typing import Dict, Any
from tyrell.core.models import DatasetSpec, DatasetRule
from tyrell.core.generator_engine import generate_dataset


class TyrellPlugin:
    """Plugin de generación sintética de datasets para Ripley."""

    name = "dataset_generator"
    description = "Generación sintética de testcases deterministas (.in/.out) para arnés de pruebas"

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        count = context.get("testcases_count", 5)
        seed = context.get("seed", 42)
        out_dir = Path(context.get("testcases_dir", "tests_generated"))

        spec = DatasetSpec(
            name="auto",
            count=count,
            seed=seed,
            format_template="{n}\n",
            rules=[DatasetRule(name="n", type="integer", min_val=1, max_val=100)]
        )

        testcases = generate_dataset(spec, output_dir=out_dir)

        return {
            "passed": True,
            "generated_count": len(testcases),
            "output_dir": str(out_dir)
        }
