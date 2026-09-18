"""Regresión de TYRELL-D0801: el README declaraba alimentar a nostromo sin ninguna prueba.

Se genera una suite con binario de referencia y se la evalúa con el propio
descubridor y evaluador de nostromo: si el formato de los `.in`/`.out` no fuera
el que nostromo lee, ningún caso pasaría.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tyrell.core.generator_engine import generate_dataset
from tyrell.core.models import DatasetRule, DatasetSpec

NOSTROMO_SRC = Path(__file__).resolve().parents[2] / "nostromo" / "src"

try:
    import nostromo  # noqa: F401
except ImportError:
    if NOSTROMO_SRC.is_dir():
        sys.path.insert(0, str(NOSTROMO_SRC))

nostromo = pytest.importorskip("nostromo.core.runner", reason="nostromo no está disponible")
necesita_gcc = pytest.mark.skipif(not shutil.which("gcc"), reason="requiere gcc")

REFERENCIA = """#include <stdio.h>
int main(void) {
    int a, b;
    if (scanf("%d %d", &a, &b) == 2) printf("%d\\n", a + b);
    return 0;
}
"""


@necesita_gcc
def test_una_suite_generada_por_tyrell_es_evaluable_por_nostromo(tmp_path):
    fuente = tmp_path / "suma.c"
    fuente.write_text(REFERENCIA, encoding="utf-8")
    binario = tmp_path / "suma"
    subprocess.run(["gcc", str(fuente), "-o", str(binario)], check=True)

    spec = DatasetSpec(
        name="suma", count=6, seed=7, format_template="{a} {b}\n",
        rules=[
            DatasetRule(name="a", type="integer", min_val=-50, max_val=50),
            DatasetRule(name="b", type="integer", min_val=-50, max_val=50),
        ],
    )
    suite = tmp_path / "suite"
    generate_dataset(spec, output_dir=suite, reference_binary=binario)

    casos = nostromo.descubrir_casos_prueba(suite)
    assert len(casos) == 6
    assert all(c.stdin_texto and c.stdout_esperado for c in casos)

    reporte = nostromo.evaluar_binario(binario, casos, integrar_hal=False)
    assert reporte.casos_aprobados == 6 and reporte.ok


@necesita_gcc
def test_un_binario_con_un_defecto_falla_algun_caso_de_la_suite_generada(tmp_path):
    referencia = tmp_path / "ref.c"
    referencia.write_text(REFERENCIA, encoding="utf-8")
    ref_bin = tmp_path / "ref"
    subprocess.run(["gcc", str(referencia), "-o", str(ref_bin)], check=True)
    mala = tmp_path / "mala.c"
    mala.write_text(REFERENCIA.replace("a + b", "a - b"), encoding="utf-8")
    mala_bin = tmp_path / "mala"
    subprocess.run(["gcc", str(mala), "-o", str(mala_bin)], check=True)

    spec = DatasetSpec(
        name="suma", count=6, seed=7, format_template="{a} {b}\n",
        rules=[DatasetRule(name="a", type="integer", min_val=1, max_val=50),
               DatasetRule(name="b", type="integer", min_val=1, max_val=50)],
    )
    suite = tmp_path / "suite"
    generate_dataset(spec, output_dir=suite, reference_binary=ref_bin)
    reporte = nostromo.evaluar_binario(mala_bin, nostromo.descubrir_casos_prueba(suite), integrar_hal=False)
    assert reporte.casos_fallidos > 0
