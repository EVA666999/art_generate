import React, { useEffect, useRef } from 'react';
import styled from 'styled-components';
import { theme } from '../theme';
import { Message } from './Message';

const MessagesContainer = styled.div`
  flex: 1;
  padding: ${theme.spacing.lg};
  overflow-y: auto;
  overflow-x: hidden;
  background: ${theme.colors.background.secondary};
  position: relative;
  min-height: 0; /* Важно для flex-элементов */
  
  /* Добавляем тонкую текстуру */
  background-image: 
    linear-gradient(45deg, transparent 40%, rgba(139, 92, 246, 0.02) 50%, transparent 60%);
  background-size: 30px 30px;
`;

const MessagesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.lg};
  min-height: 100%;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${theme.spacing.xl};
`;

const LoadingMessage = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  padding: ${theme.spacing.lg};
  background: ${theme.colors.gradients.message};
  border-radius: ${theme.borderRadius.xl};
  border: 1px solid ${theme.colors.border.accent};
  box-shadow: ${theme.colors.shadow.message};
  color: ${theme.colors.text.secondary};
  font-style: italic;
`;

const LoadingDots = styled.div`
  display: flex;
  gap: 4px;
  
  span {
    width: 8px;
    height: 8px;
    border-radius: ${theme.borderRadius.full};
    background: ${theme.colors.accent.primary};
    animation: pulse 1.4s ease-in-out infinite;
    
    &:nth-child(1) {
      animation-delay: 0s;
    }
    
    &:nth-child(2) {
      animation-delay: 0.2s;
    }
    
    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
  color: ${theme.colors.text.muted};
  
  h3 {
    font-size: ${theme.fontSize.xl};
    margin-bottom: ${theme.spacing.md};
    color: ${theme.colors.text.secondary};
  }
  
  p {
    font-size: ${theme.fontSize.base};
    line-height: 1.6;
    max-width: 400px;
  }
`;

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  imageUrl?: string;
}

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
}

export const ChatArea: React.FC<ChatAreaProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Автоматическая прокрутка к последнему сообщению
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <MessagesContainer>
      <MessagesList>
        {messages.length === 0 && !isLoading && (
          <EmptyState>
            <h3>Добро пожаловать в чат!</h3>
            <p>
              Выберите персонажа в боковой панели и начните общение. 
              Каждый персонаж имеет свой уникальный характер и стиль общения.
            </p>
          </EmptyState>
        )}
        
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <LoadingMessage>
            <LoadingDots>
              <span></span>
              <span></span>
              <span></span>
            </LoadingDots>
            Генерируется ответ...
          </LoadingMessage>
        )}
        
        <div ref={messagesEndRef} />
      </MessagesList>
    </MessagesContainer>
  );
};
