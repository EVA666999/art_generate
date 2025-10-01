# 🚀 Инструкции по запуску

## Быстрый старт

### Вариант 1: Запуск обоих серверов одновременно (Рекомендуется)
```bash
# Из корневой папки проекта
./start-dev.bat

# Или из папки frontend
cd frontend
npm run dev:both
```

### Вариант 2: Запуск серверов отдельно

#### FastAPI сервер:
```bash
# Из корневой папки проекта
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Или используйте bat-файл
./start-fastapi.bat
```

#### React фронтенд:
```bash
# Из папки frontend
npm run dev

# Или используйте bat-файл
./frontend/start-react.bat
```

## 📱 Доступ к приложению

После запуска серверов:

- **React фронтенд**: http://localhost:5173
- **FastAPI сервер**: http://localhost:8000
- **API документация**: http://localhost:8000/docs

### Доступ с других устройств в сети:
- **React**: http://0.0.0.0:5173 (замените на IP вашего компьютера)
- **FastAPI**: http://0.0.0.0:8000 (замените на IP вашего компьютера)

## ⚡ Автоматическая перезагрузка

### FastAPI (--reload)
- ✅ Перезапускается при изменении Python файлов
- ✅ Отслеживает изменения в `app/`, `main.py`, и других модулях
- ✅ Сохраняет состояние приложения

### React (Vite HMR)
- ✅ Мгновенная перезагрузка при изменении React компонентов
- ✅ Сохраняет состояние компонентов (Hot Module Replacement)
- ✅ Быстрая перезагрузка CSS и стилей
- ✅ TypeScript проверки в реальном времени

## 🔧 Настройка разработки

### Переменные окружения

Создайте файл `.env.local` в папке `frontend/`:
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=AI Chat
```

### Прокси настройки

React автоматически проксирует запросы к FastAPI:
- `/api/*` → `http://localhost:8000/api/*`
- `/chat` → `http://localhost:8000/chat`
- `/auth/*` → `http://localhost:8000/auth/*`

## 🐛 Отладка

### Проверка работы серверов:
```bash
# Проверка FastAPI
curl http://localhost:8000/docs

# Проверка React
curl http://localhost:5173
```

### Логи:
- **FastAPI**: Логи отображаются в консоли с префиксом `[FastAPI]`
- **React**: Логи отображаются в консоли с префиксом `[React]`
- **Ошибки**: Отображаются в браузере (F12 → Console)

## 📦 Полезные команды

```bash
# Установка зависимостей
cd frontend
npm install

# Сборка для продакшена
npm run build

# Просмотр собранной версии
npm run preview

# Проверка кода
npm run lint
```

## 🔄 Обновление

```bash
# Обновление зависимостей React
cd frontend
npm update

# Обновление зависимостей Python
pip install -r requirements.txt --upgrade
```

## ❓ Частые проблемы

### Ошибка кодировки Unicode (Windows):
```
UnicodeEncodeError: 'charmap' codec can't encode character
```
**Решение**: Эмодзи в логах заменены на обычный текст `[OK]`, `[ERROR]`, `[START]` и т.д.

### Порт уже занят:
```bash
# Изменить порт React
npm run dev -- --port 3000

# Изменить порт FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Проблемы с прокси:
- Убедитесь, что FastAPI запущен на порту 8000
- Проверьте настройки в `vite.config.ts`

### Проблемы с авторизацией:
- Проверьте настройки OAuth в `app/auth/`
- Убедитесь, что токены сохраняются в localStorage

### Ошибка импорта FastAPI:
```
ERROR: Error loading ASGI app. Could not import module "main"
```
**Решение**: Используйте `uvicorn app.main:app` вместо `uvicorn main:app`
