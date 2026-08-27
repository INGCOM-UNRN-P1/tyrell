"""Tests unitarios y de integración para TYRELL."""

from pathlib import Path
from typer.testing import CliRunner
from tyrell.cli import app
from tyrell.core.models import DatasetSpec, DatasetRule
from tyrell.core.generator_engine import generate_dataset
from tyrell.plugins.ripley_plugin import TyrellPlugin

runner = CliRunner()


def test_generate_dataset_deterministic(tmp_path):
    spec = DatasetSpec(
        name="test",
        count=5,
        seed=123,
        format_template="{n}\n",
        rules=[DatasetRule(name="n", type="integer", min_val=10, max_val=20)]
    )
    tcs1 = generate_dataset(spec, output_dir=tmp_path / "out1")
    tcs2 = generate_dataset(spec, output_dir=tmp_path / "out2")

    assert len(tcs1) == 5
    assert [t.input_content for t in tcs1] == [t.input_content for t in tcs2]


def test_generate_dataset_with_reference_binary(tmp_path):
    # Compilar un binario simple que suma 1
    src = tmp_path / "echo_bin.c"
    src.write_text("""
    #include <stdio.h>
    int main(void) {
        int x;
        if (scanf("%d", &x) == 1) {
            printf("RESULT:%d\\n", x + 1);
        }
        return 0;
    }
    """)
    bin_path = tmp_path / "echo_bin"
    import subprocess
    subprocess.run(["gcc", str(src), "-o", str(bin_path)], check=True)

    spec = DatasetSpec(
        name="sum",
        count=3,
        seed=42,
        format_template="{n}\n",
        rules=[DatasetRule(name="n", type="integer", min_val=5, max_val=10)]
    )
    tcs = generate_dataset(spec, output_dir=tmp_path / "suite", reference_binary=bin_path)
    assert len(tcs) == 3
    assert all("RESULT:" in tc.output_content for tc in tcs)


def test_cli_generate_json(tmp_path):
    res = runner.invoke(app, ["generate", "-n", "3", "-o", str(tmp_path), "--json"])
    assert res.exit_code == 0
    assert '"count": 3' in res.output


def test_cli_version():
    res = runner.invoke(app, ["version"])
    assert res.exit_code == 0
    assert "TYRELL" in res.output


def test_ripley_plugin(tmp_path):
    plugin = TyrellPlugin()
    res = plugin.run({"testcases_count": 3, "testcases_dir": str(tmp_path / "ripley_tests")})
    assert res["passed"] is True
    assert res["generated_count"] == 3
