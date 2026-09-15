from dataclasses import replace
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
        stem = self._resolve_stem(options.output_name, source)
        destination = output_dir / f"{stem}.md"
        if destination.exists() and not options.overwrite:
            return ConversionResult(source, destination, False, "Arquivo de destino já existe.")

        try:
            markdown = converter.convert(source, options).strip() + "\n"
            if options.include_source_header and source.suffix.lower() != ".md":
                markdown = f"<!-- Fonte: {source.name} -->\n\n{markdown}"
            destination.write_text(markdown, encoding="utf-8")
            return ConversionResult(source, destination, True, "Convertido com sucesso.")
        except Exception as exc:
            return ConversionResult(source, destination, False, f"Erro: {exc}")

    def convert_many(self, sources: list[Path], output_dir: Path, options: ConversionOptions | None = None) -> list[ConversionResult]:
        options = options or ConversionOptions()
        # Um nome de saída fixo só faz sentido para um único arquivo; com vários,
        # ele causaria colisão de destino, então é ignorado.
        if options.output_name and len(sources) > 1:
            options = replace(options, output_name=None)
        return [self.convert_file(source, output_dir, options) for source in sources]

    @staticmethod
    def _resolve_stem(output_name: str | None, source: Path) -> str:
        if not output_name:
            return source.stem
        # Aceita nome com ou sem extensão .md e ignora componentes de diretório.
        return Path(output_name.strip()).stem or source.stem
