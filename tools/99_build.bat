@echo off
cd /d "%~dp0\.."

echo ============================================
echo  Build Start / ビルド開始
echo ============================================

pyinstaller --noconsole --onefile ^
  --hidden-import=tkinterdnd2 ^
  --collect-all=tkinterdnd2 ^
  src\hash_viewer_gui.py

echo.
echo ============================================
echo  Build Completed! / ビルド完了！
echo  The EXE is in the dist folder. / dist フォルダに EXE が生成されました
echo ============================================
pause
