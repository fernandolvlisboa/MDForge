from pathlib import Path
from mdforge.models import ConversionOptions
from mdforge.service import ConversionService


def test_txt_to_md(tmp_path: Path):
    source = tmp_path / "hello.txt"
    source.write_text("Olá mundo", encoding="utf-8")
    out = tmp_path / "out"
    result = ConversionService().convert_file(source, out, ConversionOptions(False, False))
    assert result.success
    assert (out / "hello.md").read_text(encoding="utf-8") == "Olá mundo\n"


def test_unsupported_format(tmp_path: Path):
    source = tmp_path / "sample.xyz"
    source.write_text("x", encoding="utf-8")
    result = ConversionService().convert_file(source, tmp_path / "out")
    assert not result.success
