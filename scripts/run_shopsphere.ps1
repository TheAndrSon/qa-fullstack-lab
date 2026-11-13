$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path '.venv')) {
    Write-Host 'No .venv yet. Running install first...'
    & (Join-Path $PSScriptRoot 'install.ps1')
}

Write-Host 'Starting ShopSphere on http://127.0.0.1:8000 ...'
.\.venv\Scripts\python.exe -m uvicorn apps.shopsphere.main:app --reload --port 8000
