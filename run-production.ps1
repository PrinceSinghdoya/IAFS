# Build the React app and serve everything from Flask on port 5000.
$ErrorActionPreference = "Stop"
$frontend = Join-Path $PSScriptRoot "frontend"
$backend = Join-Path $PSScriptRoot "backend"

Set-Location $frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "Building the React app into backend/static..." -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) {
    throw "Frontend build failed."
}

Set-Location $backend
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created backend/.env from .env.example - adjust it if needed." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "IAFS is available at http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Gray
python app.py
