@echo off
if exist "%~dp0bin\AhsokaAnimations\OctaneCharacterViewer.exe" (
 start "Ahsoka animations" "%~dp0bin\AhsokaAnimations\OctaneCharacterViewer.exe" --ahsoka-trial
) else if exist "%~dp0bin\AhsokaDiagnostic\OctaneCharacterViewer.exe" (
 start "Ahsoka body diagnostic" "%~dp0bin\AhsokaDiagnostic\OctaneCharacterViewer.exe" --ahsoka-trial
) else (
 start "Ahsoka trial" "%~dp0bin\AhsokaTrial\OctaneCharacterViewer.exe" --ahsoka-trial
)
