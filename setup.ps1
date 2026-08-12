# Astra Platform — Fast Setup
# Run: powershell -ExecutionPolicy Bypass -File setup.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "ASTRA FAST SETUP" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan
Write-Host ""

# Python check
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Install Python 3.10+ first." -ForegroundColor Red
    exit 1
}

Write-Host "[1/5] Installing UI + dev tools..." -ForegroundColor Yellow
python -m pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed. Try: python -m pip install streamlit" -ForegroundColor Red
    exit 1
}

Write-Host "[2/5] Installing Astra voice stack (optional)..." -ForegroundColor Yellow
python -m pip install -q -r requirements-voice.txt 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Voice stack skipped — run: pip install -r requirements-voice.txt" -ForegroundColor DarkYellow
}

# .env setup
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "[3/5] Created .env — add ANTHROPIC_API_KEY + ELEVENLABS_API_KEY" -ForegroundColor Yellow
    } else {
        @"
# Add your OpenAI key here (optional)
OPENAI_API_KEY=
"@ | Out-File -FilePath ".env" -Encoding utf8
        Write-Host "[3/5] Created .env — add API keys" -ForegroundColor Yellow
    }
} else {
    Write-Host "[3/5] .env already exists" -ForegroundColor Green
}

# Data folders
New-Item -ItemType Directory -Force -Path data, logs, plugins | Out-Null
Write-Host "[4/5] Data folders ready" -ForegroundColor Green

# Status check
Write-Host "[5/5] Running status check..." -ForegroundColor Yellow
python main.py --status
$code = $LASTEXITCODE

Write-Host ""
if ($code -eq 0) {
    Write-Host "SETUP COMPLETE" -ForegroundColor Green
    Write-Host ""
    Write-Host "  python astra_hello.py      First win — Claude + voice greet"
    Write-Host "  FAST: .\go.ps1  (auto-opens browser)" -ForegroundColor Green
    Write-Host "  python main.py --desktop  Command OS (8501)"
    Write-Host "  python main.py --portal   Free trial + pricing (8503)"
    Write-Host "  python main.py --mobile   Mobile (8502)"
    Write-Host "  .\astra.ps1               Launcher (PowerShell)"
    Write-Host "  .\astra.bat               Launcher (CMD)"
    Write-Host ""
} else {
    Write-Host "Setup finished with warnings. Try: python main.py --demo" -ForegroundColor Yellow
}

exit $code
