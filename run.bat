@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Algorithm Visualizer v5.1 - Enhanced
echo ========================================
echo.

cd /d "%~dp0"

REM Check if required files exist
if not exist "main.c" (
    echo ERROR: main.c not found!
    echo Please ensure all files are in the same directory.
    pause
    exit /b 1
)

if not exist "visualize.py" (
    echo ERROR: visualize.py not found!
    echo Please ensure all files are in the same directory.
    pause
    exit /b 1
)

REM Clean up old files
echo Cleaning up previous files...
if exist "algorithm_steps.json" del "algorithm_steps.json"
if exist "algorithm_config.json" del "algorithm_config.json"
if exist "main.exe" del "main.exe"

REM Compile C program
echo.
echo Compiling C program...
gcc -Wall main.c -o main.exe
if errorlevel 1 (
    echo ERROR: Compilation failed! Check if GCC is installed.
    echo Download MinGW-w64 or use a C compiler.
    pause
    exit /b 1
)

if not exist "main.exe" (
    echo ERROR: Executable not created after compilation!
    pause
    exit /b 1
)

REM Run algorithm selection
echo.
echo Running algorithm generator...
echo ==============================
main.exe
if errorlevel 1 (
    echo ERROR: Algorithm execution failed!
    pause
    exit /b 1
)

if not exist "algorithm_steps.json" (
    echo ERROR: No visualization data generated!
    echo Please check your algorithm selection in the program.
    pause
    exit /b 1
)

if not exist "algorithm_config.json" (
    echo ERROR: No configuration file generated!
    pause
    exit /b 1
)

REM Launch visualization
echo.
echo Launching enhanced visualization...
echo ===================================
echo New Features:
echo - Smart Input System
echo - Professional Animations  
echo - Live Analytics Dashboard
echo - Interactive Learning Mode
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.7+ and required packages:
    echo pip install matplotlib numpy
    pause
    exit /b 1
)

REM Install required packages if missing (optional - uncomment if needed)
REM echo Installing required packages...
REM pip install matplotlib numpy --quiet

python visualize.py
if errorlevel 1 (
    echo.
    echo ERROR: Visualization failed!
    echo Please check if all Python packages are installed.
    echo Run: pip install matplotlib numpy
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Visualization completed successfully!
echo ========================================
echo.
pause