@echo off
echo 🚀 Запуск React фронтенда...
echo.
echo 📱 React будет доступен по адресу: http://localhost:5173
echo 🌐 Доступ с других устройств: http://0.0.0.0:5173
echo.
echo ⚡ Автоматическая перезагрузка включена!
echo 💡 Изменения в коде будут применяться мгновенно
echo.
echo Нажмите Ctrl+C для остановки
echo.

cd /d "%~dp0"
npm run dev
