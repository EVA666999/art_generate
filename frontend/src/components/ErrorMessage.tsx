import React from 'react';
import styled from 'styled-components';
import { theme } from '../theme';

const ErrorContainer = styled.div`
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: ${theme.colors.status.error};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.lg};
  margin: ${theme.spacing.md} ${theme.spacing.lg};
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: ${theme.spacing.md};
  animation: fadeIn 0.3s ease-out;
`;

const ErrorContent = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  flex: 1;
`;

const ErrorIcon = styled.div`
  font-size: ${theme.fontSize.lg};
  flex-shrink: 0;
`;

const ErrorText = styled.div`
  font-size: ${theme.fontSize.sm};
  font-weight: 500;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: ${theme.colors.status.error};
  cursor: pointer;
  font-size: ${theme.fontSize.lg};
  padding: ${theme.spacing.xs};
  border-radius: ${theme.borderRadius.sm};
  transition: ${theme.transition.fast};
  
  &:hover {
    background: rgba(239, 68, 68, 0.1);
  }
`;

interface ErrorMessageProps {
  message: string;
  onClose?: () => void;
  type?: 'error' | 'warning' | 'info';
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ 
  message, 
  onClose, 
  type = 'error' 
}) => {
  const getIcon = () => {
    switch (type) {
      case 'warning': return '!';
      case 'info': return 'i';
      default: return 'X';
    }
  };

  const getStyles = () => {
    switch (type) {
      case 'warning':
        return {
          background: 'rgba(245, 158, 11, 0.1)',
          borderColor: 'rgba(245, 158, 11, 0.3)',
          color: theme.colors.status.warning
        };
      case 'info':
        return {
          background: 'rgba(59, 130, 246, 0.1)',
          borderColor: 'rgba(59, 130, 246, 0.3)',
          color: theme.colors.status.info
        };
      default:
        return {
          background: 'rgba(239, 68, 68, 0.1)',
          borderColor: 'rgba(239, 68, 68, 0.3)',
          color: theme.colors.status.error
        };
    }
  };

  const styles = getStyles();

  return (
    <ErrorContainer style={styles}>
      <ErrorContent>
        <ErrorIcon>{getIcon()}</ErrorIcon>
        <ErrorText>{message}</ErrorText>
      </ErrorContent>
      {onClose && (
        <CloseButton onClick={onClose} title="Закрыть">
          ×
        </CloseButton>
      )}
    </ErrorContainer>
  );
};
