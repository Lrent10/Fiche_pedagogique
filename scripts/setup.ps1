$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BundledPython = 'C:\Users\HP\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$BundledNodeDir = 'C:\Users\HP\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin'
$BundledPnpm = 'C:\Users\HP\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd'

Write-Host 'Préparation du Générateur de fiches pédagogiques…' -ForegroundColor Cyan
Set-Location -LiteralPath $ProjectRoot

if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($PythonCommand) { $Python = $PythonCommand.Source }
    elseif (Test-Path -LiteralPath $BundledPython) { $Python = $BundledPython }
    else { throw 'Python 3.11 ou supérieur est requis.' }
    & $Python -m venv .venv
}

& '.\.venv\Scripts\python.exe' -m pip install -r '.\backend\requirements.txt'

$NodeCommand = Get-Command node -ErrorAction SilentlyContinue
if (-not $NodeCommand -and (Test-Path -LiteralPath $BundledNodeDir)) {
    $env:PATH = "$BundledNodeDir;$env:PATH"
}
$PnpmCommand = Get-Command pnpm -ErrorAction SilentlyContinue
if ($PnpmCommand) { $Pnpm = $PnpmCommand.Source }
elseif (Test-Path -LiteralPath $BundledPnpm) { $Pnpm = $BundledPnpm }
else { throw 'Node.js et pnpm sont requis pour l’interface.' }

Push-Location '.\frontend'
try { & $Pnpm install }
finally { Pop-Location }

New-Item -ItemType Directory -Force '.\data', '.\exports', '.\tmp' | Out-Null
Write-Host 'SETUP COMPLETE' -ForegroundColor Green

