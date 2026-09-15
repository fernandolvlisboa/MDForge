@echo off
setlocal
py -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .[dev]
pytest
ruff check src tests
pyinstaller --noconfirm --clean MDForge.spec

echo.
echo Build concluido: dist\MDForge.exe
endlocal
