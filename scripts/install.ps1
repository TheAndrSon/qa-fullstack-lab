$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path '.venv')) {
    Write-Host 'Creating virtual environment...'
    python -m venv .venv
}

Write-Host 'Installing dependencies...'
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host 'Installing Playwright Chromium (optional, for UI tests)...'
.\.venv\Scripts\python.exe -m playwright install chromium

Write-Host 'Done. Run scripts\run_shopsphere.ps1'
