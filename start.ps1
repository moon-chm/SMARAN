<#
.SYNOPSIS
Single command startup script for SMARAN on Windows (PowerShell)
#>

$ErrorActionPreference = "Stop"

# Define colors
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"

Write-Host "🚀 Starting SMARAN Initialization Pipeline...`n" -ForegroundColor $Green

# Verify .env exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ ERROR: .env file missing in the root directory!" -ForegroundColor $Red
    Write-Host "Please copy .env.example to .env and configure the required keys."
    exit 1
}

# Function to check required .env keys
function Check-EnvKey {
    param([string]$Key)
    $envContent = Get-Content ".env"
    $found = $envContent | Select-String -Pattern "^$Key="
    if (-not $found) {
        Write-Host "❌ ERROR: Required configuration key '$Key' not found in .env!" -ForegroundColor $Red
        exit 1
    }
}

Write-Host "1. Checking environment keys..."
Check-EnvKey "NEO4J_URI"
Check-EnvKey "NEO4J_USER"
Check-EnvKey "NEO4J_PASSWORD"
Check-EnvKey "GROQ_API_KEY"
Check-EnvKey "JWT_SECRET"
Write-Host "✅ .env Configuration OK`n" -ForegroundColor $Green

# Check if port 8000 is occupied
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "⚠️ WARNING: Port 8000 is already in use. Please stop the existing process before continuing." -ForegroundColor $Yellow
    exit 1
}

$env:PYTHONPATH = $PWD.Path

# Step 1: Initialize Neo4j Graph
Write-Host "Step 1: Initializing Neo4j Schema (Constraints & Indices)..."
python app\graph\init_graph.py
Write-Host "✅ Graph Initialized`n" -ForegroundColor $Green

# Step 2: Boot FastAPI layer for Seeding
Write-Host "Step 2: Booting FastAPI layer for Seeding..."
$apiProcess = Start-Process -FilePath "uvicorn" -ArgumentList "app.main:app","--host","0.0.0.0","--port","8000" -PassThru -NoNewWindow

# Wait for API to come online
Write-Host "Waiting for API to hit Health check bounds..."
$apiReady = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Head -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $apiReady = $true
            break
        }
    } catch {}
    Write-Host -NoNewline "."
    Start-Sleep -Seconds 2
}

if (-not $apiReady) {
    Write-Host "`n❌ ERROR: FastAPI failed to start within the expected time." -ForegroundColor $Red
    Stop-Process -Id $apiProcess.Id -Force
    exit 1
}
Write-Host "`n✅ FastAPI Online`n" -ForegroundColor $Green

# Step 3: Run Seed
Write-Host "Step 3: Seeding Graph Demo Data..."
python scripts\seed_demo.py
Write-Host "✅ Seed Completed`n" -ForegroundColor $Green

# Step 4 & 5: Start Streamlit Dashboards
Write-Host "Step 4 & 5: Starting Streamlit Panels..."
$cgProcess = Start-Process -FilePath "streamlit" -ArgumentList "run","frontend\caregiver_panel.py","--server.port","8501","--server.headless","true" -PassThru -NoNewWindow
$elderProcess = Start-Process -FilePath "streamlit" -ArgumentList "run","frontend\elder_panel.py","--server.port","8502","--server.headless","true" -PassThru -NoNewWindow

Write-Host "`n================================================" -ForegroundColor $Green
Write-Host "🌟 SMARAN SYSTEM IS LIVE 🌟" -ForegroundColor $Green
Write-Host "================================================" -ForegroundColor $Green
Write-Host "📖 FastAPI Docs:        http://localhost:8000/docs"
Write-Host "🩺 Health Check:        http://localhost:8000/health"
Write-Host "🏥 Caregiver Panel:     http://localhost:8501"
Write-Host "💖 Elder Panel:         http://localhost:8502"
Write-Host "🔑 Credentials:         caregiver_demo / password123"
Write-Host "                        elder_123 / password123"
Write-Host "================================================`n" -ForegroundColor $Green
Write-Host "Press Ctrl+C to stop all services..."

# Clean up processes on exit
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "`nShutting down SMARAN..." -ForegroundColor $Yellow
    if ($apiProcess) { Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue }
    if ($cgProcess) { Stop-Process -Id $cgProcess.Id -Force -ErrorAction SilentlyContinue }
    if ($elderProcess) { Stop-Process -Id $elderProcess.Id -Force -ErrorAction SilentlyContinue }
}
