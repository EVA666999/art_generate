import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { theme } from '../theme';
import { ChatArea } from './ChatArea';
import { MessageInput } from './MessageInput';
import { AuthModal } from './AuthModal';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';

const Container = styled.div`
  width: 100vw;
  height: 100vh;
  display: flex;
  position: relative;
  overflow: hidden;

  /* Адаптивность для мобильных устройств */
  @media (max-width: 1024px) {
    height: auto;
    min-height: 100vh;
    flex-direction: column;
  }
`;

const CompactSidebar = styled.div`
  width: 80px;
  min-width: 80px;
  height: 100vh;
  background: rgba(22, 33, 62, 0.3);
  backdrop-filter: blur(5px);
  padding: ${theme.spacing.lg};
  border-right: 1px solid ${theme.colors.border.accent};
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${theme.spacing.md};
  position: relative;
  
  /* Адаптивность для мобильных устройств */
  @media (max-width: 1024px) {
    width: 100%;
    height: auto;
    min-height: 80px;
    flex-direction: row;
    justify-content: center;
    border-right: none;
    border-bottom: 1px solid ${theme.colors.border.accent};
  }
`;

const ActionButton = styled.button`
  width: 60px;
  height: 40px;
  border-radius: ${theme.borderRadius.lg};
  background: transparent;
  border: 2px solid;
  border-image: linear-gradient(45deg, #764ba2 50%, #4a0000 50%) 1;
  color: #a8a8a8;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform ${theme.transition.fast};
  cursor: pointer;
  font-size: ${theme.fontSize.xs};
  font-weight: 600;
  text-align: center;
  
  &:hover {
    transform: scale(1.05);
    border-image: linear-gradient(45deg, #8b5cf6 50%, #7f1d1d 50%) 1;
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

const BackButton = styled.button`
  width: 60px;
  height: 40px;
  border-radius: ${theme.borderRadius.lg};
  background: transparent;
  border: 2px solid;
  border-image: linear-gradient(45deg, #764ba2 50%, #4a0000 50%) 1;
  color: #a8a8a8;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform ${theme.transition.fast};
  cursor: pointer;
  font-size: ${theme.fontSize.xs};
  font-weight: 600;
  text-align: center;
  
  &:hover {
    transform: scale(1.05);
    border-image: linear-gradient(45deg, #8b5cf6 50%, #7f1d1d 50%) 1;
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

const MainContent = styled.div`
  flex: 1;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: transparent; /* Полностью прозрачный */
  border-radius: ${theme.borderRadius.xl} 0 0 ${theme.borderRadius.xl};
  margin-left: ${theme.spacing.md};
  box-shadow: ${theme.colors.shadow.card};
  overflow: hidden;

  /* Адаптивность для мобильных устройств */
  @media (max-width: 1024px) {
    height: auto;
    flex: 1;
    border-radius: 0;
    margin-left: 0;
    margin-top: ${theme.spacing.md};
  }
`;

const ChatHeader = styled.div`
  background: rgba(102, 126, 234, 0.3); /* Очень прозрачный */
  backdrop-filter: blur(5px);
  color: ${theme.colors.text.primary};
  padding: ${theme.spacing.lg} ${theme.spacing.xl};
  text-align: center;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: ${theme.colors.gradients.buttonHover};
  }
`;

const HeaderContent = styled.div`
  flex: 1;
  text-align: center;
`;

const Title = styled.h1`
  font-size: ${theme.fontSize['2xl']};
  font-weight: 600;
  margin-bottom: ${theme.spacing.sm};
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
`;

const Subtitle = styled.p`
  font-size: ${theme.fontSize.sm};
  opacity: 0.9;
  font-weight: 300;
`;

const ChatMessagesArea = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0; /* Важно для flex-элементов */
`;

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

interface UserInfo {
  id: number;
  username: string;
  coins: number;
}

interface ChatContainerProps {
  onBackToMain?: () => void;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({ onBackToMain }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentCharacter, setCurrentCharacter] = useState<Character>({
    id: 'anna',
    name: 'Anna',
    description: 'Дружелюбный помощник с теплым характером'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [modelInfo, setModelInfo] = useState<string>('Загрузка...');

  // Проверка авторизации при загрузке
  useEffect(() => {
    // Проверяем токены в URL параметрах (после OAuth)
    const urlParams = new URLSearchParams(window.location.search);
    const accessToken = urlParams.get('access_token');
    const refreshToken = urlParams.get('refresh_token');
    
    if (accessToken && refreshToken) {
      // Сохраняем токены в localStorage
      localStorage.setItem('authToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      
      // Очищаем URL от токенов
      window.history.replaceState({}, document.title, window.location.pathname);
      
      // Проверяем авторизацию
      checkAuth();
    } else {
      // Обычная проверка авторизации
      checkAuth();
    }
    
    loadModelInfo();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        // Нет токена - пользователь не авторизован
        setIsAuthenticated(false);
        setUserInfo(null);
        return;
      }

      // Проверяем токен через API
      const response = await fetch('/auth/me/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setIsAuthenticated(true);
        setUserInfo({
          id: userData.id,
          username: userData.username || 'Пользователь',
          coins: userData.coins || 0
        });
      } else {
        // Токен недействителен
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        setIsAuthenticated(false);
        setUserInfo(null);
      }
    } catch (error) {
      // Только логируем ошибку, не показываем в консоли для неавторизованных пользователей
      if (localStorage.getItem('authToken')) {
        console.error('Ошибка проверки авторизации:', error);
      }
      setIsAuthenticated(false);
      setUserInfo(null);
    }
  };

  const loadModelInfo = async () => {
    try {
      const response = await fetch('/api/v1/models/');
      if (response.ok) {
        const models = await response.json();
        setModelInfo(`${models.length} модель(ей) доступно`);
      }
    } catch (error) {
      console.error('Ошибка загрузки информации о моделях:', error);
      setModelInfo('Информация недоступна');
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    // Проверяем авторизацию
    if (!isAuthenticated) {
      setIsAuthModalOpen(true);
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          character: currentCharacter.id,
          history: messages,
          session_id: `chat_${Date.now()}`,
          user_id: userInfo ? userInfo.id : undefined // Используем реальный ID пользователя
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка отправки сообщения');
      }

      const data = await response.json();
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.response || 'Извините, не удалось получить ответ',
        timestamp: new Date(),
        imageUrl: data.image_url
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Обновляем информацию о пользователе после отправки сообщения
      if (isAuthenticated) {
        await checkAuth();
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Произошла ошибка');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCharacterSelect = (character: Character) => {
    setCurrentCharacter(character);
    setMessages([]); // Очищаем историю при смене персонажа
  };

  const handleAuthSuccess = (token: string) => {
    localStorage.setItem('authToken', token);
    setIsAuthenticated(true);
    setIsAuthModalOpen(false);
    checkAuth(); // Обновляем информацию о пользователе
  };

  const handleQuickAction = async (action: string) => {
    switch (action) {
      case 'gallery':
        window.open('/paid_gallery/', '_blank');
        break;
      case 'shop':
        showShopModal();
        break;
      case 'create':
        showCreateCharacterModal();
        break;
      case 'clear':
        clearChat();
        break;
      default:
        console.log('Неизвестное действие:', action);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  const showShopModal = () => {
    // Временная реализация - можно заменить на модальное окно
    alert('Функция магазина будет реализована в следующих версиях');
  };

  const showCreateCharacterModal = () => {
    // Временная реализация - можно заменить на модальное окно
    alert('Функция создания персонажа будет реализована в следующих версиях');
  };

  return (
    <Container>
      <CompactSidebar>
        <ActionButton onClick={onBackToMain}>
          Домой
        </ActionButton>
        <BackButton onClick={onBackToMain}>
          Назад
        </BackButton>
        <ActionButton onClick={() => alert('Платная галерея')}>
          Галерея
        </ActionButton>
        <ActionButton onClick={() => setMessages([])}>
          Очистить
        </ActionButton>
        <ActionButton onClick={() => alert('Генерация фото')}>
          Фото
        </ActionButton>
      </CompactSidebar>
      
      <MainContent>
        <ChatMessagesArea>
          <ChatArea 
            messages={messages}
            isLoading={isLoading}
          />
          
          {error && (
            <ErrorMessage 
              message={error}
              onClose={() => setError(null)}
            />
          )}
          
          <MessageInput 
            onSendMessage={handleSendMessage}
            disabled={isLoading}
            placeholder={`Напишите сообщение ${currentCharacter.name}...`}
          />
        </ChatMessagesArea>
      </MainContent>

      {isAuthModalOpen && (
        <AuthModal 
          isOpen={isAuthModalOpen}
          onClose={() => setIsAuthModalOpen(false)}
          onAuthSuccess={handleAuthSuccess}
        />
      )}
    </Container>
  );
};