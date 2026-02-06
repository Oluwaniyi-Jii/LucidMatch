$ErrorActionPreference = "Stop"

Write-Host "Starting LucidMatch..." -ForegroundColor Cyan

# Check if we are in the root directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Error "Please run this script from the project root directory."
    exit 1
}

# Start Backend
Write-Host "Launching Backend (FastAPI)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {
    cd backend
    if (-not (Test-Path '.env')) {
        Write-Warning '.env file not found in backend!'
    }
    Write-Host 'Starting Uvicorn...' -ForegroundColor Cyan
    uvicorn main:app --reload
}"

# Start Frontend
Write-Host "Launching Frontend (Vite)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {
    cd frontend
    Write-Host 'Starting Vite...' -ForegroundColor Cyan
    npm run dev
}"

Write-Host "Both services launched!" -ForegroundColor Cyan
