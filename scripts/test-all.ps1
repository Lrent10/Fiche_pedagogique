$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BundledNodeDir = 'C:\Users\HP\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin'
$BundledPnpm = 'C:\Users\HP\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd'
Set-Location -LiteralPath $ProjectRoot

Push-Location '.\backend'
try { & '..\.venv\Scripts\python.exe' -m pytest }
finally { Pop-Location }
if ($LASTEXITCODE -ne 0) { throw "Les tests backend ont échoué (code $LASTEXITCODE)." }

if (-not (Get-Command node -ErrorAction SilentlyContinue) -and (Test-Path -LiteralPath $BundledNodeDir)) { $env:PATH = "$BundledNodeDir;$env:PATH" }
$PnpmCommand = Get-Command pnpm -ErrorAction SilentlyContinue
if ($PnpmCommand) { $Pnpm = $PnpmCommand.Source } else { $Pnpm = $BundledPnpm }
Push-Location '.\frontend'
try {
    & $Pnpm run test
    if ($LASTEXITCODE -ne 0) { throw "Les tests frontend ont échoué (code $LASTEXITCODE)." }
    & $Pnpm run build
    if ($LASTEXITCODE -ne 0) { throw "Le build frontend a échoué (code $LASTEXITCODE)." }
}
finally { Pop-Location }
Write-Host 'ALL TESTS PASSED' -ForegroundColor Green
