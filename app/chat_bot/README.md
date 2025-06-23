# 🤖 Чат-бот с настраиваемым характером

Чат-бот на базе локальной модели Llama с возможностью создания персонажей с уникальными характерами, стилями речи и предысториями.

## ✨ Возможности

- **Настраиваемые персонажи** - создавайте персонажей с уникальными характерами
- **Локальная модель** - работает с GGUF моделями Llama без интернета
- **Гибкая конфигурация** - настройте параметры генерации под свои нужды
- **Кэширование** - ускорение повторных запросов
- **Фильтрация контента** - опциональная фильтрация нежелательного контента
- **Логирование** - подробные логи для отладки

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Установите llama-cpp-python (для Windows используйте готовый wheel)
pip install llama_cpp_python-0.2.89-cp310-cp310-win_amd64.whl

# Или для Linux/Mac
pip install llama-cpp-python
```

### 2. Настройка модели

Отредактируйте `app/chat_bot/config/chat_config.py`:

```python
MODEL_PATH: str = "путь/к/вашей/модели.gguf"
```

### 3. Простой тест

```bash
python app/chat_bot/test_chat.py
```

### 4. Примеры персонажей

```bash
python app/chat_bot/examples/chat_example.py
```

## 🎭 Создание персонажей

### Структура персонажа

```python
from app.chat_bot.schemas.chat import CharacterConfig

character = CharacterConfig(
    name="Имя персонажа",
    personality="Описание личности и характера",
    background="Предыстория персонажа",
    speaking_style="Стиль речи и манера общения",
    interests=["интерес1", "интерес2"],
    mood="текущее настроение",
    additional_context={}  # Дополнительный контекст
)
```

### Примеры персонажей

#### Дружелюбная Алиса
```python
alice = CharacterConfig(
    name="Алиса",
    personality="Дружелюбная и любознательная девушка, которая любит общаться и помогать людям.",
    background="Алиса - виртуальный помощник, созданный для общения и поддержки пользователей.",
    speaking_style="Говорит дружелюбно и естественно, использует эмодзи и выражает эмоции.",
    interests=["общение", "помощь людям", "технологии", "творчество"],
    mood="веселая и энергичная"
)
```

#### Мудрый профессор
```python
professor = CharacterConfig(
    name="Профессор Иванов",
    personality="Мудрый и опытный преподаватель с глубокими знаниями в различных областях науки.",
    background="Профессор с 30-летним стажем преподавания в университете.",
    speaking_style="Говорит академично, но доступно, любит приводить примеры.",
    interests=["наука", "образование", "исследования", "чтение"],
    mood="спокойный и задумчивый"
)
```

## 🔧 Конфигурация

### Основные параметры

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `MODEL_PATH` | Путь к GGUF модели | - |
| `N_CTX` | Размер контекста | 4096 |
| `N_THREADS` | Количество потоков CPU | 8 |
| `N_BATCH` | Размер батча | 512 |

### Параметры генерации

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `DEFAULT_MAX_TOKENS` | Максимум токенов | 512 |
| `DEFAULT_TEMPERATURE` | Температура (креативность) | 0.8 |
| `DEFAULT_TOP_P` | Top-p параметр | 0.9 |
| `DEFAULT_TOP_K` | Top-k параметр | 40 |
| `DEFAULT_REPEAT_PENALTY` | Штраф за повторения | 1.1 |

## 📡 API использование

### Базовое использование

```python
from app.chat_bot.services.llama_chat_service import llama_chat_service
from app.chat_bot.schemas.chat import ChatMessage, CharacterConfig, MessageRole

# Создаем персонажа
character = CharacterConfig(
    name="Тестовый персонаж",
    personality="Описание личности",
    additional_context={}
)

# Создаем сообщение
messages = [
    ChatMessage(
        role=MessageRole.USER,
        content="Привет!",
        timestamp=None
    )
]

# Генерируем ответ
response, metadata = await llama_chat_service.generate_response(
    messages=messages,
    character_config=character,
    max_tokens=100,
    temperature=0.8
)

print(f"Ответ: {response}")
print(f"Время: {metadata['generation_time']:.2f}с")
```

### Продолжение диалога

```python
# Добавляем ответ ассистента в историю
messages.append(ChatMessage(
    role=MessageRole.ASSISTANT,
    content=response,
    timestamp=None
))

# Добавляем новое сообщение пользователя
messages.append(ChatMessage(
    role=MessageRole.USER,
    content="Расскажи подробнее",
    timestamp=None
))

# Генерируем следующий ответ
response, metadata = await llama_chat_service.generate_response(
    messages=messages,
    character_config=character
)
```

## ⚙️ Настройки производительности

### Кэширование
```python
# Включить/выключить кэширование
ENABLE_CACHE: bool = True

# Размер кэша
MAX_CACHE_SIZE: int = 1000

# Время жизни кэша
CACHE_TTL: int = 3600  # секунды
```

### Логирование
```python
# Логировать запросы
LOG_CHAT_REQUESTS: bool = True

# Логировать ответы
LOG_CHAT_RESPONSES: bool = False
```

### Фильтрация контента
```python
# Включить фильтрацию
ENABLE_CONTENT_FILTER: bool = False

# Запрещенные слова
FORBIDDEN_WORDS: list = ["слово1", "слово2"]
```

## 🔍 Отладка

### Проверка состояния модели
```python
info = llama_chat_service.get_model_info()
print(f"Статус: {info['status']}")
print(f"Путь к модели: {info['model_path']}")
print(f"Размер кэша: {info['cache_size']}")
```

### Логи
Логи сохраняются в `app/logs/` с подробной информацией о:
- Загрузке модели
- Генерации ответов
- Ошибках
- Производительности

## 🐛 Устранение неполадок

### Ошибка загрузки модели
1. Проверьте путь к модели в `chat_config.py`
2. Убедитесь, что файл модели существует
3. Проверьте формат файла (должен быть .gguf)

### Медленная генерация
1. Увеличьте `N_THREADS` для использования большего количества ядер
2. Уменьшите `N_CTX` для экономии памяти
3. Используйте более легкую модель

### Ошибки памяти
1. Уменьшите `N_CTX`
2. Уменьшите `N_BATCH`
3. Используйте модель с меньшим количеством параметров

## 📚 Примеры

Смотрите папку `examples/` для дополнительных примеров:
- `chat_example.py` - примеры разных персонажей
- `test_chat.py` - простой тест

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License

## 🆘 Поддержка

Если у вас возникли проблемы:
1. Проверьте логи в `app/logs/`
2. Убедитесь, что модель загружена корректно
3. Проверьте конфигурацию в `chat_config.py`
4. Создайте Issue с подробным описанием проблемы 