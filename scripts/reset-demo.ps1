$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath (Split-Path -Parent $PSScriptRoot)).Path
$DatabasePath = (Join-Path $ProjectRoot 'data\app.db')
$ExportPath = (Join-Path $ProjectRoot 'exports')
if (-not $DatabasePath.StartsWith($ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Cible de base invalide.' }
if (-not $ExportPath.StartsWith($ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Cible d’export invalide.' }

& "$PSScriptRoot\stop-dev.ps1"
if (Test-Path -LiteralPath $DatabasePath) { Remove-Item -LiteralPath $DatabasePath -Force }
if (Test-Path -LiteralPath $ExportPath) {
    Get-ChildItem -LiteralPath $ExportPath -File | Where-Object { $_.Extension -in '.pdf', '.log' } | Remove-Item -Force
}
Push-Location (Join-Path $ProjectRoot 'backend')
try {
    & '..\.venv\Scripts\python.exe' -m alembic upgrade head
    & '..\.venv\Scripts\python.exe' -m app.seed
}
finally { Pop-Location }
Write-Host 'DEMO RESET COMPLETE' -ForegroundColor Green

