# MDForge

MDForge é um conversor local de documentos para Markdown, com interface desktop (Tkinter), CLI e arquitetura extensível por conversores.

## Formatos do MVP

| Entrada | Estado | Observação |
|---|---|---|
| `.txt` / `.md` | ✅ | Texto direto |
| `.html` / `.htm` | ✅ | Conversão semântica para Markdown |
| `.docx` | ✅ | Parágrafos, headings, listas e tabelas básicas |
| `.pptx` | ✅ | Texto por slide |
| `.pdf` | ✅ | Extração de texto; não faz OCR |

> PDFs escaneados/imagem não são o foco deste MVP. OCR deve entrar como módulo opcional numa fase posterior.

## Arquitetura

```text
src/mdforge/
├── converters/        # Adaptadores por formato
│   ├── base.py        # Contrato Converter
│   ├── docx.py
│   ├── html.py
│   ├── pdf.py
│   ├── pptx.py
│   └── text.py
├── registry.py        # Descobre conversor pela extensão
├── service.py         # Caso de uso / orquestração
├── models.py          # DTOs e opções
├── cli.py             # Interface de terminal
└── gui.py             # Interface Tkinter
```

A UI não conhece detalhes de DOCX/PDF/etc. Ela chama `ConversionService`, que consulta o `ConverterRegistry`. Para adicionar um novo formato, implemente `Converter` e registre a classe.

## Instalação para desenvolvimento

Recomendado: Python 3.11+.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Rodar a interface

```powershell
mdforge-gui
```

ou:

```powershell
python -m mdforge.gui
```

## CLI

```powershell
mdforge relatorio.docx apresentacao.pptx -o .\saida
mdforge arquivo.pdf -o .\saida --overwrite
```

## Testes e lint

```powershell
pytest
ruff check src tests
```

## Gerar o `.exe` no Windows

Use Windows para gerar um executável Windows. O PyInstaller não é um cross-compiler genérico: o build deve ser feito no sistema operacional alvo.

```powershell
.\scripts\build_windows.ps1
```

Ou:

```bat
scripts\build_windows.bat
```

Ao final:

```text
dist\MDForge.exe
```

O build está configurado como `--onefile --windowed`, portanto o usuário final recebe um único `.exe` e não abre uma janela de console.

## Decisões do MVP

- **Tkinter:** vem com Python e reduz dependências/complexidade do empacotamento.
- **Core desacoplado da UI:** permite futuramente trocar Tkinter por PySide6, web UI ou outra camada sem reescrever conversores.
- **Conversores independentes:** facilita testes e novos formatos.
- **Markdown UTF-8:** saída previsível e amigável para LLMs, Git e editores.
- **Sem OCR inicialmente:** evita inflar o executável e introduzir dependências nativas antes de validar o produto.

## Roadmap sugerido

1. Drag & drop e remoção individual de arquivos.
2. Preview do Markdown antes de salvar.
3. Conversão recursiva de pastas.
4. Preservação melhor de hyperlinks/imagens em DOCX/PPTX.
5. OCR opcional para PDF escaneado.
6. Barra de progresso e conversão em worker thread.
7. Preferências persistentes.
8. Ícone, version info, instalador MSI/Inno Setup e assinatura de código.

## Limitações conhecidas

Conversão de documentos é heurística. Layouts complexos, caixas de texto, colunas, SmartArt, fórmulas, imagens e PDFs com posicionamento sofisticado podem perder estrutura. O objetivo deste MVP é gerar Markdown limpo e útil, não reproduzir fielmente o layout visual do arquivo original.
