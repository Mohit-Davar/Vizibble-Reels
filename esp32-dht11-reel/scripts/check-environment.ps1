# Verifies every tool the pipeline needs. Exit code 1 if anything required is missing.
. "$PSScriptRoot\tools.ps1"
$ErrorActionPreference = 'Continue'
$missing = 0

function Report($name, $value, [switch]$Optional) {
  if ($value) { Write-Host ("  [OK]   {0,-12} {1}" -f $name, $value) }
  elseif ($Optional) { Write-Host ("  [--]   {0,-12} not found (optional)" -f $name) }
  else { Write-Host ("  [MISS] {0,-12} not found" -f $name) -ForegroundColor Red; $script:missing++ }
}

Write-Host 'Environment check' -ForegroundColor Cyan
$node = Get-Command node -ErrorAction SilentlyContinue
Report 'Node.js' $(if ($node) { "$(& node -v)  $($node.Source)" })
Report 'Blender' $(if ($Blender) { "$((& $Blender --version | Select-Object -First 1))  $Blender" })
Report 'FFmpeg' $FFmpeg
Report 'ffprobe' $FFprobe
Report 'Remotion' $(if (Test-Path "$Root\remotion\node_modules\remotion") { 'installed' })
$ard = Get-Command arduino-cli -ErrorAction SilentlyContinue
Report 'arduino-cli' $(if ($ard) { $ard.Source }) -Optional
Report 'narration' $(if (Test-Path "$Root\remotion\public\audio\narration.wav") { 'remotion/public/audio/narration.wav' }) -Optional
Report 'music' $(if (Test-Path "$Root\remotion\public\audio\music.wav") { 'remotion/public/audio/music.wav' }) -Optional

if ($missing -gt 0) { Write-Host "$missing required tool(s) missing" -ForegroundColor Red; exit 1 }
Write-Host 'All required tools present.' -ForegroundColor Green
exit 0
