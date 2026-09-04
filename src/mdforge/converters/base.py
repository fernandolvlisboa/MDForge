from abc import ABC, abstractmethod
from pathlib import Path


class Converter(ABC):
    extensions: tuple[str, ...] = ()

    @abstractmethod
    def convert(self, source: Path) -> str:
        """Return Markdown content for *source*."""
        raise NotImplementedError
