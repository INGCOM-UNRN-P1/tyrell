"""Regresión de TYRELL-D0303 (include_extremes) y TYRELL-D0304 (.out degradado en silencio)."""

import json
import stat

from typer.testing import CliRunner

from tyrell.cli import app
from tyrell.core.generator_engine import generate_dataset
from tyrell.core.models import DatasetRule, DatasetSpec

runner = CliRunner()
EXTREMOS = {-2147483648, 2147483647, 0, -1, 1, 2}


def _spec(include_extremes):
    return DatasetSpec(
        count=6, seed=1, format_template="{v}",
        rules=[DatasetRule(name="v", type="integer", min_val=10, max_val=20, include_extremes=include_extremes)],
    )


def test_include_extremes_false_no_genera_casos_borde():
    valores = {int(tc.input_content) for tc in generate_dataset(_spec(False))}
    assert valores <= set(range(10, 21))


def test_include_extremes_true_conserva_los_casos_borde():
    primeros = [int(tc.input_content) for tc in generate_dataset(_spec(True))[:2]]
    assert all(v in EXTREMOS | {10, 20} for v in primeros)


def test_referencia_inexistente_es_error_y_no_un_out_fantasma(tmp_path):
    res = runner.invoke(app, ["generate", "-n", "2", "-o", str(tmp_path / "t"), "-r", str(tmp_path / "nada")])
    assert res.exit_code == 2
    assert "no existe" in res.output
    assert not list((tmp_path / "t").glob("*.out"))


def test_referencia_que_falla_no_escribe_out_vacio(tmp_path):
    ref = tmp_path / "ref.sh"
    ref.write_text("#!/bin/sh\nsleep 5\n", encoding="utf-8")
    ref.chmod(ref.stat().st_mode | stat.S_IXUSR)
    tcs = generate_dataset(DatasetSpec(count=1), output_dir=tmp_path / "t", reference_binary=ref)
    assert tcs[0].out_filename is None and tcs[0].advertencia
    assert not list((tmp_path / "t").glob("*.out"))
