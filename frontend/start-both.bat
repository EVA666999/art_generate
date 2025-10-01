@echo off
echo 🚀 Запуск обоих серверов одновременно...
echo.
echo 🔧 FastAPI: http://localhost:8000
echo 📱 React: http://localhost:5173
echo 🌐 Доступ с других устройств включен!
echo.
echo ⚡ Автоматическая перезагрузка включена для обоих серверов!
echo 💡 Изменения в коде будут применяться мгновенно
echo.
echo Нажмите Ctrl+C для остановки обоих серверов
echo.

cd /d "%~dp0"
npm run dev:both
