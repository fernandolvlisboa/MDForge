from pathlib import Path
from .models import ConversionOptions, ConversionResult
from .registry import ConverterRegistry


class ConversionService:
    def __init__(self, registry: ConverterRegistry | None = None):
        self.registry = registry or ConverterRegistry()

    def convert_file(self, source: Path, output_dir: Path, options: ConversionOptions | None = None) -> ConversionResult:
        options = options or ConversionOptions()
        source = source.resolve()
        output_dir = output_dir.resolve()
        converter = self.registry.get(source)
        if converter is None:
            return ConversionResult(source, None, False, f"Formato não suportado: {source.suffix}")

        output_dir.mkdir(parents=True, exist_ok=True)
        destination = output_dir / f"{source.stem}.md"
        if destination.exists() and not options.overwrite:
            return ConversionResult(source, destination, False, "Arquivo de destino já existe.")

        try:
            markdown = converter.convert(source).strip() + "\n"
            if options.include_source_header and source.suffix.lower() != ".md":
                markdown = f"<!-- Fonte: {source.name} -->\n\n{markdown}"
            destination.write_text(markdown, encoding="utf-8")
            return ConversionResult(source, destination, True, "Convertido com sucesso.")
        except Exception as exc:
            return ConversionResult(source, destination, False, f"Erro: {exc}")

    def convert_many(self, sources: list[Path], output_dir: Path, options: ConversionOptions | None = None) -> list[ConversionResult]:
        return [self.convert_file(source, output_dir, options) for source in sources]
