# Start the IAFS React development server on http://localhost:5173
$ErrorActionPreference = "Stop"
$frontend = Join-Path $PSScriptRoot "frontend"

Set-Location $frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "Starting IAFS frontend..." -ForegroundColor Cyan
Write-Host "Open http://localhost:5173" -ForegroundColor Gray
npm run dev
