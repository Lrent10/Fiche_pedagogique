$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BundledNodeDir = 'C:\Users\HP\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin'
$BundledPnpm = 'C:\Users\HP\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd'
Set-Location -LiteralPath $ProjectRoot

if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe') -or -not (Test-Path -LiteralPath 'frontend\node_modules')) {
    & "$PSScriptRoot\setup.ps1"
}

New-Item -ItemType Directory -Force '.\data', '.\exports', '.\tmp' | Out-Null
$Occupied = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in 8000, 5173 })
if ($Occupied.Count -gt 0) {
    $Details = ($Occupied | Sort-Object LocalPort | ForEach-Object { "port $($_.LocalPort), PID $($_.OwningProcess)" }) -join '; '
    throw "L'application n'a pas été démarrée : un serveur utilise déjà les ports requis ($Details). Arrêtez l'ancienne session avec .\scripts\stop-dev.ps1, puis relancez."
}
Push-Location '.\backend'
try {
    & '..\.venv\Scripts\python.exe' -m alembic upgrade head
    & '..\.venv\Scripts\python.exe' -m app.seed
}
finally { Pop-Location }

$NodeCommand = Get-Command node -ErrorAction SilentlyContinue
if (-not $NodeCommand -and (Test-Path -LiteralPath $BundledNodeDir)) { $env:PATH = "$BundledNodeDir;$env:PATH" }
$PnpmCommand = Get-Command pnpm -ErrorAction SilentlyContinue
if ($PnpmCommand) { $Pnpm = $PnpmCommand.Source }
elseif (Test-Path -LiteralPath $BundledPnpm) { $Pnpm = $BundledPnpm }
else { throw 'pnpm est introuvable. Lancez scripts\setup.ps1.' }

$Backend = Start-Process -FilePath '.\.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000','--app-dir','backend' -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru
$Frontend = Start-Process -FilePath $Pnpm -ArgumentList 'run','dev' -WorkingDirectory "$ProjectRoot\frontend" -WindowStyle Hidden -PassThru

$Ready = $false
for ($Attempt = 0; $Attempt -lt 30; $Attempt++) {
    try {
        $Response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -UseBasicParsing -TimeoutSec 2
        if ($Response.StatusCode -eq 200) { $Ready = $true; break }
    }
    catch { Start-Sleep -Milliseconds 500 }
}
if (-not $Ready -or $Backend.HasExited -or $Frontend.HasExited) { throw 'Le démarrage a échoué. Arrêtez la session, puis consultez les processus de développement avant de relancer.' }

$FrontendReady = $false
for ($Attempt = 0; $Attempt -lt 30; $Attempt++) {
    try {
        $Response = Invoke-WebRequest -Uri 'http://127.0.0.1:5173/' -UseBasicParsing -TimeoutSec 2
        if ($Response.StatusCode -eq 200) { $FrontendReady = $true; break }
    }
    catch { Start-Sleep -Milliseconds 500 }
}
if (-not $FrontendReady -or $Backend.HasExited -or $Frontend.HasExited) { throw 'Le frontend n’a pas démarré correctement. Arrêtez la session, puis relancez.' }

$BackendListener = Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object -First 1
$FrontendListener = Get-NetTCPConnection -LocalPort 5173 -State Listen | Select-Object -First 1
@{ backend_pid = $BackendListener.OwningProcess; frontend_pid = $FrontendListener.OwningProcess } | ConvertTo-Json | Set-Content -LiteralPath '.\tmp\dev-processes.json' -Encoding UTF8

Write-Host ''
Write-Host 'APPLICATION READY' -ForegroundColor Green
Write-Host 'Frontend:'
Write-Host 'http://127.0.0.1:5173/' -ForegroundColor Cyan
Write-Host 'Backend docs:'
Write-Host 'http://127.0.0.1:8000/docs' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Pour arrêter : powershell -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1'
