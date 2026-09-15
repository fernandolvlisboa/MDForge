from pathlib import Path
from typing import TYPE_CHECKING

from markdownify import markdownify as to_markdown

from .base import Converter

if TYPE_CHECKING:
    from ..models import ConversionOptions


class HtmlConverter(Converter):
    extensions = (".html", ".htm")

    def convert(self, source: Path, options: "ConversionOptions | None" = None) -> str:
        html = source.read_text(encoding="utf-8", errors="replace")
        return to_markdown(html, heading_style="ATX").strip() + "\n"
