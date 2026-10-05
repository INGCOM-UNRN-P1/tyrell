"""Bordes sistemáticos, arreglos casi ordenados, corruptos y estrés (QoL #969, #973–#977)."""

import json

from typer.testing import CliRunner

from tyrell.cli import app
from tyrell.core.generator_engine import INT_MAX, INT_MIN, bordes, generate_dataset
from tyrell.core.models import DatasetRule, DatasetSpec

runner = CliRunner()


def test_bordes_numericos_respetan_los_limites_declarados():
    assert bordes(DatasetRule(name="n", type="integer", min_val=1, max_val=10)) == [1, 10, 2, 9]
    sin_limites = bordes(DatasetRule(name="n", type="integer"))
    assert {INT_MAX, INT_MIN, 0, -1, 1} <= set(sin_limites)


def test_cadenas_vacias_y_con_espacios():
    b = bordes(DatasetRule(name="s", type="string"))
    assert "" in b and " " in b and "a  b" in b and "\t" in b and "a\n\nb" in b


def test_arreglos_vacio_unitario_iguales_y_ordenados():
    b = bordes(DatasetRule(name="v", type="array", min_val=0, max_val=9, length=4))
    assert [] in b and [0] in b and [9, 9, 9, 9] in b and [0, 3, 6, 9] in b and [9, 6, 3, 0] in b


def test_todos_los_bordes_aparecen_y_el_largo_del_arreglo():
    spec = DatasetSpec(count=8, format_template="{v_n}\n{v}\n",
                       rules=[DatasetRule(name="v", type="array", min_val=0, max_val=9, length=4)])
    casos = generate_dataset(spec)
    assert casos[0].input_content == "0\n\n" and casos[0].tipo == "borde"
    assert casos[1].input_content == "1\n0\n"
    assert [c.tipo for c in casos].count("borde") == 5 and casos[-1].tipo == "normal"


def test_casi_ordenado():
    rule = DatasetRule(name="v", type="array", min_val=0, max_val=1000, length=200,
                       orden="casi_ordenado", include_extremes=False)
    (caso,) = generate_dataset(DatasetSpec(count=1, format_template="{v}", rules=[rule]))
    v = [int(x) for x in caso.input_content.split()]
    fuera_de_lugar = sum(1 for a, b in zip(v, v[1:]) if a > b)
    assert v != sorted(v) and 0 < fuera_de_lugar <= 20


def test_corruptos_y_estres(tmp_path):
    spec = DatasetSpec(count=2, corruptos=5, estres_longitud=100_000, format_template="{v_n}\n{v}\n",
                       rules=[DatasetRule(name="v", type="array", min_val=0, max_val=9)])
    casos = generate_dataset(spec, output_dir=tmp_path)
    tipos = [c.tipo for c in casos]
    assert tipos.count("corrupto") == 5 and tipos[-1] == "estres"
    corruptos = [c.input_content for c in casos if c.tipo == "corrupto"]
    assert "" in corruptos and any("\x01" in c for c in corruptos) and any(not c.endswith("\n") for c in corruptos)
    assert casos[-1].input_content.startswith("100000\n")
    assert (tmp_path / f"{len(casos):02d}_suite_estres.in").is_file()


def test_cli_corruptos_y_estres(tmp_path):
    res = runner.invoke(app, ["generate", "-n", "2", "--corruptos", "2", "--estres", "50",
                              "--type", "array", "-o", str(tmp_path), "--json"])
    assert res.exit_code == 0, res.output
    datos = json.loads(res.stdout)
    assert datos["count"] == 5 and [t["tipo"] for t in datos["testcases"]][-1] == "estres"
