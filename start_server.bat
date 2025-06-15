@echo off
echo Starting Automata Visualization Server...

REM Check if Graphviz is installed and in PATH
where dot >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Graphviz 'dot' executable not found in PATH.
    echo Please install Graphviz from https://graphviz.org/download/
    echo During installation, make sure to select the option to add Graphviz to your system PATH.
    echo.
    echo After installation, restart your terminal and try again.
    pause
    exit /b 1
)

echo Graphviz found. Starting server...
python server.py
