from pathlib import Path

from .converters import BUILTIN_CONVERTERS
from .converters.base import Converter


class ConverterRegistry:
    def __init__(self, converters: list[Converter] | None = None):
        self._by_extension: dict[str, Converter] = {}
        for converter in converters or BUILTIN_CONVERTERS:
            self.register(converter)

    def register(self, converter: Converter) -> None:
        for ext in converter.extensions:
            self._by_extension[ext.lower()] = converter

    def get(self, source: Path) -> Converter | None:
        return self._by_extension.get(source.suffix.lower())

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_extension))
