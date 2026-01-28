@echo off
cd /d "%~dp0"

py -m PyInstaller --onefile --icon=icon.ico renderer.py --add-binary "SDL2.dll;."

pause