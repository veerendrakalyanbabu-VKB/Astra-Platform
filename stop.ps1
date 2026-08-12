# Stop Astra / Streamlit on default ports
# Run: .\stop.ps1

$ports = @(8501, 8502, 8503)

foreach ($port in $ports) {
    $lines = netstat -ano | Select-String ":$port\s"
    foreach ($line in $lines) {
        if ($line -match '\s(\d+)\s*$') {
            $procId = $Matches[1]
            if ($procId -match '^\d+$' -and [int]$procId -gt 0) {
                Write-Host "Stopping PID $procId on port $port" -ForegroundColor Yellow
                taskkill /PID $procId /F 2>$null | Out-Null
            }
        }
    }
}

Write-Host "Ports cleared. Run .\go.ps1 to start." -ForegroundColor Green
