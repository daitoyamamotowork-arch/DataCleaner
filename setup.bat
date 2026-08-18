@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo DataCleaner - First-time setup
echo ========================================
echo.

where py >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON=py"
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        set "PYTHON=python"
    ) else (
        echo Python was not found on this PC.
        echo.
        echo Please install Python 3.10 or later, then run setup.bat again.
        echo During installation, enable "Add python.exe to PATH" if that option appears.
        echo.
        pause
        exit /b 1
    )
)

echo [1/3] Checking Python...
%PYTHON% --version
if errorlevel 1 goto :error

echo.
echo [2/3] Creating a private Python environment for DataCleaner...
if not exist ".venv\Scripts\python.exe" (
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :error
) else (
    echo Existing environment found. Reusing it.
)

echo.
echo [3/3] Installing required packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo ========================================
echo Setup completed successfully.
echo Next time, double-click run.bat to start DataCleaner.
echo ========================================
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo Setup failed.
echo Please check the message above and try again.
echo ========================================
echo.
pause
exit /b 1
