# Astra FAST LAUNCH - clears port, starts desktop (browser opens once when ready)
# Run: .\go.ps1

$ErrorActionPreference = "SilentlyContinue"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "  ASTRA FAST LAUNCH" -ForegroundColor Cyan
Write-Host ""

# Free port 8501 if old Streamlit still running
& "$PSScriptRoot\stop.ps1" 2>$null | Out-Null
Start-Sleep -Seconds 1

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  Created .env - add ANTHROPIC_API_KEY for Claude" -ForegroundColor Yellow
    }
}

Write-Host "  Starting desktop at http://localhost:8501" -ForegroundColor DarkYellow
Write-Host "  Browser opens once when Streamlit is ready" -ForegroundColor DarkGray
Write-Host "  Portal auto-starts at http://localhost:8503 (trials & pricing)" -ForegroundColor DarkYellow
Write-Host "  Press Ctrl+C to stop (no error - normal shutdown)" -ForegroundColor DarkGray
Write-Host ""

python main.py --desktop
