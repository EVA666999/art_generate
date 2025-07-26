@echo off
chcp 65001 >nul
echo ========================================
echo   Text Generation WebUI Launcher (Fixed)
echo ========================================
echo.

cd /D "%~dp0"

echo 📁 Рабочая директория: %CD%
echo 🤖 Модель: Llama-3.1-128k-Dark-Planet-Uncensored-8B-Q4_k_s.gguf
echo 🔌 API порт: 5000
echo 🌐 Web порт: 7861
echo.

REM Проверяем наличие модели
if not exist "models\main_model\Llama-3.1-128k-Dark-Planet-Uncensored-8B-Q4_k_s.gguf" (
    echo ❌ Ошибка: Модель не найдена!
    echo 📍 Ожидаемый путь: models\main_model\Llama-3.1-128k-Dark-Planet-Uncensored-8B-Q4_k_s.gguf
    pause
    exit /b 1
)

echo ✅ Модель найдена
echo.

echo 🚀 Запускаем text-generation-webui...
echo.

REM Запускаем с API и веб-интерфейсом
python server.py ^
    --api ^
    --api-port 5000 ^
    --listen ^
    --listen-port 7861 ^
    --model Llama-3.1-128k-Dark-Planet-Uncensored-8B-Q4_k_s.gguf ^
    --loader llama.cpp ^
    --model-dir models/main_model ^
    --extensions api ^
    --nowebui

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Ошибка запуска text-generation-webui
    echo 🔍 Проверьте логи выше для деталей
) else (
    echo.
    echo ✅ text-generation-webui завершен успешно
)

pause 