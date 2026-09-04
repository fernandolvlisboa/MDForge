from pathlib import Path
from pypdf import PdfReader
from .base import Converter


class PdfConverter(Converter):
    extensions = (".pdf",)

    def convert(self, source: Path) -> str:
        reader = PdfReader(str(source))
        chunks: list[str] = []
        for index, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            chunks.append(f"## Página {index}\n\n{text if text else '*Sem texto extraível.*'}")
        return "\n\n".join(chunks).strip() + "\n"
