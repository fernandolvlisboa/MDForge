from pathlib import Path

from openpyxl import Workbook

from mdforge.converters.xlsx import XlsxConverter
from mdforge.models import ConversionOptions
from mdforge.service import ConversionService


def _make_xlsx(path: Path) -> Path:
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Vendas"
    ws1.append(["Produto", "Total"])
    ws1.append(["Caneta", 10])
    ws2 = wb.create_sheet("Resumo")
    ws2.append(["Item", "Valor"])
    ws2.append(["X", 1])
    wb.save(path)
    return path


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


def test_custom_output_name(tmp_path: Path):
    source = tmp_path / "hello.txt"
    source.write_text("oi", encoding="utf-8")
    out = tmp_path / "out"
    options = ConversionOptions(include_source_header=False, output_name="renomeado.md")
    result = ConversionService().convert_file(source, out, options)
    assert result.success
    assert result.destination == (out / "renomeado.md").resolve()
    assert (out / "renomeado.md").exists()


def test_output_name_ignored_for_multiple_files(tmp_path: Path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("a", encoding="utf-8")
    b.write_text("b", encoding="utf-8")
    out = tmp_path / "out"
    options = ConversionOptions(include_source_header=False, output_name="unico.md")
    results = ConversionService().convert_many([a, b], out, options)
    assert all(r.success for r in results)
    assert (out / "a.md").exists()
    assert (out / "b.md").exists()


def test_xlsx_all_sheets(tmp_path: Path):
    source = _make_xlsx(tmp_path / "planilha.xlsx")
    out = tmp_path / "out"
    result = ConversionService().convert_file(
        source, out, ConversionOptions(include_source_header=False)
    )
    assert result.success
    content = (out / "planilha.md").read_text(encoding="utf-8")
    assert "## Vendas" in content
    assert "## Resumo" in content
    assert "| Produto | Total |" in content


def test_xlsx_single_sheet(tmp_path: Path):
    source = _make_xlsx(tmp_path / "planilha.xlsx")
    out = tmp_path / "out"
    options = ConversionOptions(include_source_header=False, sheet_name="Resumo")
    result = ConversionService().convert_file(source, out, options)
    assert result.success
    content = (out / "planilha.md").read_text(encoding="utf-8")
    assert "## Resumo" in content
    assert "## Vendas" not in content


def test_xlsx_unknown_sheet_fails(tmp_path: Path):
    source = _make_xlsx(tmp_path / "planilha.xlsx")
    out = tmp_path / "out"
    options = ConversionOptions(include_source_header=False, sheet_name="Inexistente")
    result = ConversionService().convert_file(source, out, options)
    assert not result.success
    assert "Inexistente" in result.message


def test_xlsx_sheet_names(tmp_path: Path):
    source = _make_xlsx(tmp_path / "planilha.xlsx")
    assert XlsxConverter().sheet_names(source) == ["Vendas", "Resumo"]
