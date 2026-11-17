# Open the Flask API and Vite dev server in separate PowerShell windows.
$ErrorActionPreference = "Stop"
$backendScript = Join-Path $PSScriptRoot "start-backend.ps1"
$frontendScript = Join-Path $PSScriptRoot "start-frontend.ps1"

Write-Host "Launching IAFS development servers..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$backendScript`""

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$frontendScript`""

Start-Sleep -Seconds 4
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "Backend:  http://127.0.0.1:5000/api/health" -ForegroundColor Gray
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Gray
Write-Host "Demo admin:   admin@iafs.school / Admin@123" -ForegroundColor Gray
Write-Host "Demo teacher: teacher@iafs.school / Teacher@123" -ForegroundColor Gray
Write-Host "Demo student: aarav@iafs.school / Student@123" -ForegroundColor Gray
