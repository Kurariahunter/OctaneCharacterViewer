@echo off
if exist "%~dp0bin\WiiULocomotion\OctaneCharacterViewer.exe" (
 start "Wii U Elsa motions" "%~dp0bin\WiiULocomotion\OctaneCharacterViewer.exe" --wiiu-adapter --wiiu-model
) else if exist "%~dp0bin\WiiUIdleExpansion\OctaneCharacterViewer.exe" (
 start "Wii U Elsa idle pack" "%~dp0bin\WiiUIdleExpansion\OctaneCharacterViewer.exe" --wiiu-adapter --wiiu-model
) else if exist "%~dp0bin\WiiUFullPalette\OctaneCharacterViewer.exe" (
 start "Wii U source mesh and full palette animation" "%~dp0bin\WiiUFullPalette\OctaneCharacterViewer.exe" --wiiu-adapter --wiiu-model
) else if exist "%~dp0bin\WiiUDressAdapter\OctaneCharacterViewer.exe" (
 start "Wii U source mesh and dress animation" "%~dp0bin\WiiUDressAdapter\OctaneCharacterViewer.exe" --wiiu-adapter --wiiu-model
) else if exist "%~dp0bin\WiiUNativeMeshAdapter\OctaneCharacterViewer.exe" (
 start "Wii U source mesh and animation" "%~dp0bin\WiiUNativeMeshAdapter\OctaneCharacterViewer.exe" --wiiu-adapter --wiiu-model
) else if exist "%~dp0bin\WiiULegAdapter\OctaneCharacterViewer.exe" (
 start "Wii U controls on PC reference rig" "%~dp0bin\WiiULegAdapter\OctaneCharacterViewer.exe" --wiiu-adapter
) else if exist "%~dp0bin\WiiUAdapterContinuous\OctaneCharacterViewer.exe" (
 start "Wii U controls on PC reference rig" "%~dp0bin\WiiUAdapterContinuous\OctaneCharacterViewer.exe" --wiiu-adapter
) else (
 start "Wii U controls on PC reference rig" "%~dp0bin\WiiUAdapterPreview\OctaneCharacterViewer.exe" --wiiu-adapter
)
