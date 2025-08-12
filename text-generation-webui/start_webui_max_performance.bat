@echo off
chcp 65001 >nul
echo ========================================
echo   Text Generation WebUI - MAX PERFORMANCE
echo ========================================
echo.

cd /D "%~dp0"

REM Read model name from server.py and remove .gguf extension
for /f "tokens=3 delims= " %%i in ('findstr /C:"MODEL_NAME = " server.py') do set MODEL_NAME=%%i
set MODEL_NAME=%MODEL_NAME:"=%
set MODEL_NAME=%MODEL_NAME:.gguf=%

echo Working directory: %CD%
echo Model: %MODEL_NAME%
echo.
echo API port: 5000
echo Web port: 7861
echo GPU: MAXIMUM PERFORMANCE MODE
echo.

REM Check if model exists
if not exist "models\main_models\%MODEL_NAME%.gguf" (
    echo ERROR: Model %MODEL_NAME%.gguf not found!
    echo Expected path: models\main_models\%MODEL_NAME%.gguf
    echo.
    echo Available models in models/main_models/ folder:
    dir /b "models\main_models\*.gguf" 2>nul
    dir /b "models\main_models\*.safetensors" 2>nul
    echo.
    echo Trying to find model in other locations...
    dir /b "models\*.gguf" 2>nul
    echo.
    pause
    exit /b 1
)

echo Model %MODEL_NAME%.gguf found
echo.

echo Starting text-generation-webui in MAXIMUM PERFORMANCE mode...
echo WARNING: This mode prioritizes speed over context length!
echo.

REM Start with MAXIMUM PERFORMANCE configuration
python server.py --api --api-port 5000 --listen --listen-port 7861 --model "%MODEL_NAME%.gguf" --model-dir "models\main_models" --loader llama.cpp --gpu-layers 40 --ctx-size 4096 --threads 16 --threads-batch 8 --batch-size 128 --streaming

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR starting text-generation-webui
    echo Check logs above for details
) else (
    echo.
    echo text-generation-webui started in MAXIMUM PERFORMANCE mode!
)

pause
