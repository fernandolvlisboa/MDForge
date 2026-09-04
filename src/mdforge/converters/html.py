from pathlib import Path

from markdownify import markdownify as to_markdown

from .base import Converter


class HtmlConverter(Converter):
    extensions = (".html", ".htm")

    def convert(self, source: Path) -> str:
        html = source.read_text(encoding="utf-8", errors="replace")
        return to_markdown(html, heading_style="ATX").strip() + "\n"
