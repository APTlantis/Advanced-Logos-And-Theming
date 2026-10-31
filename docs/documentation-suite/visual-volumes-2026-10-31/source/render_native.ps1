param([switch]$Templates)
$ErrorActionPreference='Stop'
$collection=Split-Path $PSScriptRoot -Parent
$root=(Resolve-Path (Join-Path $collection '../../..')).Path
$inventory=Get-Content -LiteralPath (Join-Path $collection 'validation/template-inventory.json') -Raw | ConvertFrom-Json
$app=New-Object -ComObject PowerPoint.Application
$receipts=@()
try {
 $app.AutomationSecurity=3
 foreach($item in $inventory) {
  $path=if($Templates){Join-Path $root $item.powerpoint.sample}else{(Get-ChildItem -LiteralPath (Join-Path $collection $item.stem) -Filter '*.pptx').FullName}
  $target=if($Templates){Join-Path $collection ('template-previews/'+$item.stem)}else{Join-Path $collection ($item.stem+'/previews')}
  New-Item -ItemType Directory -Path $target -Force | Out-Null
  $deck=$null
  try {
   $deck=$app.Presentations.Open2007($path,-1,0,0,0)
   $deck.Export($target,'PNG',1280,720)
   if(-not $Templates){$deck.SaveCopyAs([IO.Path]::ChangeExtension($path,'.pdf'),32)}
   $overflow=@()
   for($i=1;$i -le $deck.Slides.Count;$i++) {
    foreach($shape in $deck.Slides.Item($i).Shapes) {
     if($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
      if($shape.TextFrame2.TextRange.BoundHeight -gt ($shape.Height+2)){$overflow+=@{slide=$i;shape=$shape.Name;height=$shape.Height;boundHeight=$shape.TextFrame2.TextRange.BoundHeight}}
     }
    }
   }
   $receipts+=@{stem=$item.stem;file=$path;slides=$deck.Slides.Count;powerpoint=$app.Version;repair=$false;readOnly=$true;rendered=$true;overflow=$overflow;manualEditSaveReopen='not performed'}
   Write-Output ('Rendered '+$item.stem+' ('+$deck.Slides.Count+' slides)')
  } finally {if($null -ne $deck){$deck.Close();[Runtime.InteropServices.Marshal]::ReleaseComObject($deck)|Out-Null}}
 }
} finally {[Runtime.InteropServices.Marshal]::ReleaseComObject($app)|Out-Null}
$name=if($Templates){'template-native.json'}else{'native.json'}
ConvertTo-Json -InputObject @($receipts) -Depth 10 | Set-Content -LiteralPath (Join-Path $collection ('validation/'+$name)) -Encoding utf8
