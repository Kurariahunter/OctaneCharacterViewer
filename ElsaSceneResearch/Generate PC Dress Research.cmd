@echo off
set "PC_RESEARCH_PYTHON=C:\Users\Kurar\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
"%PC_RESEARCH_PYTHON%" "%~dp0evaluate_pc_dress_anchors.py"
if errorlevel 1 goto failed
"%PC_RESEARCH_PYTHON%" "%~dp0validate_pc_dress_orientation.py"
if errorlevel 1 goto failed
echo PC dress anchor and orientation reports generated. No game process is accessed.
pause
exit /b 0
:failed
echo Generation failed. See the diagnostic above.
pause
exit /b 1
