import React from 'react';
import styled from 'styled-components';
import { theme } from '../theme';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: ${theme.colors.background.primary};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.xl};
  width: 90%;
  max-width: 400px;
  border: 1px solid ${theme.colors.border.accent};
  box-shadow: ${theme.colors.shadow.message};
  text-align: center;
`;

const Title = styled.h2`
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.lg};
  font-weight: 700;
  margin: 0 0 ${theme.spacing.lg} 0;
`;

const Message = styled.p`
  color: ${theme.colors.text.secondary};
  font-size: ${theme.fontSize.md};
  margin: 0 0 ${theme.spacing.xl} 0;
  line-height: 1.5;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  justify-content: center;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.fontSize.md};
  font-weight: 600;
  cursor: pointer;
  transition: ${theme.transition.fast};
  border: none;
  min-width: 100px;
  
  ${props => {
    if (props.variant === 'primary') {
      return `
        background: #dc2626;
        color: white;
        
        &:hover {
          background: #b91c1c;
          transform: translateY(-2px);
          box-shadow: ${theme.colors.shadow.button};
        }
        
        &:active {
          transform: translateY(0);
        }
      `;
    } else {
      return `
        background: transparent;
        color: ${theme.colors.text.primary};
        border: 2px solid;
        border-image: linear-gradient(45deg, #764ba2 50%, #4a0000 50%) 1;
        
        &:hover {
          border-image: linear-gradient(45deg, #8b5cf6 50%, #7f1d1d 50%) 1;
          transform: scale(1.05);
        }
        
        &:active {
          transform: scale(0.95);
        }
      `;
    }
  }}
`;

interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  title,
  message,
  confirmText = 'OK',
  cancelText = 'Отмена',
  onConfirm,
  onCancel
}) => {
  if (!isOpen) return null;

  return (
    <ModalOverlay onClick={onCancel}>
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <Title>{title}</Title>
        <Message>{message}</Message>
        <ButtonGroup>
          <Button variant="secondary" onClick={onCancel}>
            {cancelText}
          </Button>
          <Button variant="primary" onClick={onConfirm}>
            {confirmText}
          </Button>
        </ButtonGroup>
      </ModalContent>
    </ModalOverlay>
  );
};
