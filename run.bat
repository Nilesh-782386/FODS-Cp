@echo off
setlocal enabledelayedexpansion

REM Algorithm Visualizer v5.1 - Runner Script
echo ==================================================================
echo     ALGORITHM VISUALIZER v5.1
echo ==================================================================
echo.
echo New Features in v5.1:
echo • Enhanced Input Validation
echo • Memory Leak Fixes
echo • Better Error Messages
echo • Improved BST Layout Algorithm
echo • Smooth Animations & Transitions
echo • Algorithm Comparison Mode
echo.

REM Change to the correct directory
cd /d "%~dp0"

REM Check if required files exist
if not exist "main.c" (
    echo ERROR: main.c not found!
    pause
    exit /b 1
)

if not exist "visualize.py" (
    echo ERROR: visualize.py not found!
    pause
    exit /b 1
)

REM Clean up old files
if exist "algorithm_steps.json" del "algorithm_steps.json"
if exist "algorithm_config.json" del "algorithm_config.json"
if exist "main.exe" del "main.exe"

echo Compiling C program...
gcc main.c -o main.exe

REM Check if compilation was successful
if not exist "main.exe" (
    echo ERROR: Compilation failed! Check GCC installation.
    pause
    exit /b 1
)

echo Compilation successful!
echo Running algorithm selection...
main.exe

REM Check if execution was successful
if not exist "algorithm_steps.json" (
    echo ERROR: Program execution failed!
    pause
    exit /b 1
)

echo Algorithm data generated successfully!
echo Launching visualization...


REM Check for Python and required libraries
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Python not found! Install Python 3.x
    pause
    exit /b 1
)

REM Check and install required Python packages
python -c "import matplotlib, numpy" >nul 2>&1
if !errorlevel! neq 0 (
    echo Installing required packages...
    pip install matplotlib numpy
    if !errorlevel! neq 0 (
        echo ERROR: Failed to install packages!
        pause
        exit /b 1
    )
)

python visualize.py

echo.
echo Visualization completed!
pause
in this have a some extra message are come  that is not imp you can remove only usefull take