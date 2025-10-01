import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { theme } from '../theme';

const InputContainer = styled.div`
  padding: ${theme.spacing.lg};
  background: ${theme.colors.gradients.card};
  border-top: 1px solid ${theme.colors.border.accent};
  position: relative;
`;

const InputWrapper = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  align-items: flex-end;
  max-width: 100%;
`;

const TextArea = styled.textarea<{ $isDisabled: boolean }>`
  flex: 1;
  min-height: 50px;
  max-height: 120px;
  padding: ${theme.spacing.md};
  background: ${theme.colors.background.secondary};
  border: 2px solid ${theme.colors.border.primary};
  border-radius: ${theme.borderRadius.lg};
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.base};
  font-family: inherit;
  resize: none;
  transition: ${theme.transition.fast};
  opacity: ${props => props.$isDisabled ? 0.6 : 1};
  
  &:focus {
    border-color: ${theme.colors.accent.primary};
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
    outline: none;
  }
  
  &::placeholder {
    color: ${theme.colors.text.muted};
  }
  
  &:disabled {
    cursor: not-allowed;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
`;

const SendButton = styled.button<{ $isDisabled: boolean }>`
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  background: ${props => props.$isDisabled 
    ? theme.colors.background.tertiary 
    : theme.colors.gradients.button
  };
  color: ${theme.colors.text.primary};
  border: none;
  border-radius: ${theme.borderRadius.lg};
  font-weight: 600;
  font-size: ${theme.fontSize.base};
  cursor: ${props => props.$isDisabled ? 'not-allowed' : 'pointer'};
  transition: ${theme.transition.fast};
  opacity: ${props => props.$isDisabled ? 0.6 : 1};
  
  &:hover:not(:disabled) {
    background: ${theme.colors.gradients.buttonHover};
    box-shadow: ${theme.colors.shadow.button};
    transform: translateY(-2px);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
`;

const ImageButton = styled.button<{ $isDisabled: boolean }>`
  padding: ${theme.spacing.md};
  background: ${props => props.$isDisabled 
    ? theme.colors.background.tertiary 
    : theme.colors.gradients.card
  };
  color: ${theme.colors.text.primary};
  border: 2px solid ${props => props.$isDisabled 
    ? theme.colors.border.primary 
    : theme.colors.border.accent
  };
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.fontSize.lg};
  cursor: ${props => props.$isDisabled ? 'not-allowed' : 'pointer'};
  transition: ${theme.transition.fast};
  opacity: ${props => props.$isDisabled ? 0.6 : 1};
  
  &:hover:not(:disabled) {
    border-color: ${theme.colors.accent.primary};
    background: ${theme.colors.background.tertiary};
    transform: translateY(-2px);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
`;

const CharacterIndicator = styled.div`
  position: absolute;
  top: ${theme.spacing.sm};
  left: ${theme.spacing.lg};
  font-size: ${theme.fontSize.sm};
  color: ${theme.colors.text.muted};
  background: ${theme.colors.background.secondary};
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  border-radius: ${theme.borderRadius.md};
  border: 1px solid ${theme.colors.border.primary};
`;

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  currentCharacter?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Введите сообщение...",
  currentCharacter = "Anna"
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Автоматическое изменение высоты textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleImageGeneration = () => {
    if (message.trim() && !disabled) {
      // Здесь можно добавить специальную логику для генерации изображений
      onSendMessage(`Генерирую изображение: ${message.trim()}`);
    }
  };

  return (
    <InputContainer>
      <CharacterIndicator>
        Чат с {currentCharacter}
      </CharacterIndicator>
      
      <form onSubmit={handleSubmit}>
        <InputWrapper>
          <TextArea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            $isDisabled={disabled}
            rows={1}
          />
          
          <ButtonGroup>
            <SendButton
              type="submit"
              disabled={disabled || !message.trim()}
              $isDisabled={disabled || !message.trim()}
            >
              Отправить
            </SendButton>
            
            <ImageButton
              type="button"
              onClick={handleImageGeneration}
              disabled={disabled || !message.trim()}
              $isDisabled={disabled || !message.trim()}
              title="Генерировать изображение"
            >
              IMG
            </ImageButton>
          </ButtonGroup>
        </InputWrapper>
      </form>
    </InputContainer>
  );
};
