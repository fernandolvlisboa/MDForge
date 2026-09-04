$ErrorActionPreference = "Stop"

py -m venv .venv

& .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -e ".[dev]"

pytest

ruff check src tests

pyinstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onefile `
    --name MDForge `
    --paths src `
    --collect-all docx `
    --collect-all pptx `
    --collect-all pypdf `
    launcher_gui.py

Write-Host "Build concluído: dist\MDForge.exe"
