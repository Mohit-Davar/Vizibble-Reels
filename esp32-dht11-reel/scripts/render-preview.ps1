# Low-resolution preview: Blender scenes at 50% / low samples, then the full
# Remotion composition at 540x960.
#   .\scripts\render-preview.ps1                 # all 3D scenes + full preview
#   .\scripts\render-preview.ps1 -Scene wiring   # one 3D scene + full preview
#   .\scripts\render-preview.ps1 -SkipBlender    # reuse existing frames
param([string]$Scene = 'all', [switch]$SkipBlender)
. "$PSScriptRoot\tools.ps1"
Set-Location $Root
New-Item -ItemType Directory -Force output\previews, output\logs | Out-Null

if (-not $SkipBlender) {
  if (-not $Blender) { throw 'Blender not found. Run scripts\check-environment.ps1' }
  Invoke-Checked "Blender preview ($Scene)" { & $Blender -b --factory-startup --python-exit-code 1 --python blender/render.py -- --scene $Scene --preview *> output\logs\blender-preview.log }
}
Invoke-Checked 'Sound effects' { node scripts/generate-sfx.mjs }
Sync-Scenes

Push-Location remotion
try {
  Invoke-Checked 'Remotion preview render' { npx.cmd remotion render src/index.ts Reel ..\output\previews\full-preview.mp4 --scale=0.5 --log=error }
} finally { Pop-Location }

Write-Host "Preview: output\previews\full-preview.mp4" -ForegroundColor Green
