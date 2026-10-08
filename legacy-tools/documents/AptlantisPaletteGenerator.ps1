<#
.SYNOPSIS
    Build a 32-color UI-oriented palette from an image.

.DESCRIPTION
    1. Uses ImageMagick to obtain a larger representative candidate palette.
    2. Converts candidates from sRGB to OKLab / OKLCH.
    3. Selects 32 colors with deliberate lightness, chroma, and hue diversity.
    4. Outputs:
        palette.txt
        palette.css
        palette.toml (language.template.toml-compatible structure)
        palette.png

.EXAMPLE
    .\New-AptlantisPalette.ps1 `
        -InputImage "C:\Path\apt-julia-logo.png" `
        -OutputDir "C:\Path\apt-julia-palette"

.EXAMPLE
    .\New-AptlantisPalette.ps1 `
        -InputImage "C:\Path\apt-julia-logo.png" `
        -OutputDir "C:\Path\apt-julia-palette" `
        -Language "Julia" `
        -Inspiration "Julia language" `
        -Notes "Derived from Aptlantis Julia crest"

.EXAMPLE
    .\New-AptlantisPalette.ps1 `
        -InputImage "C:\Path\apt-julia-logo.png" `
        -OutputDir "C:\Path\apt-julia-palette" `
        -UseWorkingTiff
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$InputImage,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir,

    [int]$CandidateColors = 192,

    [int]$FinalColors = 32,

    [int]$ResizeMax = 768,

    [switch]$UseWorkingTiff,

    [string]$ThemeId,

    [string]$ThemeName,

    [string]$Language,

    [string]$Inspiration,

    [string]$Notes,

    [string]$Family = "Aptlantis",

    [ValidateSet("dark", "light")]
    [string]$Variant = "dark",

    [string]$CssPrefix
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

if (-not (Get-Command magick -ErrorAction SilentlyContinue)) {
    throw "ImageMagick 'magick' was not found in PATH."
}

if (-not (Test-Path -LiteralPath $InputImage)) {
    throw "Input image not found: $InputImage"
}

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

$WorkDir = Join-Path $OutputDir "_work"
New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null


# ------------------------------------------------------------
# Color conversion
# ------------------------------------------------------------

function Convert-SrgbByteToLinear {
    param(
        [double]$Value
    )

    $v = $Value / 255.0

    if ($v -le 0.04045) {
        return ($v / 12.92)
    }

    return [math]::Pow(
        (($v + 0.055) / 1.055),
        2.4
    )
}


function Convert-RgbToOklch {
    param(
        [int]$R,
        [int]$G,
        [int]$B
    )

    $rLin = Convert-SrgbByteToLinear $R
    $gLin = Convert-SrgbByteToLinear $G
    $bLin = Convert-SrgbByteToLinear $B

    $l = (
        0.4122214708 * $rLin +
        0.5363325363 * $gLin +
        0.0514459929 * $bLin
    )

    $m = (
        0.2119034982 * $rLin +
        0.6806995451 * $gLin +
        0.1073969566 * $bLin
    )

    $s = (
        0.0883024619 * $rLin +
        0.2817188376 * $gLin +
        0.6299787005 * $bLin
    )

    # Values here should normally be >= 0 for sRGB.
    # Keep the sign-safe cube root anyway.
    function CubeRoot([double]$x) {
        if ($x -eq 0) {
            return 0.0
        }

        return (
            [math]::Sign($x) *
            [math]::Pow([math]::Abs($x), (1.0 / 3.0))
        )
    }

    $lRoot = CubeRoot $l
    $mRoot = CubeRoot $m
    $sRoot = CubeRoot $s

    $L = (
        0.2104542553 * $lRoot +
        0.7936177850 * $mRoot -
        0.0040720468 * $sRoot
    )

    $A = (
        1.9779984951 * $lRoot -
        2.4285922050 * $mRoot +
        0.4505937099 * $sRoot
    )

    $Bok = (
        0.0259040371 * $lRoot +
        0.7827717662 * $mRoot -
        0.8086757660 * $sRoot
    )

    $C = [math]::Sqrt(
        ($A * $A) +
        ($Bok * $Bok)
    )

    $H = (
        [math]::Atan2($Bok, $A) *
        180.0 /
        [math]::PI
    )

    if ($H -lt 0) {
        $H += 360.0
    }

    return [pscustomobject]@{
        L = [double]$L
        C = [double]$C
        H = [double]$H
        A = [double]$A
        B = [double]$Bok
    }
}


