@echo off
set "PC_READER_PYTHON=C:\Users\Kurar\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
"%PC_READER_PYTHON%" "%~dp0read_pc_idle_files.py"
if errorlevel 1 goto failed
echo Generated pc-file-idle-channels.json from installed-PC files. No running game needed.
pause
exit /b 0
:failed
echo Reader failed. See the diagnostic above.
pause
exit /b 1
