@echo off
if exist "%~dp0bin\AnkleValidationPreview\OctaneCharacterViewer.exe" (
  start "Octane Character Viewer" "%~dp0bin\AnkleValidationPreview\OctaneCharacterViewer.exe"
) else if exist "%~dp0bin\TurnPreview\OctaneCharacterViewer.exe" (
  start "Octane Character Viewer" "%~dp0bin\TurnPreview\OctaneCharacterViewer.exe"
) else if exist "%~dp0bin\BackwardWalkPreview\OctaneCharacterViewer.exe" (
  start "Octane Character Viewer" "%~dp0bin\BackwardWalkPreview\OctaneCharacterViewer.exe"
) else if exist "%~dp0bin\BackwardPreview\OctaneCharacterViewer.exe" (
  start "Octane Character Viewer" "%~dp0bin\BackwardPreview\OctaneCharacterViewer.exe"
) else if exist "%~dp0bin\FullPalettePreview\OctaneCharacterViewer.exe" (
  start "Octane Character Viewer" "%~dp0bin\FullPalettePreview\OctaneCharacterViewer.exe"
) else if exist "%~dp0bin\CurrentPreview\OctaneCharacterViewer.exe" (
  start "Octane Character Viewer" "%~dp0bin\CurrentPreview\OctaneCharacterViewer.exe"
) else if exist "%~dp0bin\DiagonalPreview\OctaneCharacterViewer.exe" (
  start "Octane Character Viewer" "%~dp0bin\DiagonalPreview\OctaneCharacterViewer.exe"
) else (
  start "Octane Character Viewer" "%~dp0bin\Release\net10.0-windows\OctaneCharacterViewer.exe"
)
