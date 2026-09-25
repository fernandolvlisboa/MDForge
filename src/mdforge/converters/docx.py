from pathlib import Path
from typing import TYPE_CHECKING

from docx import Document
from docx.document import Document as _Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from .base import Converter
from .table import table_to_markdown

if TYPE_CHECKING:
    from ..models import ConversionOptions


def _iter_blocks(parent: _Document):
    body = parent.element.body
    for child in body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def _table_to_md(table: Table) -> str:
    rows = [[cell.text for cell in row.cells] for row in table.rows]
    return table_to_markdown(rows, extract_caption=True)


class DocxConverter(Converter):
    extensions = (".docx",)

    def convert(self, source: Path, options: "ConversionOptions | None" = None) -> str:
        doc = Document(str(source))
        out: list[str] = []
        for block in _iter_blocks(doc):
            if isinstance(block, Table):
                table_md = _table_to_md(block)
                if table_md:
                    out.append(table_md)
                continue

            text = block.text.strip()
            if not text:
                continue
            style = (block.style.name or "").lower() if block.style else ""
            if style.startswith("heading"):
                try:
                    level = max(1, min(6, int(style.split()[-1])))
                except ValueError:
                    level = 2
                out.append(f"{'#' * level} {text}")
            elif "list bullet" in style:
                out.append(f"- {text}")
            elif "list number" in style:
                out.append(f"1. {text}")
            else:
                out.append(text)
        return "\n\n".join(out).strip() + "\n"
