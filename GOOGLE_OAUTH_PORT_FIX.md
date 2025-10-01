# Исправление проблемы с портом Google OAuth

## Проблема
При входе через Google OAuth происходит перенаправление на `http://localhost:5174` вместо `http://localhost:5175`, что вызывает ошибку.

## Решение

### 1. ✅ Исправлен код (уже сделано)
В файле `app/auth/oauth_routers.py` изменен порт с 5174 на 5175:
```python
# Было:
frontend_url = "http://localhost:5174"

# Стало:
frontend_url = "http://localhost:5175"
```

### 2. 🔧 Нужно исправить в Google Cloud Console

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Выберите ваш проект
3. Перейдите в "APIs & Services" → "Credentials"
4. Найдите ваш OAuth 2.0 Client ID
5. Нажмите "Edit" (карандаш)
6. В разделе "Authorized redirect URIs" убедитесь, что есть:
   - `http://localhost:8000/auth/google/callback/`
7. В разделе "Authorized JavaScript origins" добавьте:
   - `http://localhost:5175`
   - `http://localhost:8000`
8. Сохраните изменения

### 3. 🔄 Перезапустите сервер

После внесения изменений в Google Cloud Console:

1. Остановите FastAPI сервер (Ctrl+C)
2. Запустите заново:
   ```bash
   source venv/Scripts/activate
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 4. ✅ Проверьте работу

1. Откройте http://localhost:5175
2. Нажмите "Войти"
3. Выберите "Войти через Google"
4. После авторизации должно перенаправить на http://localhost:5175 с токенами в URL
5. Страница должна автоматически обработать токены и войти в систему

## Примечание

Если проблема все еще остается, проверьте:
- Правильно ли настроены redirect URIs в Google Cloud Console
- Не кэшируется ли старый redirect URI в браузере
- Работает ли сервер на порту 8000

## Логи для отладки

Проверьте логи сервера при попытке входа через Google OAuth:
```bash
tail -f logs/app.log
```
