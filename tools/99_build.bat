@echo off
rem Version: 3.2-dev / Updated: 2026-09-30 / Author: hiro1960
setlocal
cd /d "%~dp0\.."
set "PYTHON_CMD=py -3"
py -3 --version >nul 2>&1
if errorlevel 1 (
  set "PYTHON_CMD=python"
  python --version >nul 2>&1
  if errorlevel 1 goto :no_python
)
if not exist "src\v3.2-dev\hash_viewer_gui_dev.py" goto :no_source
%PYTHON_CMD% -m PyInstaller --version >nul 2>&1
if errorlevel 1 goto :no_pyinstaller
%PYTHON_CMD% -c "import tkinterdnd2" >nul 2>&1
if errorlevel 1 goto :no_dnd
echo Building hash_viewer_gui_dev...
%PYTHON_CMD% -m PyInstaller --noconsole --onefile --name hash_viewer_gui_dev --hidden-import=tkinterdnd2 --collect-all=tkinterdnd2 --distpath "dist\build_v3.2-dev" --workpath "build\v3.2-dev" --specpath "build" "src\v3.2-dev\hash_viewer_gui_dev.py"
if errorlevel 1 goto :build_failed
if not exist "dist\build_v3.2-dev\hash_viewer_gui_dev.exe" goto :build_failed
echo Build completed: dist\build_v3.2-dev\hash_viewer_gui_dev.exe
pause
exit /b 0
:no_python
echo ERROR: Python 3 was not found.
goto :failed
:no_source
echo ERROR: Source file was not found.
goto :failed
:no_pyinstaller
echo ERROR: Install PyInstaller in the selected Python environment.
goto :failed
:no_dnd
echo ERROR: Install tkinterdnd2 in the selected Python environment.
goto :failed
:build_failed
echo ERROR: Build failed.
:failed
pause
exit /b 1