function Get-OklabDistance {
    param(
        $Color1,
        $Color2
    )

    $dL = $Color1.L - $Color2.L
    $dA = $Color1.A - $Color2.A
    $dB = $Color1.Bok - $Color2.Bok

    return [math]::Sqrt(
        ($dL * $dL) +
        ($dA * $dA) +
        ($dB * $dB)
    )
}


# ------------------------------------------------------------
# Selection scoring
# ------------------------------------------------------------

function Get-PreferenceScore {
    param(
        $Color,
        [string]$Mode
    )

    $L = [double]$Color.L
    $C = [double]$Color.C

    switch ($Mode) {

        "dark" {
            return (
                ((1.0 - $L) * 3.0) +
                ((0.12 - [math]::Min($C, 0.12)) * 3.0)
            )
        }

        "surface" {
            return (
                ((1.0 - [math]::Abs($L - 0.42)) * 2.0) +
                ((0.12 - [math]::Abs($C - 0.07)) * 2.0)
            )
        }

        "light" {
            return (
                ($L * 3.0) +
                ((0.12 - [math]::Min($C, 0.12)) * 2.0)
            )
        }

        "accent" {
            return (
                ($C * 5.0) +
                (1.0 - [math]::Abs($L - 0.60))
            )
        }

        "vivid" {
            return (
                ($C * 7.0) +
                (1.0 - [math]::Abs($L - 0.62))
            )
        }

        "neutral" {
            return (
                ((0.10 - [math]::Min($C, 0.10)) * 5.0) +
                (1.0 - [math]::Abs($L - 0.58))
            )
        }

        "data" {
            return (
                ($C * 4.0) +
                (1.0 - [math]::Abs($L - 0.58))
            )
        }

        default {
            return 0.0
        }
    }
}


function Select-DiverseColors {
    param(
        $Colors,
        [int]$Count,
        [string]$Mode,
        $AlreadySelected = @()
    )

    $remaining = @($Colors)
    $picked = @()
    $existing = @($AlreadySelected)

    if ($remaining.Count -eq 0) {
        return @()
    }

    while (
        ($picked.Count -lt $Count) -and
        ($remaining.Count -gt 0)
    ) {

        $best = $null
        $bestScore = [double]::NegativeInfinity

        foreach ($candidate in $remaining) {

            $frequencyScore = [math]::Log(
                [double]$candidate.Count + 1.0
            )

            $preferenceScore = Get-PreferenceScore `
                -Color $candidate `
                -Mode $Mode

            $comparison = @($existing + $picked)

            if ($comparison.Count -eq 0) {
                $diversityScore = 0.15
            }
            else {
                $distances = @(
                    foreach ($other in $comparison) {
                        Get-OklabDistance `
                            -Color1 $candidate `
                            -Color2 $other
                    }
                )

                $diversityScore = (
                    $distances |
                    Measure-Object -Minimum
                ).Minimum
            }

            $score = (
                $frequencyScore +
                ($preferenceScore * 2.0) +
                ($diversityScore * 12.0)
            )

            if ($score -gt $bestScore) {
                $bestScore = $score
                $best = $candidate
            }
        }

        if ($null -eq $best) {
            break
        }

        $picked += $best

        $remaining = @(
            $remaining |
            Where-Object {
                $_.Hex -ne $best.Hex
            }
        )
    }

    return @($picked)
}


# ------------------------------------------------------------
# Working image
# ------------------------------------------------------------

Write-Host "Preparing working image..." -ForegroundColor Cyan

$WorkingImage = $InputImage

if ($UseWorkingTiff) {

    $WorkingImage = Join-Path $WorkDir "working-16bit.tif"

    & magick `
        $InputImage `
        -alpha off `
        -strip `
        -colorspace sRGB `
        -depth 16 `
        $WorkingImage

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create 16-bit TIFF working image."
    }
}


# ------------------------------------------------------------
# Candidate extraction
# ------------------------------------------------------------

Write-Host "Extracting candidate colors..." -ForegroundColor Cyan

