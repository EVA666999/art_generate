# React Frontend для AI Chat

Современный React фронтенд для чата с AI персонажами, выполненный в темной теме с фиолетово-черными градиентами и пурпурными акцентами.

## 🎨 Дизайн

- **Темная тема** с фиолетово-черными градиентами
- **Пурпурные акценты** для интерактивных элементов
- **Синие подтоны** для глубины
- **Современный UI** с плавными анимациями
- **Адаптивный дизайн** для всех устройств

## 🚀 Технологии

- **React 18** с TypeScript
- **Styled Components** для стилизации
- **Vite** для быстрой сборки
- **Axios** для API запросов
- **Современные хуки** React

## 📦 Установка

```bash
# Установка зависимостей
npm install

# Запуск в режиме разработки
npm run dev

# Сборка для продакшена
npm run build
```

## 🔧 Конфигурация

### Прокси к FastAPI

Фронтенд настроен на проксирование запросов к FastAPI серверу:

- `/api/*` → `http://localhost:8000/api/*`
- `/chat` → `http://localhost:8000/chat`
- `/auth/*` → `http://localhost:8000/auth/*`

### Переменные окружения

Создайте файл `.env.local`:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=AI Chat
```

## 🏗️ Структура проекта

```
src/
├── components/          # React компоненты
│   ├── ChatContainer.tsx # Основной контейнер чата
│   ├── Sidebar.tsx     # Боковая панель с персонажами
│   ├── ChatArea.tsx    # Область сообщений
│   ├── Message.tsx     # Компонент сообщения
│   ├── MessageInput.tsx # Поле ввода
│   ├── AuthModal.tsx   # Модальное окно авторизации
│   ├── LoadingSpinner.tsx # Индикатор загрузки
│   └── ErrorMessage.tsx # Сообщения об ошибках
├── styles/             # Глобальные стили
│   └── GlobalStyles.ts
├── theme.ts           # Тема приложения
├── App.tsx            # Главный компонент
└── main.tsx           # Точка входа
```

## 🎯 Основные компоненты

### ChatContainer
Главный компонент, управляющий состоянием чата:
- Управление сообщениями
- Авторизация пользователей
- Интеграция с API

### Sidebar
Боковая панель с персонажами:
- Список доступных персонажей
- Переключение между персонажами
- Информация об авторизации

### ChatArea
Область отображения сообщений:
- Автоматическая прокрутка
- Индикатор загрузки
- Пустое состояние

### MessageInput
Поле ввода сообщений:
- Автоматическое изменение высоты
- Отправка по Enter
- Генерация изображений

## 🔌 API Интеграция

### Эндпоинты

- `POST /chat` - Отправка сообщения
- `GET /api/auth/me` - Проверка авторизации
- `POST /api/auth/login` - Вход в систему
- `GET /auth/google` - Google OAuth

### Типы данных

```typescript
interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  imageUrl?: string;
}

interface Character {
  id: string;
  name: string;
  description: string;
  avatar?: string;
}
```

## 🎨 Тема

Тема включает:

- **Цвета**: Фиолетовые, черные, пурпурные оттенки
- **Градиенты**: Плавные переходы цветов
- **Тени**: Эффекты свечения и глубины
- **Анимации**: Плавные переходы и эффекты
- **Типографика**: Современные шрифты и размеры

## 📱 Адаптивность

- **Desktop**: Полнофункциональный интерфейс
- **Tablet**: Адаптированная боковая панель
- **Mobile**: Мобильная версия с оптимизированным UX

## 🚀 Развертывание

### Локальная разработка

```bash
# Запуск FastAPI сервера
cd ../app
uvicorn main:app --reload

# Запуск React приложения
cd frontend
npm run dev
```

### Продакшен

```bash
# Сборка React приложения
npm run build

# Статические файлы будут в dist/
```

## 🔧 Разработка

### Добавление новых компонентов

1. Создайте компонент в `src/components/`
2. Используйте styled-components для стилизации
3. Применяйте тему из `theme.ts`
4. Добавьте TypeScript типы

### Стилизация

Используйте тему для консистентности:

```typescript
import { theme } from '../theme';

const StyledComponent = styled.div`
  background: ${theme.colors.gradients.main};
  color: ${theme.colors.text.primary};
  padding: ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.lg};
`;
```

## 📄 Лицензия

MIT License