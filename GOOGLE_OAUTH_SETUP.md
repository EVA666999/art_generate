# Настройка Google OAuth

## 1. Создание проекта в Google Cloud Console

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google+ API

## 2. Настройка OAuth 2.0

1. Перейдите в "APIs & Services" → "Credentials"
2. Нажмите "Create Credentials" → "OAuth 2.0 Client IDs"
3. Выберите "Web application"
4. Добавьте авторизованные URI перенаправления:
   - `http://localhost:8000/auth/google/callback/`
   - `http://127.0.0.1:8000/auth/google/callback/`

## 3. Настройка переменных окружения

Добавьте в файл `.env`:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback/
```

## 4. Тестирование

1. Запустите сервер: `uvicorn app.main:app --reload`
2. Откройте http://localhost:8000/static/chat.html
3. Нажмите "Войти через Google"
4. Авторизуйтесь в Google
5. Вы будете перенаправлены обратно в приложение

## 5. Для продакшена

Обновите `GOOGLE_REDIRECT_URI` на ваш домен:
```env
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/google/callback/
```

И добавьте этот URI в Google Cloud Console.
