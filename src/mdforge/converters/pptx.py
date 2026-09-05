from pathlib import Path
from typing import TYPE_CHECKING

from pptx import Presentation

from .base import Converter

if TYPE_CHECKING:
    from ..models import ConversionOptions


class PptxConverter(Converter):
    extensions = (".pptx",)

    def convert(self, source: Path, options: "ConversionOptions | None" = None) -> str:
        prs = Presentation(str(source))
        out: list[str] = []
        for index, slide in enumerate(prs.slides, start=1):
            out.append(f"## Slide {index}")
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    out.append(shape.text.strip())
            out.append("")
        return "\n\n".join(out).strip() + "\n"
