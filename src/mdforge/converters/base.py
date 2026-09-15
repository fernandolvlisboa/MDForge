from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import ConversionOptions


class Converter(ABC):
    extensions: tuple[str, ...] = ()

    @abstractmethod
    def convert(self, source: Path, options: "ConversionOptions | None" = None) -> str:
        """Return Markdown content for *source*."""
        raise NotImplementedError
