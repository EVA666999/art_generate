import React from 'react';
import styled from 'styled-components';
import { theme } from '../theme';

const SidebarContainer = styled.div`
  width: 80px;
  min-width: 80px;
  height: 100vh;
  background: rgba(22, 33, 62, 0.3); /* Очень прозрачный */
  backdrop-filter: blur(5px);
  padding: ${theme.spacing.lg} ${theme.spacing.md};
  border-right: 1px solid ${theme.colors.border.accent};
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow-y: auto;
  overflow-x: hidden;
  
  /* Добавляем эффект свечения */
  &::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 1px;
    height: 100%;
    background: ${theme.colors.gradients.button};
    opacity: 0.3;
  }
`;

const Logo = styled.div`
  width: 50px;
  height: 50px;
  border-radius: ${theme.borderRadius.full};
  background: ${theme.colors.gradients.button};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: ${theme.fontSize.xl};
  margin-bottom: ${theme.spacing.xl};
  box-shadow: ${theme.colors.shadow.button};
  
  /* Сердечко как на картинке */
  &::before {
    content: '♥';
    color: ${theme.colors.text.primary};
  }
`;

const NavItem = styled.button`
  width: 80px;
  height: 50px;
  border-radius: ${theme.borderRadius.lg};
  background: ${theme.colors.background.secondary};
  border: 1px solid ${theme.colors.border.primary};
  color: ${theme.colors.text.primary};
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: ${theme.spacing.md};
  transition: ${theme.transition.fast};
  cursor: pointer;
  font-size: ${theme.fontSize.sm};
  font-weight: 600;
  text-align: center;
  
  &:hover {
    background: ${theme.colors.background.tertiary};
    border-color: ${theme.colors.accent.primary};
  }
`;

const QuickActions = styled.div`
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
`;

const ActionButton = styled.button`
  width: 80px;
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
  font-size: ${theme.fontSize.sm};
  font-weight: 600;
  text-align: center;
  position: relative;
  
  /* Градиентный текст */
  background: linear-gradient(135deg, #a8a8a8, #ffffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  
  /* Светящаяся линия снизу */
  &::after {
    content: '';
    position: absolute;
    bottom: -4px;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
    filter: blur(1px);
  }
  
  &:hover {
    transform: scale(1.05);
    border-image: linear-gradient(45deg, #8b5cf6 50%, #7f1d1d 50%) 1;
    
    /* Более яркий градиент при hover */
    background: linear-gradient(135deg, #ffffff, rgba(102, 126, 234, 0.9));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    
    /* Показываем светящуюся линию */
    &::after {
      opacity: 1;
    }
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

const Tooltip = styled.div`
  position: absolute;
  left: 60px;
  top: 50%;
  transform: translateY(-50%);
  background: ${theme.colors.background.primary};
  color: ${theme.colors.text.primary};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.fontSize.sm};
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: ${theme.transition.fast};
  z-index: 1000;
  border: 1px solid ${theme.colors.border.accent};
  box-shadow: ${theme.colors.shadow.message};
  
  &::before {
    content: '';
    position: absolute;
    left: -6px;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-top: 6px solid transparent;
    border-bottom: 6px solid transparent;
    border-right: 6px solid ${theme.colors.background.primary};
  }
`;

const NavItemWithTooltip = styled.div`
  position: relative;
  
  &:hover ${Tooltip} {
    opacity: 1;
  }
`;

interface CompactSidebarProps {
  onCreateCharacter: () => void;
  onShop: () => void;
  onMyCharacters: () => void;
}

export const CompactSidebar: React.FC<CompactSidebarProps> = ({
  onCreateCharacter,
  onShop,
  onMyCharacters
}) => {
  return (
    <SidebarContainer>
      <Logo />
      
      <QuickActions>
        <ActionButton onClick={onCreateCharacter}>
          Персонаж
        </ActionButton>
        <ActionButton onClick={onMyCharacters}>
          Мои
        </ActionButton>
        <ActionButton onClick={onShop}>
          Магазин
        </ActionButton>
      </QuickActions>
    </SidebarContainer>
  );
};
