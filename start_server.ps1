# PowerShell script to start the Automata Visualization Server
Write-Host "Starting Automata Visualization Server..." -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.x" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Graphviz is installed and in PATH
try {
    $dotVersion = dot -V
    Write-Host "Found Graphviz: $dotVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Graphviz 'dot' executable not found in PATH." -ForegroundColor Red
    Write-Host "Please install Graphviz from: https://graphviz.org/download/" -ForegroundColor Yellow
    Write-Host "During installation, make sure to select the option to add Graphviz to your system PATH." -ForegroundColor Yellow
    Write-Host "After installation, restart your terminal and try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required Python packages are installed
try {
    $graphvizPackage = python -c "import graphviz; print(f'Found graphviz package version {graphviz.__version__}')"
    Write-Host $graphvizPackage -ForegroundColor Green
} catch {
    Write-Host "Installing required Python packages..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
}

# Start the server
try {
    Write-Host "Starting server..." -ForegroundColor Cyan
    python server.py
} catch {
    Write-Host "ERROR: Failed to start server: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
