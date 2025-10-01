@echo off
echo 🚀 Запуск FastAPI сервера...
echo.
echo 🔧 FastAPI будет доступен по адресу: http://localhost:8000
echo 🌐 Доступ с других устройств: http://0.0.0.0:8000
echo.
echo ⚡ Автоматическая перезагрузка включена!
echo 💡 Изменения в Python файлах будут применяться мгновенно
echo.
echo Нажмите Ctrl+C для остановки
echo.

cd /d "%~dp0\.."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
