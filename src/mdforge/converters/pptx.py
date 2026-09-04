from pathlib import Path

from pptx import Presentation

from .base import Converter


class PptxConverter(Converter):
    extensions = (".pptx",)

    def convert(self, source: Path) -> str:
        prs = Presentation(str(source))
        out: list[str] = []
        for index, slide in enumerate(prs.slides, start=1):
            out.append(f"## Slide {index}")
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    out.append(shape.text.strip())
            out.append("")
        return "\n\n".join(out).strip() + "\n"
