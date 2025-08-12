@echo off
chcp 65001 >nul
echo ========================================
echo   Text Generation WebUI - MythoMax L2 13B
echo ========================================
echo.

cd /D "%~dp0"

echo Working directory: %CD%
echo Model: Gryphe-MythoMax-L2-13b.Q4_K_S.gguf
echo API port: 5000
echo Web port: 7861
echo GPU: Full model loading (40 layers)
echo.

REM Check if model exists
if not exist "models\main_models\Gryphe-MythoMax-L2-13b.Q4_K_S.gguf" (
    echo ERROR: MythoMax model not found!
    echo Expected path: models\main_models\Gryphe-MythoMax-L2-13b.Q4_K_S.gguf
    pause
    exit /b 1
)

echo MythoMax model found
echo.

echo Starting text-generation-webui with MythoMax L2 13B (Full GPU mode)...
echo.

REM Start with settings from chat_config.py
REM Только параметры, поддерживаемые text-generation-webui
python server.py ^
    --api ^
    --api-port 5000 ^
    --listen ^
    --listen-port 7861 ^
    --model Gryphe-MythoMax-L2-13b.Q4_K_S.gguf ^
    --loader llama.cpp ^
    --model-dir models/main_models ^
    --gpu-layers 40 ^
    --ctx-size 4096 ^
    --batch-size 128 ^
    --threads 16 ^
    --threads-batch 8

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR starting text-generation-webui
    echo Check logs above for details
) else (
    echo.
    echo text-generation-webui finished successfully
)

pause
