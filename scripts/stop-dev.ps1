$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PidFile = Join-Path $ProjectRoot 'tmp\dev-processes.json'
if (-not (Test-Path -LiteralPath $PidFile)) {
    Write-Host 'Aucun processus de développement enregistré.'
    exit 0
}
$Processes = Get-Content -LiteralPath $PidFile -Raw | ConvertFrom-Json
foreach ($ProcessId in @($Processes.backend_pid, $Processes.frontend_pid)) {
    if ($ProcessId -and (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue)) {
        Stop-Process -Id $ProcessId -Force
    }
}
Remove-Item -LiteralPath $PidFile -Force
Write-Host 'APPLICATION STOPPED' -ForegroundColor Green

