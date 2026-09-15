from pathlib import Path
from typing import TYPE_CHECKING

from .base import Converter

if TYPE_CHECKING:
    from ..models import ConversionOptions


class TextConverter(Converter):
    extensions = (".txt", ".md")

    def convert(self, source: Path, options: "ConversionOptions | None" = None) -> str:
        return source.read_text(encoding="utf-8", errors="replace")
