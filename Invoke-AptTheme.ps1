[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ThemeArguments)
$ErrorActionPreference = 'Stop'
$pipelinePython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pipelinePython)) { throw 'Run Setup.ps1 first.' }
& $pipelinePython -m apt_theme @ThemeArguments
exit $LASTEXITCODE
