@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo DataCleaner has not been set up yet.
    echo Starting the first-time setup now...
    echo.
    call setup.bat
    if errorlevel 1 exit /b 1
)

echo Starting DataCleaner...
".venv\Scripts\python.exe" -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo DataCleaner stopped because an error occurred.
    pause
)
