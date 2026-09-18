"""Regresión de TYRELL-D0301/D0302/D0501: un YAML mal formado no puede degradarse en silencio."""

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from tyrell.cli import app
from tyrell.core.models import DatasetRule, DatasetSpec

runner = CliRunner()


def _yaml(tmp_path, texto):
    ruta = tmp_path / "spec.yaml"
    ruta.write_text(texto, encoding="utf-8")
    return ruta


def test_spec_inexistente_es_un_error_y_no_un_dataset_por_defecto(tmp_path):
    res = runner.invoke(app, ["generate", str(tmp_path / "no_existe.yaml"), "-o", str(tmp_path / "out")])
    assert res.exit_code == 2
    assert not (tmp_path / "out").exists()


def test_un_tipo_desconocido_se_rechaza():
    with pytest.raises(ValidationError):
        DatasetRule(name="v", type="intger")


def test_una_clave_desconocida_se_rechaza():
    with pytest.raises(ValidationError):
        DatasetRule(name="v", type="integer", max_value=9)


def test_plantilla_sin_placeholders_se_rechaza():
    with pytest.raises(ValidationError, match="ningún placeholder"):
        DatasetSpec(format_template="%d %d", rules=[DatasetRule(name="a", type="integer")])


def test_placeholder_sin_regla_se_rechaza():
    with pytest.raises(ValidationError, match="sin regla"):
        DatasetSpec(format_template="{a} {b}", rules=[DatasetRule(name="a", type="integer")])


def test_regla_sin_usar_se_rechaza():
    with pytest.raises(ValidationError, match="no aparecen"):
        DatasetSpec(
            format_template="{a}",
            rules=[DatasetRule(name="a", type="integer"), DatasetRule(name="b", type="integer")],
        )


def test_spec_valida_genera_los_casos_del_yaml(tmp_path):
    spec = _yaml(
        tmp_path,
        'count: 2\nseed: 7\nformat_template: "{v}\\n"\nrules: [{name: v, type: integer, min_val: 1, max_val: 9}]\n',
    )
    res = runner.invoke(app, ["generate", str(spec), "-o", str(tmp_path / "out"), "--json"])
    assert res.exit_code == 0, res.output
    assert len(list((tmp_path / "out").glob("*.in"))) == 2


def test_las_opciones_de_cli_ignoradas_se_avisan(tmp_path):
    spec = _yaml(
        tmp_path,
        'count: 2\nformat_template: "{v}\\n"\nrules: [{name: v, type: integer}]\n',
    )
    res = runner.invoke(app, ["generate", str(spec), "-n", "99", "-o", str(tmp_path / "out")])
    assert res.exit_code == 0
    assert "--count" in res.output
    assert len(list((tmp_path / "out").glob("*.in"))) == 2


def test_sin_opciones_extra_no_hay_aviso(tmp_path):
    spec = _yaml(tmp_path, 'count: 2\nformat_template: "{v}\\n"\nrules: [{name: v, type: integer}]\n')
    res = runner.invoke(app, ["generate", str(spec), "-o", str(tmp_path / "out")])
    assert "Aviso" not in res.output
