# Start the IAFS Flask API on http://127.0.0.1:5000
$ErrorActionPreference = "Stop"
$backend = Join-Path $PSScriptRoot "backend"

Set-Location $backend

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created backend/.env from .env.example - adjust it if needed." -ForegroundColor Yellow
}

Write-Host "Starting IAFS backend..." -ForegroundColor Cyan
Write-Host "API:    http://127.0.0.1:5000/api" -ForegroundColor Gray
Write-Host "Health: http://127.0.0.1:5000/api/health" -ForegroundColor Gray
python app.py
