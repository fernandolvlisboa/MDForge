import argparse
from pathlib import Path

from .models import ConversionOptions
from .service import ConversionService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mdforge", description="Converte documentos para Markdown.")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("markdown-output"))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-source-header", action="store_true")
    parser.add_argument(
        "--name",
        help="Nome do arquivo Markdown de saída (aplica-se apenas a um único arquivo).",
    )
    parser.add_argument(
        "--sheet",
        help="Nome da aba a converter em arquivos Excel (.xlsx/.xlsm). Padrão: todas.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    service = ConversionService()
    options = ConversionOptions(
        include_source_header=not args.no_source_header,
        overwrite=args.overwrite,
        output_name=args.name,
        sheet_name=args.sheet,
    )
    results = service.convert_many(args.files, args.output, options)
    for result in results:
        mark = "OK" if result.success else "ERRO"
        target = f" -> {result.destination}" if result.destination else ""
        print(f"[{mark}] {result.source}{target}: {result.message}")
    return 0 if all(r.success for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
