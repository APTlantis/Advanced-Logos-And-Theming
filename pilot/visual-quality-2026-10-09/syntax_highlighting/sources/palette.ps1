# Illustrative, read-only inventory; displayed rather than executed.
[CmdletBinding()]
param(
    [Parameter()]
    [string] $SourcePath = '.\source',
    [ValidateRange(1, 32)]
    [int] $Limit = 32
)

$ErrorActionPreference = 'Stop'
$labels = @('Observed colors', 'Semantic roles', 'Target tokens')

function Get-SourceSummary {
    param([System.IO.FileInfo] $File)
    [pscustomobject]@{
        Name = $File.Name
        Bytes = $File.Length
        Illustrative = $true
    }
}

try {
    foreach ($label in $labels) {
        Write-Verbose "Review section: $label"
    }
    Get-ChildItem -LiteralPath $SourcePath -File |
        Select-Object -First $Limit |
        ForEach-Object { Get-SourceSummary -File $_ } |
        Format-Table -AutoSize
}
catch {
    Write-Error "Inventory failed: $($_.Exception.Message)"
}
