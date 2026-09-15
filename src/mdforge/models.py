from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ConversionOptions:
    include_source_header: bool = True
    overwrite: bool = False
    output_name: str | None = None
    sheet_name: str | None = None


@dataclass(slots=True)
class ConversionResult:
    source: Path
    destination: Path | None
    success: bool
    message: str = ""
    warnings: list[str] = field(default_factory=list)
