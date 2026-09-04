@echo off
setlocal
py -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .[dev]
pytest
ruff check src tests
pyinstaller --noconfirm --clean --windowed --onefile --name MDForge --collect-all docx --collect-all pptx --collect-all pypdf src\mdforge\gui.py

echo.
echo Build concluido: dist\MDForge.exe
endlocal
