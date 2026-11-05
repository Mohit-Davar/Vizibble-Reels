# Full quality: Blender scenes at 1080x1920 / full samples, Remotion at full
# size, FFmpeg loudness pass, then format validation.
#   .\scripts\render-final.ps1 [-SkipBlender]
param([switch]$SkipBlender)
. "$PSScriptRoot\tools.ps1"
Set-Location $Root
New-Item -ItemType Directory -Force output\final, output\logs | Out-Null
if (-not $FFmpeg) { throw 'FFmpeg not found. Run scripts\check-environment.ps1' }

if (-not $SkipBlender) {
  if (-not $Blender) { throw 'Blender not found. Run scripts\check-environment.ps1' }
  Invoke-Checked 'Blender final scenes' { & $Blender -b --factory-startup --python-exit-code 1 --python blender/render.py -- --scene all *> output\logs\blender-final.log }
}
Invoke-Checked 'Sound effects' { node scripts/generate-sfx.mjs }
Sync-Scenes

$master = Join-Path $Root 'output\final\master.mp4'
$final = Join-Path $Root 'output\final\esp32-s3-dht11-reel.mp4'
Push-Location remotion
try {
  # Near-lossless intermediate; FFmpeg makes the delivery encode below.
  Invoke-Checked 'Remotion final render' { npx remotion render src/index.ts Reel $master --crf=8 --log=error }
} finally { Pop-Location }

# Delivery encode:
#   video: H.264 High, limited-range BT.709 yuv420p (what phones and Instagram
#          expect; Remotion's JPEG frames arrive as full-range), CRF 17.
#   audio: loudness-normalised to -14 LUFS, true-peak ceiling -1.5 dBTP
#          (AAC encoding adds a few tenths of a dB), AAC 192k.
Invoke-Checked 'FFmpeg delivery encode' {
  & $FFmpeg -y -loglevel error -i $master `
    -vf 'scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p' `
    -c:v libx264 -preset slow -crf 17 -profile:v high -level 4.2 `
    -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 `
    -af 'loudnorm=I=-14:TP=-1.5:LRA=11' -c:a aac -b:a 192k -ar 48000 `
    -movflags +faststart $final
}
Remove-Item $master -Force -Confirm:$false

Write-Host 'Validating final MP4' -ForegroundColor Cyan
if (-not (Test-Video $final 1080 1920)) { throw 'Validation failed' }
Write-Host "Final: $final" -ForegroundColor Green
