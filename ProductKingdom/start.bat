@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE="

where python >nul 2>nul
if not errorlevel 1 (
  for /f "delims=" %%i in ('where python') do (
    if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
  )
)

if not defined PYTHON_EXE (
  where py >nul 2>nul
  if not errorlevel 1 set "PYTHON_EXE=py"
)

if not defined PYTHON_EXE (
  if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    set "PYTHON_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
  )
)

if not defined PYTHON_EXE (
  echo [ProductKingdom] Python was not found.
  echo Please install Python 3.11+ and enable "Add python.exe to PATH".
  echo Download: https://www.python.org/downloads/
  pause
  exit /b 1
)

echo [ProductKingdom] Python: %PYTHON_EXE%

if not exist ".venv\Scripts\python.exe" (
  echo [ProductKingdom] Creating virtual environment...
  "%PYTHON_EXE%" -m venv .venv
  if errorlevel 1 (
    echo [ProductKingdom] Failed to create virtual environment.
    pause
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [ProductKingdom] Failed to activate virtual environment.
  pause
  exit /b 1
)

echo [ProductKingdom] Installing dependencies...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
if errorlevel 1 (
  echo [ProductKingdom] Failed to upgrade pip.
  pause
  exit /b 1
)

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
if errorlevel 1 (
  echo [ProductKingdom] Failed to install dependencies.
  echo Try closing proxy/VPN, then run this file again.
  pause
  exit /b 1
)

python -c "import flask, langgraph, langchain_openai"
if errorlevel 1 (
  echo [ProductKingdom] Dependency check failed. Delete .venv and run start.bat again.
  pause
  exit /b 1
)

echo [ProductKingdom] Starting web app...
echo [ProductKingdom] Open: http://127.0.0.1:7860
start "" "http://127.0.0.1:7860"

echo [ProductKingdom] Opening LangSmith dashboard...
start "" "https://smith.langchain.com"
python web_app.py

pause
