#!/usr/bin/env powershell
# Build documentation sur Windows
# Usage: .\build.ps1

Write-Host "📚 Building documentation..." -ForegroundColor Cyan

# 1. Installer dépendances
Write-Host "`n1️⃣  Installing dependencies..." -ForegroundColor Blue
pip install -r requirements.txt --quiet
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# 2. Nettoyer
Write-Host "`n2️⃣  Cleaning old builds..." -ForegroundColor Blue
if (Test-Path "_build") {
    Remove-Item _build -Recurse -Force
}
Write-Host "✅ Cleaned" -ForegroundColor Green

# 3. Générer
Write-Host "`n3️⃣  Building HTML..." -ForegroundColor Blue
sphinx-build -b html . _build/html
Write-Host "✅ Build complete" -ForegroundColor Green

# 4. Info
Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host "✨ Documentation ready!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "`n📖 View locally:" -ForegroundColor Yellow
Write-Host "   python -m http.server 8000 -d _build/html" -ForegroundColor White
Write-Host "   Then open: http://localhost:8000" -ForegroundColor White
Write-Host "`n📤 Publish to GitHub:" -ForegroundColor Yellow
Write-Host "   git add ." -ForegroundColor White
Write-Host "   git commit -m docs:_update" -ForegroundColor White
Write-Host "   git push origin main" -ForegroundColor White
Write-Host ""
