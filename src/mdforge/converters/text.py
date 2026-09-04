from pathlib import Path

from .base import Converter


class TextConverter(Converter):
    extensions = (".txt", ".md")

    def convert(self, source: Path) -> str:
        return source.read_text(encoding="utf-8", errors="replace")