$HistogramArgs = @(
    $WorkingImage,
    '-alpha', 'off',
    '-strip',
    '-resize', ("{0}x{0}>" -f $ResizeMax),
    '+dither',
    '-colors', $CandidateColors,
    '-colorspace', 'sRGB',
    '-depth', '8',
    '-format', '%c',
    'histogram:info:-'
)

$HistogramText = @(
    & magick @HistogramArgs
)

if ($LASTEXITCODE -ne 0) {
    throw "ImageMagick histogram extraction failed."
}


$CandidateMap = @{}

foreach ($line in $HistogramText) {

    if (
        $line -match
        '^\s*(\d+):\s*\((\d+),(\d+),(\d+)\)\s*#([0-9A-Fa-f]{6})'
    ) {

        $count = [int]$matches[1]
        $r = [int]$matches[2]
        $g = [int]$matches[3]
        $b = [int]$matches[4]
        $hex = "#" + $matches[5].ToUpper()

        if ($CandidateMap.ContainsKey($hex)) {

            $CandidateMap[$hex].Count += $count
        }
        else {

            $ok = Convert-RgbToOklch `
                -R $r `
                -G $g `
                -B $b

            $CandidateMap[$hex] = [pscustomobject]@{
                Hex   = $hex
                R     = $r
                G     = $g
                Blue  = $b
                Count = $count

                L     = $ok.L
                C     = $ok.C
                H     = $ok.H

                A     = $ok.A
                Bok   = $ok.B
            }
        }
    }
}


$AllColors = @(
    $CandidateMap.Values |
    Sort-Object Count -Descending
)

Write-Host (
    "Parsed {0} candidate colors." -f $AllColors.Count
) -ForegroundColor Green


if ($AllColors.Count -lt $FinalColors) {
    throw (
        "Only found {0} candidate colors; need at least {1}." -f
        $AllColors.Count,
        $FinalColors
    )
}


# ------------------------------------------------------------
# Helper for each palette role
# ------------------------------------------------------------

$Selected = @()


function Add-PaletteGroup {

    param(
        [string]$Name,
        [int]$Count,
        [string]$Mode,
        [scriptblock]$Filter
    )

    $unused = @(
        $script:AllColors |
        Where-Object {
            $hex = $_.Hex

            -not (
                $script:Selected |
                Where-Object Hex -eq $hex
            )
        }
    )


    $filtered = @(
        $unused |
        Where-Object $Filter
    )


    # Empty filtered pools are completely valid.
    # Fall back to all unused candidates.
    if ($filtered.Count -eq 0) {

        Write-Host (
            "  {0}: preferred pool empty; using general candidates." -f
            $Name
        ) -ForegroundColor DarkYellow

        $filtered = @($unused)
    }


    if ($filtered.Count -lt $Count) {

        $extra = @(
            $unused |
            Where-Object {
                $filtered.Hex -notcontains $_.Hex
            }
        )

        $filtered = @(
            $filtered + $extra
        )
    }


    $picked = @(
        Select-DiverseColors `
            -Colors $filtered `
            -Count $Count `
            -Mode $Mode `
            -AlreadySelected $script:Selected
    )


    foreach ($color in $picked) {

        $script:Selected += [pscustomobject]@{
            Group = $Name

            Hex   = $color.Hex
            R     = $color.R
            G     = $color.G
            Blue  = $color.Blue
            Count = $color.Count

            L     = $color.L
            C     = $color.C
            H     = $color.H

            A     = $color.A
            Bok   = $color.Bok
        }
    }
}


$script:AllColors = $AllColors
$script:Selected = @()


# ------------------------------------------------------------
# Final 32-color composition
# ------------------------------------------------------------

Write-Host "Selecting final 32-color palette..." -ForegroundColor Cyan


Add-PaletteGroup `
    -Name "structural-dark" `
    -Count 4 `
    -Mode "dark" `
    -Filter {
        $_.L -le 0.32
    }


Add-PaletteGroup `
    -Name "structural-mid" `
    -Count 4 `
    -Mode "surface" `
    -Filter {
        $_.L -gt 0.25 -and
        $_.L -lt 0.62
    }


Add-PaletteGroup `
    -Name "text-light" `
    -Count 5 `
    -Mode "light" `
    -Filter {
        $_.L -ge 0.72
    }


Add-PaletteGroup `
    -Name "accent" `
    -Count 5 `
    -Mode "accent" `
    -Filter {
        $_.C -ge 0.08 -and
        $_.L -gt 0.32 -and
        $_.L -lt 0.82
    }


Add-PaletteGroup `
    -Name "accent-strong" `
    -Count 4 `
    -Mode "vivid" `
    -Filter {
        $_.C -ge 0.15
    }


Add-PaletteGroup `
    -Name "neutral" `
    -Count 4 `
    -Mode "neutral" `
    -Filter {
        $_.C -le 0.08 -and
        $_.L -gt 0.35
    }


Add-PaletteGroup `
    -Name "data" `
    -Count 6 `
    -Mode "data" `
    -Filter {
        $_.C -ge 0.05
    }


$FinalPalette = @(
    $script:Selected |
    Select-Object -First $FinalColors
)


if ($FinalPalette.Count -ne $FinalColors) {
    throw (
        "Final palette contains {0} colors instead of {1}." -f
        $FinalPalette.Count,
        $FinalColors
    )
}


# ------------------------------------------------------------
# Naming
# ------------------------------------------------------------

$Counters = @{}

$NamedPalette = @(
    foreach ($color in $FinalPalette) {

        if (-not $Counters.ContainsKey($color.Group)) {
            $Counters[$color.Group] = 0
        }

        $Counters[$color.Group]++

        $safeGroup = $color.Group -replace '-', '_'

        [pscustomobject]@{
            Name = (
                "{0}_{1:D2}" -f
                $safeGroup,
                $Counters[$color.Group]
            )

            Role = $color.Group

            Hex = $color.Hex

            R = $color.R
            G = $color.G
            B = $color.Blue

            L = $color.L
            C = $color.C
            H = $color.H

            Count = $color.Count
        }
    }
)


# ------------------------------------------------------------
# Output helpers
# ------------------------------------------------------------

function Get-OklchString {
    param($Color)

    return (
        "oklch({0:N2}% {1:N4} {2:N1})" -f
        ($Color.L * 100.0),
        $Color.C,
        $Color.H
    )
}


function ConvertTo-TomlBasicString {
    param(
        [AllowEmptyString()]
        [string]$Value
    )

    if ($null -eq $Value) {
        return ""
    }

    $escaped = $Value.Replace('\', '\\')
    $escaped = $escaped.Replace('"', '\"')
    $escaped = $escaped.Replace("`r", '\r')
    $escaped = $escaped.Replace("`n", '\n')
    $escaped = $escaped.Replace("`t", '\t')

    return $escaped
}


function ConvertTo-ThemeSlug {
    param(
        [string]$Value
    )

    $slug = $Value.ToLowerInvariant() -replace '[^a-z0-9]+', '-'
    return $slug.Trim('-')
}


$TxtPath  = Join-Path $OutputDir "palette.txt"
$CssPath  = Join-Path $OutputDir "palette.css"
$TomlPath = Join-Path $OutputDir "palette.toml"
$PngPath  = Join-Path $OutputDir "palette.png"


# ------------------------------------------------------------
# TXT
# ------------------------------------------------------------

Write-Host "Writing palette.txt..." -ForegroundColor Cyan

$TxtOutput = @()

$TxtOutput += (
    "name`trole`thex`trgb`toklch`tcount"
)

foreach ($c in $NamedPalette) {

    $TxtOutput += (
        "{0}`t{1}`t{2}`trgb({3},{4},{5})`t{6}`t{7}" -f
        $c.Name,
        $c.Role,
        $c.Hex,
        $c.R,
        $c.G,
        $c.B,
        (Get-OklchString $c),
        $c.Count
    )
}

Set-Content `
    -LiteralPath $TxtPath `
    -Value $TxtOutput `
    -Encoding UTF8


# ------------------------------------------------------------
# CSS
# ------------------------------------------------------------

Write-Host "Writing palette.css..." -ForegroundColor Cyan

$CssOutput = @()
$CssOutput += ":root {"

foreach ($c in $NamedPalette) {

    $CssName = $c.Name -replace '_', '-'

    $CssOutput += (
        "  --{0}: {1};" -f
        $CssName,
        $c.Hex
    )

    $CssOutput += (
        "  --{0}-oklch: {1};" -f
        $CssName,
        (Get-OklchString $c)
    )
}

$CssOutput += "}"

Set-Content `
    -LiteralPath $CssPath `
    -Value $CssOutput `
    -Encoding UTF8


# ------------------------------------------------------------
# TOML
# ------------------------------------------------------------

Write-Host "Writing palette.toml..." -ForegroundColor Cyan

$ImageStem = [System.IO.Path]::GetFileNameWithoutExtension($InputImage)
$InferredLanguage = $ImageStem `
    -replace '(?i)^apt(?:lantis)?[-_ ]*', '' `
    -replace '(?i)[-_ ]*(?:crest|emblem|logo|palette)$', '' `
    -replace '[-_]+', ' '

if ([string]::IsNullOrWhiteSpace($InferredLanguage)) {
    $InferredLanguage = $ImageStem
}

if ([string]::IsNullOrWhiteSpace($Language)) {
    $Language = (Get-Culture).TextInfo.ToTitleCase(
        $InferredLanguage.ToLowerInvariant()
    )
}

$LanguageSlug = ConvertTo-ThemeSlug $Language

if ([string]::IsNullOrWhiteSpace($ThemeId)) {
    $ThemeId = "aptlantis-$LanguageSlug"
}

if ([string]::IsNullOrWhiteSpace($ThemeName)) {
    $ThemeName = "Aptlantis $Language"
}

if ([string]::IsNullOrWhiteSpace($Inspiration)) {
    $Inspiration = $Language
}

if ([string]::IsNullOrWhiteSpace($Notes)) {
    $Notes = "Derived from Aptlantis $Language crest"
}

if ([string]::IsNullOrWhiteSpace($CssPrefix)) {
    $CssPrefix = "--apt-$LanguageSlug"
}

$TomlSourceImage = ConvertTo-TomlBasicString (
    $InputImage -replace '\\', '/'
)
$TomlThemeId = ConvertTo-TomlBasicString $ThemeId
$TomlThemeName = ConvertTo-TomlBasicString $ThemeName
$TomlFamily = ConvertTo-TomlBasicString $Family
$TomlVariant = ConvertTo-TomlBasicString $Variant
$TomlLanguage = ConvertTo-TomlBasicString $Language
$TomlInspiration = ConvertTo-TomlBasicString $Inspiration
$TomlNotes = ConvertTo-TomlBasicString $Notes
$TomlCssPrefix = ConvertTo-TomlBasicString $CssPrefix

$TomlOutput = @()

$TomlOutput += "[theme]"
$TomlOutput += ('id = "{0}"' -f $TomlThemeId)
$TomlOutput += ('name = "{0}"' -f $TomlThemeName)
$TomlOutput += ('family = "{0}"' -f $TomlFamily)
$TomlOutput += ('variant = "{0}"' -f $TomlVariant)
$TomlOutput += ('source_image = "{0}"' -f $TomlSourceImage)
$TomlOutput += ('generated_at = "{0}"' -f ([DateTimeOffset]::Now.ToString("o")))
$TomlOutput += ("candidate_colors = {0}" -f $CandidateColors)
$TomlOutput += ("final_colors = {0}" -f $FinalColors)
$TomlOutput += ""
$TomlOutput += "[source]"
$TomlOutput += ('language = "{0}"' -f $TomlLanguage)
$TomlOutput += ('inspiration = "{0}"' -f $TomlInspiration)
$TomlOutput += ('notes = "{0}"' -f $TomlNotes)
$TomlOutput += ""


foreach (
    $group in (
        $NamedPalette |
        Select-Object -ExpandProperty Role -Unique
    )
) {

    $TomlGroup = $group -replace '-', '_'

    $TomlOutput += (
        "[palette.{0}]" -f
        $TomlGroup
    )

    foreach (
        $c in (
            $NamedPalette |
            Where-Object Role -eq $group
        )
    ) {

        $TomlOutput += (
            '{0} = {{ hex = "{1}", rgb = [{2}, {3}, {4}], oklch = {{ l = {5:N6}, c = {6:N6}, h = {7:N3} }} }}' -f
            $c.Name,
            $c.Hex,
            $c.R,
            $c.G,
            $c.B,
            $c.L,
            $c.C,
            $c.H
        )
    }

    $TomlOutput += ""
}

$TomlOutput += @(
    "[roles.base]",
    'app_bg = "structural_dark_02"',
    'panel_bg = "structural_dark_01"',
    'editor_bg = "structural_dark_04"',
    'elevated_bg = "structural_mid_04"',
    'border_subtle = "neutral_03"',
    'border_strong = "structural_mid_03"',
    "",
    "[roles.text]",
    'fg_primary = "text_light_01"',
    'fg_secondary = "text_light_02"',
    'fg_muted = "neutral_01"',
    'fg_accent = "text_light_03"',
    'fg_warm = "text_light_04"',
    "",
    "[roles.accent]",
    'primary = "accent_05"',
    'secondary = "accent_01"',
    'success = "accent_03"',
    'warning = "accent_02"',
    'highlight = "data_03"',
    "",
    "[roles.syntax]",
    'keyword = "accent_01"',
    'type = "data_03"',
    'function = "text_light_03"',
    'string = "text_light_04"',
    'number = "data_05"',
    'comment = "neutral_02"',
    'constant = "data_06"',
    'operator = "text_light_02"',
    'error = "accent_strong_03"',
    "",
    "[roles.terminal]",
    'black = "structural_dark_02"',
    'red = "accent_01"',
    'green = "accent_03"',
    'yellow = "data_05"',
    'blue = "data_04"',
    'magenta = "accent_04"',
    'cyan = "data_03"',
    'white = "text_light_05"',
    "",
    "[targets.jetbrains]",
    ('ui_theme = "{0}"' -f $TomlThemeName),
    ('editor_scheme = "{0}"' -f $TomlThemeName),
    "",
    "[targets.alacritty]",
    ('flavor = "{0}"' -f $TomlVariant),
    "",
    "[targets.windows_terminal]",
    ('scheme_name = "{0}"' -f $TomlThemeName),
    "",
    "[targets.siyuan]",
    ('css_prefix = "{0}"' -f $TomlCssPrefix),
    "",
    "[validation]",
    "minimum_contrast_body = 4.5",
    "minimum_contrast_ui = 3.0",
    "apca_preferred = true"
)


Set-Content `
    -LiteralPath $TomlPath `
    -Value $TomlOutput `
    -Encoding UTF8


# ------------------------------------------------------------
# PNG swatch sheet
# ------------------------------------------------------------

Write-Host "Writing palette.png..." -ForegroundColor Cyan

$SwatchDir = Join-Path $WorkDir "swatches"

New-Item `
    -ItemType Directory `
    -Path $SwatchDir `
    -Force |
    Out-Null


$index = 0

foreach ($c in $NamedPalette) {

    $index++

    $SwatchPath = Join-Path `
        $SwatchDir `
        ("{0:D2}.png" -f $index)


    if ($c.L -ge 0.62) {
        $TextColor = "#101214"
    }
    else {
        $TextColor = "#F4F6F8"
    }


    $Label = @"
$($c.Name)
$($c.Hex)
OKLCH $([math]::Round($c.L * 100, 1))% $([math]::Round($c.C, 4)) $([math]::Round($c.H, 1))
"@


    & magick `
        -size 320x160 `
        "xc:$($c.Hex)" `
        -fill $TextColor `
        -gravity NorthWest `
        -pointsize 18 `
        -annotate +12+12 $Label `
        $SwatchPath


    if ($LASTEXITCODE -ne 0) {
        throw "Failed creating swatch $index."
    }
}


$SwatchFiles = @(
    Get-ChildItem `
        -LiteralPath $SwatchDir `
        -Filter "*.png" |
    Sort-Object Name |
    ForEach-Object FullName
)


$MontageArgs = @()

$MontageArgs += $SwatchFiles

$MontageArgs += @(
    '-tile', '4x8',
    '-geometry', '+8+8',
    '-background', '#101318',
    $PngPath
)

& magick montage @MontageArgs

if ($LASTEXITCODE -ne 0) {
    throw "Failed creating palette montage."
}


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host ""

Write-Host "Generated:" -ForegroundColor Green
Write-Host "  $TxtPath"
Write-Host "  $CssPath"
Write-Host "  $TomlPath"
Write-Host "  $PngPath"

if ($UseWorkingTiff) {
    Write-Host "  $WorkingImage"
}

Write-Host ""
Write-Host "Palette groups:" -ForegroundColor Cyan

$NamedPalette |
    Group-Object Role |
    ForEach-Object {
        Write-Host (
            "  {0,-18} {1,2}" -f
            $_.Name,
            $_.Count
        )
    }
