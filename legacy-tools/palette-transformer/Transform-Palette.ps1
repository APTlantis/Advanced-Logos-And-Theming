[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$InputPalette,
    [string]$OutputDirectory = '.\profiles',
    [ValidateSet('all','terminal','notepad','sublime','siyuan','jetbrains','website','powerpoint','desktop')][string]$Profile = 'all',
    [int]$Count = 0,
    [string]$Python = 'python',
    [switch]$Strict
)
$arguments = @((Join-Path $PSScriptRoot 'palette_transformer.py'), $InputPalette, '--output', $OutputDirectory, '--profile', $Profile)
if ($Count -gt 0) { $arguments += @('--count', "$Count") }
if ($Strict) { $arguments += '--strict' }
& $Python @arguments
if ($LASTEXITCODE -ne 0) { throw "Palette transformer exited with code $LASTEXITCODE. Inspect validation reports if code is 2." }
