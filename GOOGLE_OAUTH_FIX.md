# Обновление Google OAuth настроек для React фронтенда

## Проблема
После входа через Google OAuth пользователь перенаправляется на старый фронтенд `http://localhost:8000/static/chat.html` вместо нового React фронтенда.

## Решение

### 1. Обновлен код (уже сделано)
В файле `app/auth/oauth_routers.py` изменен URL перенаправления:
```python
# Было:
frontend_url = "http://localhost:8000/static/chat.html"

# Стало:
frontend_url = "http://localhost:5175"
```

### 2. Обновить настройки в Google Cloud Console

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Выберите ваш проект
3. Перейдите в "APIs & Services" → "Credentials"
4. Найдите ваш OAuth 2.0 Client ID
5. Нажмите "Edit" (карандаш)
6. В разделе "Authorized redirect URIs" добавьте:
   - `http://localhost:5175`
   - `http://localhost:5175/`
7. Сохраните изменения

### 3. Обновить переменные окружения (если нужно)

Если в `.env` файле есть `GOOGLE_REDIRECT_URI`, убедитесь, что она указывает на правильный callback:
```
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback/
```

### 4. Проверить работу

1. Перезапустите FastAPI сервер
2. Перезапустите React сервер
3. Попробуйте войти через Google OAuth
4. Теперь должно перенаправлять на `http://localhost:5175`

## Примечание
Порт 5175 используется потому, что порты 5173 и 5174 уже заняты (как видно в терминале).
