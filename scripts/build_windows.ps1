$ErrorActionPreference = "Stop"

py -m venv .venv

& .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -e ".[dev]"

pytest

ruff check src tests

pyinstaller --noconfirm --clean MDForge.spec

Write-Host "Build concluído: dist\MDForge.exe"
