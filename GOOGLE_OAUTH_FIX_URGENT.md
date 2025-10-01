# СРОЧНОЕ ИСПРАВЛЕНИЕ GOOGLE OAUTH

## Проблема
Ошибка 400 Bad Request при входе через Google OAuth.

## Решение

### 1. Обновите Google Cloud Console

Зайдите в [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials

### 2. Добавьте правильные URI

В разделе "Authorized JavaScript origins" добавьте:
```
http://localhost:5175
http://localhost:8000
```

В разделе "Authorized redirect URIs" добавьте:
```
http://localhost:8000/auth/google/callback/
http://localhost:8000/auth/google/callback
```

### 3. Проверьте .env файл

Убедитесь, что в файле `.env` есть:
```
GOOGLE_CLIENT_ID=ваш-client-id
GOOGLE_CLIENT_SECRET=ваш-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback/
```

### 4. Перезапустите сервер

После изменений перезапустите FastAPI сервер.

## Альтернативное решение

Если проблема продолжается, можно временно использовать старый фронтенд:
1. Откройте http://localhost:8000/static/chat.html
2. Войдите через Google
3. Скопируйте токены из URL
4. Вставьте их в React приложение

## Проверка

После исправления:
1. Откройте http://localhost:5175
2. Нажмите "Войти через Google"
3. Должно перенаправить на Google
4. После входа должно вернуть на React с токенами
