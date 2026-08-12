# Astra v3.2 Launcher — run: .\astra.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "  ==============================" -ForegroundColor DarkYellow
    Write-Host "    A S T R A   v3.4  LAUNCHER" -ForegroundColor Cyan
    Write-Host "  ==============================" -ForegroundColor DarkYellow
    Write-Host ""
    Write-Host "  1.  Command OS Desktop   http://localhost:8501"
    Write-Host "  2.  Mobile Companion    http://localhost:8502"
    Write-Host "  3.  Portal + Free Trial http://localhost:8503"
    Write-Host "  4.  Terminal REPL"
    Write-Host "  5.  Voice Mode"
    Write-Host "  6.  Wake Word (Alexa-style)"
    Write-Host "  7.  API Server"
    Write-Host "  8.  Status Check"
    Write-Host "  9.  Run Tests"
    Write-Host "  10. Setup"
    Write-Host "  0.  Exit"
    Write-Host ""
}

while ($true) {
    Show-Menu
    $choice = Read-Host "Choose"

    switch ($choice) {
        "1" { python main.py --desktop; Read-Host "Press Enter to return to menu" }
        "2" { python main.py --mobile; Read-Host "Press Enter to return to menu" }
        "3" { python main.py --portal; Read-Host "Press Enter to return to menu" }
        "4" { python main.py; Read-Host "Press Enter to return to menu" }
        "5" { python main.py --voice; Read-Host "Press Enter to return to menu" }
        "6" { python main.py --wake; Read-Host "Press Enter to return to menu" }
        "7" { python main.py --serve; Read-Host "Press Enter to return to menu" }
        "8" { python main.py --status; Read-Host "Press Enter to return to menu" }
        "9" { python -m pytest tests/ -q; Read-Host "Press Enter to return to menu" }
        "10" { powershell -ExecutionPolicy Bypass -File setup.ps1; Read-Host "Press Enter to return to menu" }
        "0" { exit 0 }
        default { Write-Host "Invalid choice" -ForegroundColor Red; Start-Sleep -Seconds 1 }
    }
}
