@echo off
cd /d "%~dp0"

py -m PyInstaller --onefile --icon=icon.ico main.py --add-binary "SDL2.dll;."

pause