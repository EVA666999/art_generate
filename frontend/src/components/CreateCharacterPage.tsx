import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { theme } from '../theme';
import { CompactSidebar } from './CompactSidebar';

const MainContainer = styled.div`
  width: 100vw;
  height: 100vh;
  display: flex;
  background: transparent;
  overflow: visible;
  box-sizing: border-box;
`;

const ContentArea = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: transparent;
  overflow: visible;
  width: calc(100vw - 80px);
  min-width: 0;
`;

const Header = styled.div`
  background: rgba(102, 126, 234, 0.1);
  backdrop-filter: blur(3px);
  padding: ${theme.spacing.lg} ${theme.spacing.xl};
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid ${theme.colors.border.accent};
  z-index: 10;
`;

const BackButton = styled.button`
  background: transparent;
  border: none;
  color: ${theme.colors.text.secondary};
  font-size: ${theme.fontSize.md};
  cursor: pointer;
  transition: color ${theme.transition.fast};
  
  &:hover {
    color: ${theme.colors.text.primary};
  }
`;

const PageTitle = styled.h2`
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.xl};
  margin: 0;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  background: rgba(22, 33, 62, 0.3);
  backdrop-filter: blur(5px);
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${theme.colors.border.accent};
`;

const UserName = styled.span`
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.sm};
  font-weight: 600;
`;

const UserCoins = styled.span`
  color: ${theme.colors.accent.primary};
  font-size: ${theme.fontSize.sm};
  font-weight: 600;
`;

const AuthButton = styled.button`
  background: transparent;
  border: 2px solid;
  border-image: linear-gradient(45deg, #764ba2 50%, #4a0000 50%) 1;
  color: #a8a8a8;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.fontSize.sm};
  font-weight: 600;
  cursor: pointer;
  transition: transform ${theme.transition.fast};
  margin-left: ${theme.spacing.sm};
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

const MainContent = styled.div`
  flex: 1;
  padding: 0;
  overflow-y: auto;
  display: flex;
  gap: 0;
  width: 100%;
  height: 100%;
`;

const LeftColumn = styled.div`
  flex: 1; /* Равная ширина с правым столбцом */
  min-width: 0;
  min-height: calc(150vh - 80px); /* Увеличиваем высоту столбцов */
  background: rgba(22, 33, 62, 0.3);
  backdrop-filter: blur(5px);
  border-radius: 0;
  padding: 0;
  border: 1px solid ${theme.colors.border.accent};
  box-shadow: ${theme.colors.shadow.message};
  display: flex;
  flex-direction: column;
`;

const RightColumn = styled.div`
  flex: 1; /* Равная ширина с левым столбцом */
  min-width: 0;
  min-height: calc(150vh - 80px); /* Увеличиваем высоту столбцов */
  background: transparent; /* Убираем фон чтобы был виден основной фон */
  backdrop-filter: none; /* Убираем размытие */
  border-radius: 0;
  padding: 0;
  border: 1px solid ${theme.colors.border.accent};
  box-shadow: none; /* Убираем тень */
  display: flex;
  flex-direction: column;
`;

const ThirdColumn = styled.div`
  display: none; /* Скрываем третий столбец */
`;

const Form = styled.form`
  display: contents;
`;

const ColumnContent = styled.div`
  padding: ${theme.spacing.md} ${theme.spacing.sm};
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const FormGroup = styled.div`
  margin-bottom: ${theme.spacing.lg};
`;

const Label = styled.label`
  display: block;
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.sm};
  font-weight: 600;
  margin-bottom: 4px;
`;

const Input = styled.input`
  width: 100%;
  padding: ${theme.spacing.md};
  border: none;
  border-radius: ${theme.borderRadius.md};
  background: rgba(22, 33, 62, 0.3);
  backdrop-filter: blur(5px);
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.sm};
  
  &::placeholder {
    color: ${theme.colors.text.secondary};
  }
  
  &:focus {
    outline: none;
    background: rgba(22, 33, 62, 0.5);
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: ${theme.spacing.md};
  border: 1px solid ${theme.colors.border.accent};
  border-radius: ${theme.borderRadius.md};
  background: rgba(22, 33, 62, 0.3);
  backdrop-filter: blur(5px);
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.sm};
  font-family: inherit;
  resize: vertical;
  
  &::placeholder {
    color: ${theme.colors.text.secondary};
  }
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.accent.primary};
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
  }
`;

const Button = styled.button<{ $variant?: 'primary' | 'secondary' }>`
  background: transparent;
  border: 2px solid;
  border-image: linear-gradient(45deg, #764ba2 50%, #4a0000 50%) 1;
  color: #a8a8a8;
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.fontSize.md};
  font-weight: 600;
  cursor: pointer;
  transition: transform ${theme.transition.fast};
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
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    
    &::after {
      opacity: 0;
    }
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  justify-content: center;
`;

const CoinsDisplay = styled.div`
  background: rgba(22, 33, 62, 0.3);
  backdrop-filter: blur(5px);
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.md};
  border: 1px solid ${theme.colors.border.accent};
  margin-bottom: ${theme.spacing.lg};
  text-align: center;
`;

const CoinsText = styled.span`
  color: ${theme.colors.accent.primary};
  font-size: ${theme.fontSize.md};
  font-weight: 600;
`;

const PhotoGenerationBox = styled.div`
  background: rgba(22, 33, 62, 0.2);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  margin: ${theme.spacing.lg} 0;
  text-align: center;
`;

const PhotoGenerationBoxTitle = styled.h3`
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.md};
  font-weight: 600;
  margin: 0 0 ${theme.spacing.sm} 0;
`;

const PhotoGenerationDescription = styled.p`
  color: ${theme.colors.text.secondary};
  font-size: ${theme.fontSize.sm};
  margin: 0 0 ${theme.spacing.md} 0;
  line-height: 1.4;
`;

const PhotoGenerationPlaceholder = styled.div`
  background: rgba(22, 33, 62, 0.3);
  border: 1px solid ${theme.colors.border.accent}; /* Сплошная обводка как у столбцов */
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.xl};
  color: ${theme.colors.text.secondary};
  font-size: ${theme.fontSize.lg};
  min-height: calc(120vh - 300px); /* Увеличиваем высоту области для фото */
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ErrorMessage = styled.div`
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.md};
  margin: ${theme.spacing.md} 0;
  font-size: ${theme.fontSize.sm};
`;

const SuccessMessage = styled.div`
  color: #51cf66;
  background: rgba(81, 207, 102, 0.1);
  border: 1px solid rgba(81, 207, 102, 0.3);
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.md};
  margin: ${theme.spacing.md} 0;
  font-size: ${theme.fontSize.sm};
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: ${theme.colors.accent.primary};
  animation: spin 1s ease-in-out infinite;
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

const HintDescription = styled.span`
  color: ${theme.colors.text.secondary};
`;

const PhotoModal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: ${theme.spacing.xl};
`;

const PhotoModalContent = styled.div`
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
`;

const PhotoModalImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: ${theme.borderRadius.lg};
`;

const PhotoModalClose = styled.button`
  position: absolute;
  top: -40px;
  right: 0;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: ${theme.fontSize.xl};
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }
`;

const PhotosContainer = styled.div`
  position: relative;
  width: 100%;
  height: 400px; /* Фиксированная высота чтобы столбец не менял размеры */
`;

const SwiperContainer = styled.div`
  position: relative;
  overflow: hidden;
  height: 100%;
`;

const SwiperWrapper = styled.div<{ translateX: number }>`
  display: flex;
  transition: transform 0.3s ease;
  transform: translateX(${props => props.translateX}px);
  height: 100%;
`;

const SwiperSlide = styled.div`
  min-width: 200px;
  margin-right: ${theme.spacing.md};
  height: 100%;
  
  &:last-child {
    margin-right: 0;
  }
`;

const SwiperButton = styled.button<{ direction: 'left' | 'right' }>`
  position: absolute;
  top: 50%;
  ${props => props.direction === 'left' ? 'left: -20px' : 'right: -20px'};
  transform: translateY(-50%);
  background: rgba(102, 126, 234, 0.8);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: ${theme.fontSize.lg};
  z-index: 10;
  
  &:hover {
    background: rgba(102, 126, 234, 1);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const FullSizePhotoSlider = styled.div`
  position: relative;
  width: 100%;
  height: 700px; /* Высота для описания без превью */
`;

const SliderButton = styled.button<{ direction: 'left' | 'right' }>`
  position: absolute;
  top: 50%;
  ${props => props.direction === 'left' ? 'left: -20px' : 'right: -20px'};
  transform: translateY(-50%);
  background: rgba(102, 126, 234, 0.8);
  border: none;
  color: white;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  z-index: 10;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 1);
    transform: translateY(-50%) scale(1.1);
  }
  
  &:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
`;

const SliderContainer = styled.div`
  position: relative;
  overflow: hidden;
  height: 100%;
  width: 100%;
`;

const SliderWrapper = styled.div<{ translateX: number }>`
  display: flex;
  transition: transform 0.3s ease;
  transform: translateX(${props => props.translateX}%);
  height: 100%;
`;

const SliderSlide = styled.div`
  min-width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.sm};
`;

const FullSizePhoto = styled.img`
  width: auto;
  max-width: 100%;
  height: auto;
  max-height: 500px; /* Ограничиваем максимальную высоту */
  border-radius: ${theme.borderRadius.lg};
  border: 2px solid ${theme.colors.border.accent};
  transition: all 0.3s ease;
  object-fit: contain; /* Сохраняем пропорции */
  
  &:hover {
    border-color: ${theme.colors.accent.primary};
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
    transform: scale(1.02);
  }
`;

const SliderDescription = styled.div`
  position: absolute;
  bottom: -100px;
  left: 0;
  right: 0;
  padding: ${theme.spacing.md};
`;

const DescriptionTitle = styled.h3`
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.lg};
  font-weight: 600;
  margin: 0 0 ${theme.spacing.sm} 0;
  text-align: center;
`;

const DescriptionText = styled.p`
  color: ${theme.colors.text.secondary};
  font-size: ${theme.fontSize.sm};
  margin: 0 0 ${theme.spacing.sm} 0;
  text-align: center;
  line-height: 1.5;
`;

const SavePhotosButton = styled.button`
  background: ${theme.colors.gradients.button};
  color: ${theme.colors.text.primary};
  border: none;
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  font-size: ${theme.fontSize.sm};
  font-weight: 600;
  cursor: pointer;
  margin-top: ${theme.spacing.sm};
  transition: ${theme.transition.fast};
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: ${theme.colors.shadow.glow};
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const DescriptionNote = styled.p`
  color: ${theme.colors.accent.primary};
  font-size: ${theme.fontSize.sm};
  font-weight: 500;
  margin: 0;
  text-align: center;
  font-style: italic;
`;

const CharacterCardPreview = styled.div`
  position: absolute;
  bottom: -200px;
  left: 0;
  right: 0;
  background: rgba(22, 33, 62, 0.9);
  backdrop-filter: blur(10px);
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.md};
  border: 1px solid ${theme.colors.border.accent};
`;

const PreviewTitle = styled.h4`
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.md};
  font-weight: 600;
  margin: 0 0 ${theme.spacing.md} 0;
  text-align: center;
`;

const PreviewCardContainer = styled.div`
  display: flex;
  justify-content: center;
`;

const PreviewCard = styled.div`
  background: rgba(22, 33, 62, 0.3);
  backdrop-filter: blur(5px);
  border-radius: ${theme.borderRadius.lg};
  border: 1px solid ${theme.colors.border.accent};
  box-shadow: ${theme.colors.shadow.message};
  width: 200px;
  height: 150px;
  position: relative;
  overflow: hidden;
`;

const PreviewSlideShow = styled.div`
  width: 100%;
  height: 100%;
  position: relative;
`;

const PreviewSlideImage = styled.img<{ $isActive: boolean }>`
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
  opacity: ${props => props.$isActive ? 1 : 0};
  transition: opacity 0.3s ease;
`;

const PreviewDots = styled.div`
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 4px;
  z-index: 3;
`;

const PreviewDot = styled.div<{ $isActive: boolean }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.$isActive ? 'rgba(255, 255, 255, 0.9)' : 'rgba(255, 255, 255, 0.5)'};
  transition: background 0.3s ease;
`;

const PreviewPlaceholder = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102, 126, 234, 0.1);
`;

const PreviewPlaceholderText = styled.span`
  color: ${theme.colors.text.secondary};
  font-size: ${theme.fontSize.sm};
  text-align: center;
`;

const PhotoGenerationSection = styled.div<{ $isExpanded: boolean }>`
  background: rgba(22, 33, 62, 0.15);
  backdrop-filter: blur(10px);
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.lg};
  border: 1px solid rgba(102, 126, 234, 0.3);
  margin-top: ${theme.spacing.xl};
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(102, 126, 234, 0.1);
  max-height: ${props => props.$isExpanded ? '600px' : '0'};
  overflow: hidden;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: ${props => props.$isExpanded ? '1' : '0'};
  transform: ${props => props.$isExpanded ? 'translateY(0)' : 'translateY(-20px)'};
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, ${theme.colors.accent.primary}, transparent);
    opacity: ${props => props.$isExpanded ? '1' : '0'};
    transition: opacity 0.6s ease;
  }
`;

const PhotoGenerationMainTitle = styled.h3`
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.xl};
  font-weight: 700;
  margin: 0 0 ${theme.spacing.xl} 0;
  text-align: center;
  background: linear-gradient(135deg, ${theme.colors.text.primary}, ${theme.colors.accent.primary});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, transparent, ${theme.colors.accent.primary}, transparent);
  }
`;

const PromptSection = styled.div`
  display: flex;
  gap: ${theme.spacing.lg};
  align-items: flex-start;
  margin-bottom: ${theme.spacing.xl};
`;

const PromptContainer = styled.div`
  flex: 1;
  background: rgba(22, 33, 62, 0.2);
  backdrop-filter: blur(8px);
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.lg};
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  position: relative;
  max-width: 400px;
`;

const PromptLabel = styled.label`
  display: block;
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.md};
  font-weight: 600;
  margin-bottom: ${theme.spacing.md};
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
`;

const PromptInput = styled.textarea`
  background: rgba(22, 33, 62, 0.1);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.lg};
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.md};
  font-family: inherit;
  resize: vertical;
  min-height: 120px;
  width: 100%;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
  
  &::placeholder {
    color: ${theme.colors.text.secondary};
    opacity: 0.7;
  }
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.accent.primary};
    box-shadow: 
      inset 0 2px 4px rgba(0, 0, 0, 0.1),
      0 0 0 3px rgba(102, 126, 234, 0.2),
      0 0 20px rgba(102, 126, 234, 0.1);
    transform: translateY(-1px);
  }
`;

const GenerateSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.lg};
  min-width: 180px;
  align-items: center;
`;

const GenerateButton = styled.button`
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(139, 92, 246, 0.1));
  backdrop-filter: blur(8px);
  border: 2px solid;
  border-image: linear-gradient(45deg, ${theme.colors.accent.primary}, ${theme.colors.accent.secondary}) 1;
  color: ${theme.colors.text.primary};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.fontSize.sm};
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
  position: relative;
  overflow: hidden;
  min-width: 160px;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s ease;
  }
  
  &:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 
      0 8px 32px rgba(102, 126, 234, 0.3),
      0 0 0 1px rgba(102, 126, 234, 0.3);
    border-image: linear-gradient(45deg, ${theme.colors.accent.primary}, ${theme.colors.accent.secondary}) 1;
    
    &::before {
      left: 100%;
    }
  }
  
  &:active {
    transform: translateY(0) scale(0.98);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  }
`;

const LargeTextInputArea = styled.div`
  background: rgba(22, 33, 62, 0.2);
  backdrop-filter: blur(8px);
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.xl};
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  margin-top: ${theme.spacing.xl};
  flex: 1;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  width: 100%;
`;

const LargeTextInput = styled.textarea`
  background: rgba(22, 33, 62, 0.3);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.md};
  font-family: inherit;
  resize: vertical;
  flex: 1;
  width: 100%;
  min-height: 200px;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
  
  &::placeholder {
    color: ${theme.colors.text.secondary};
    opacity: 0.7;
  }
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.accent.primary};
    box-shadow: 
      inset 0 2px 4px rgba(0, 0, 0, 0.1),
      0 0 0 2px rgba(102, 126, 234, 0.2);
  }
`;

const LargeTextLabel = styled.label`
  display: block;
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.lg};
  font-weight: 600;
  margin-bottom: ${theme.spacing.md};
  background: linear-gradient(135deg, ${theme.colors.accent.primary}, ${theme.colors.accent.secondary});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const PhotoCard = styled.div<{ isSelected?: boolean }>`
  position: relative;
  background: rgba(22, 33, 62, 0.1);
  backdrop-filter: blur(8px);
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.lg};
  border: 2px solid ${props => 
    props.isSelected ? theme.colors.accent.primary : 
    'rgba(102, 126, 234, 0.2)'};
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${props => props.isSelected 
      ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.1), transparent)'
      : 'linear-gradient(135deg, rgba(102, 126, 234, 0.05), transparent)'};
    opacity: ${props => props.isSelected ? '1' : '0'};
    transition: opacity 0.3s ease;
  }
  
  &:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    border-color: ${props => props.isSelected 
      ? theme.colors.accent.primary 
      : 'rgba(102, 126, 234, 0.4)'};
    
    &::before {
      opacity: 1;
    }
  }
`;

const PhotoImage = styled.img`
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: ${theme.borderRadius.lg};
  margin-bottom: ${theme.spacing.md};
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
`;

const PhotoActions = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
`;

const GeneratedPhotosGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: ${theme.spacing.md};
  margin-top: ${theme.spacing.lg};
  flex: 1;
  min-height: calc(120vh - 400px); /* Увеличиваем высоту области для фото */
  padding: ${theme.spacing.md};
`;

const SelectButton = styled.button<{ $isSelected: boolean }>`
  background: ${props => props.$isSelected 
    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
    : 'rgba(22, 33, 62, 0.3)'};
  border: 1px solid ${props => props.$isSelected 
    ? 'rgba(102, 126, 234, 0.8)' 
    : 'rgba(102, 126, 234, 0.4)'};
  color: ${theme.colors.text.primary};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.fontSize.sm};
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
  
  &:hover {
    background: ${props => props.$isSelected 
      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
      : 'rgba(102, 126, 234, 0.2)'};
    border-color: ${theme.colors.accent.primary};
    transform: translateY(-1px);
  }
`;

const PhotoStatus = styled.span<{ isSelected?: boolean }>`
  font-size: ${theme.fontSize.sm};
  font-weight: 600;
  color: ${props => props.isSelected 
    ? theme.colors.accent.primary 
    : theme.colors.text.secondary};
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
`;

const ActionButtons = styled.div`
  display: flex;
  gap: ${theme.spacing.lg};
  justify-content: center;
  margin-top: ${theme.spacing.xl};
`;

interface CreateCharacterPageProps {
  onBackToMain: () => void;
  onShop: () => void;
  onMyCharacters: () => void;
}

export const CreateCharacterPage: React.FC<CreateCharacterPageProps> = ({
  onBackToMain,
  onShop,
  onMyCharacters
}) => {
  const [formData, setFormData] = useState({
    name: '',
    personality: '',
    situation: '',
    instructions: '',
    style: '',
    appearance: '',
    location: ''
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userInfo, setUserInfo] = useState<{username: string, coins: number, id: number} | null>(null);
  const [isPhotoGenerationExpanded, setIsPhotoGenerationExpanded] = useState(false);
  const [createdCharacterData, setCreatedCharacterData] = useState<any>(null);
  const [customPrompt, setCustomPrompt] = useState('');
  const [largeTextInput, setLargeTextInput] = useState('');
  const [generatedPhotos, setGeneratedPhotos] = useState<any[]>([]);
  const [isGeneratingPhoto, setIsGeneratingPhoto] = useState(false);
  const [generationSettings, setGenerationSettings] = useState<any>(null);
  const [isCharacterCreated, setIsCharacterCreated] = useState(false); // Новое состояние
  const [selectedPhotoForView, setSelectedPhotoForView] = useState<any>(null); // Для модального окна просмотра фото
  const [swiperTranslateX, setSwiperTranslateX] = useState(0); // Для swiper
  const [selectedPhotos, setSelectedPhotos] = useState<string[]>([]); // Выбранные фото для карточки

  // Проверка авторизации
  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('authToken');
      console.log('Auth token:', token ? 'exists' : 'not found');
      
      if (!token) {
        setIsAuthenticated(false);
        setUserInfo(null);
        console.log('No token, setting isAuthenticated to false');
        return;
      }

      const response = await fetch('/auth/me/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('Auth response status:', response.status);

      if (response.ok) {
        const userData = await response.json();
        console.log('User data:', userData);
        setIsAuthenticated(true);
        setUserInfo(userData);
        console.log('Authentication successful, isAuthenticated set to true');
      } else {
        console.log('Auth failed, removing token');
        localStorage.removeItem('authToken');
        setIsAuthenticated(false);
        setUserInfo(null);
      }
    } catch (error) {
      console.error('Auth check error:', error);
      setIsAuthenticated(false);
    }
  };

  useEffect(() => {
    checkAuth();
    loadGenerationSettings();
  }, []);

  // Загружаем настройки генерации из API
  const loadGenerationSettings = async () => {
    try {
      console.log('Загружаем настройки генерации...');
      const response = await fetch('/api/v1/fallback-settings/');
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const settings = await response.json();
        setGenerationSettings(settings);
        console.log('Настройки генерации загружены:', settings);
        console.log('Steps:', settings.steps, 'CFG:', settings.cfg_scale);
      } else {
        console.error('Ошибка загрузки настроек генерации:', response.status);
      }
    } catch (error) {
      console.error('Ошибка загрузки настроек генерации:', error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(null);
    setSuccess(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form submitted!', formData); // Добавляем отладку
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Необходимо войти в систему для создания персонажей');
      }

      // Преобразуем данные в формат UserCharacterCreate
      const requestData = {
        name: formData.name.trim(),
        personality: formData.personality.trim(),
        situation: formData.situation.trim(),
        instructions: formData.instructions.trim(),
        style: formData.style?.trim() || null,
        appearance: formData.appearance?.trim() || null,
        location: formData.location?.trim() || null
      };

      // Проверяем обязательные поля
      if (!requestData.name || !requestData.personality || !requestData.situation || !requestData.instructions) {
        throw new Error('Все обязательные поля должны быть заполнены');
      }

      console.log('Sending request to API...', requestData); // Добавляем отладку
      const response = await fetch('/api/v1/characters/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestData)
      });

      console.log('Response status:', response.status); // Добавляем отладку
      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error:', errorData); // Добавляем отладку
        throw new Error(errorData.detail || 'Ошибка при создании персонажа');
      }

      const result = await response.json();
      console.log('Character created successfully:', result); // Добавляем отладку
      setCreatedCharacterData(result);
      setIsCharacterCreated(true); // Устанавливаем состояние создания персонажа
      setSuccess('Персонаж успешно создан!');
      
      // Расширяем секцию генерации фото
      setTimeout(() => {
        setIsPhotoGenerationExpanded(true);
      }, 1000);

      // Обновляем информацию о пользователе
      await checkAuth();
      
    } catch (err) {
      console.error('Error creating character:', err); // Добавляем отладку
      setError(err instanceof Error ? err.message : 'Ошибка при создании персонажа');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditCharacter = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Editing character...', formData);
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Необходимо войти в систему для редактирования персонажей');
      }

      // Преобразуем данные в формат для редактирования
      const requestData = {
        name: formData.name.trim(),
        personality: formData.personality.trim(),
        situation: formData.situation.trim(),
        instructions: formData.instructions.trim(),
        style: formData.style?.trim() || null,
        appearance: formData.appearance?.trim() || null,
        location: formData.location?.trim() || null
      };

      // Проверяем обязательные поля
      if (!requestData.name || !requestData.personality || !requestData.situation || !requestData.instructions) {
        throw new Error('Все обязательные поля должны быть заполнены');
      }

      console.log('Sending edit request to API...', requestData);
      const response = await fetch(`/api/v1/characters/${createdCharacterData.name}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestData)
      });

      console.log('Edit response status:', response.status);
      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error:', errorData);
        throw new Error(errorData.detail || 'Ошибка при редактировании персонажа');
      }

      const result = await response.json();
      console.log('Character edited successfully:', result);
      setCreatedCharacterData(result);
      setSuccess('Персонаж успешно обновлен!');

      // Обновляем информацию о пользователе
      await checkAuth();
      
    } catch (err) {
      console.error('Error editing character:', err);
      setError(err instanceof Error ? err.message : 'Ошибка при редактировании персонажа');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    window.location.reload();
  };

  // Генерация фото
  const togglePhotoSelection = (photoId: string) => {
    setGeneratedPhotos(prev => 
      prev.map(photo => 
        photo.id === photoId 
          ? { ...photo, isSelected: !photo.isSelected }
          : photo
      )
    );
    
    // Обновляем список выбранных фото
    setSelectedPhotos(prev => {
      if (prev.includes(photoId)) {
        return prev.filter(id => id !== photoId);
      } else {
        // Ограничиваем до 3 фото
        if (prev.length >= 3) {
          return prev;
        }
        return [...prev, photoId];
      }
    });
  };

  // Сохранение выбранных фото
  const saveSelectedPhotos = async () => {
    console.log('Saving selected photos:', selectedPhotos);
    console.log('Created character data:', createdCharacterData);
    
    if (!createdCharacterData || selectedPhotos.length === 0) {
      setError('Нет выбранных фото для сохранения');
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setError('Необходимо войти в систему');
        return;
      }

      const requestData = {
        character_name: createdCharacterData.name,
        photo_ids: selectedPhotos
      };
      
      console.log('Sending request to API:', requestData);

      const response = await fetch('/api/v1/characters/set-main-photos/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestData)
      });

      console.log('API response status:', response.status);
      
      if (response.ok) {
        const result = await response.json();
        console.log('API response data:', result);
        setSuccess('Главные фото успешно сохранены!');
        console.log('Main photos saved:', selectedPhotos);
        
        // Принудительно обновляем главный экран
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
      } else {
        const errorData = await response.json();
        console.error('API error:', errorData);
        setError(`Ошибка сохранения фото: ${errorData.detail || 'Неизвестная ошибка'}`);
      }
    } catch (err) {
      console.error('Error saving main photos:', err);
      setError('Ошибка при сохранении фото');
    }
  };

  const openPhotoModal = (photo: any) => {
    console.log('Opening photo modal for:', photo);
    setSelectedPhotoForView(photo);
  };

  const closePhotoModal = () => {
    setSelectedPhotoForView(null);
  };

  const nextSwiperSlide = () => {
    const maxTranslate = -(generatedPhotos.length - 1) * 100; // Процентное смещение
    setSwiperTranslateX(prev => {
      const newTranslate = prev - 100; // Перемещаем на 100% (следующий слайд)
      return Math.max(newTranslate, maxTranslate);
    });
  };

  const prevSwiperSlide = () => {
    setSwiperTranslateX(prev => {
      const newTranslate = prev + 100; // Перемещаем на 100% (предыдущий слайд)
      return Math.min(newTranslate, 0);
    });
  };

  const generatePhoto = async () => {
    if (!userInfo || userInfo.coins < 30) {
      setError('Недостаточно монет! Нужно 30 монет для генерации фото.');
      return;
    }

    setIsGeneratingPhoto(true);
    setError(null);

    try {
      const token = localStorage.getItem('authToken');
      if (!token) throw new Error('Необходимо войти в систему');

      // Используем кастомный промпт или дефолтный
      const prompt = customPrompt.trim() || `${createdCharacterData?.character_appearance || ''} ${createdCharacterData?.location || ''}`.trim() || 'portrait, high quality, detailed';

      // Используем настройки из API, как в chat.html
      console.log('Generation settings:', generationSettings);
      console.log('Using steps:', generationSettings?.steps || 20);
      console.log('Using cfg_scale:', generationSettings?.cfg_scale || 4);
      
      const requestBody = {
        character: createdCharacterData?.name || 'character',
        prompt: prompt,
        negative_prompt: generationSettings?.negative_prompt || 'blurry, low quality, distorted, bad anatomy',
        width: generationSettings?.width || 512,
        height: generationSettings?.height || 512,
        steps: generationSettings?.steps || 20,
        cfg_scale: generationSettings?.cfg_scale || 4,
        use_default_prompts: false
      };
      
      console.log('Request body:', requestBody);
      
      // Добавляем user_id если пользователь авторизован
      if (token && userInfo) {
        requestBody.user_id = userInfo.id;
      }

      const response = await fetch('/api/v1/generate-image/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка генерации фото');
      }

      const result = await response.json();
      console.log('API Response:', result);
      console.log('Image URL:', result.image_url);
      console.log('Image filename:', result.filename);
      
      // Проверяем URL изображения
      if (!result.image_url) {
        throw new Error('URL изображения не получен от сервера');
      }
      
      // Добавляем новое фото в список
      const filename = result.filename || Date.now().toString();
      const photoId = filename.replace('.png', '').replace('.jpg', ''); // Убираем расширение
      
      const newPhoto = {
        id: photoId,
        url: result.image_url,
        isSelected: false
      };
      
      console.log('New photo object:', newPhoto);
      console.log('Photo URL for display:', newPhoto.url);
      
              setGeneratedPhotos(prev => [...prev, newPhoto]);
              setSuccess('Фото успешно сгенерировано!');
              
              // Сбрасываем позицию swiper если добавили второе фото
              if (generatedPhotos.length === 1) {
                setSwiperTranslateX(0);
              }
      
      // Обновляем информацию о пользователе
      await checkAuth();
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка генерации фото');
    } finally {
      setIsGeneratingPhoto(false);
    }
  };



  // Завершение создания персонажа
  const handleFinish = () => {
    onBackToMain();
  };

  return (
    <MainContainer>
      <CompactSidebar 
        onCreateCharacter={() => {}} // Уже на странице создания
        onShop={onShop}
        onMyCharacters={onMyCharacters}
      />
      
      <ContentArea>
        <Header>
          <BackButton onClick={onBackToMain}>← Назад</BackButton>
          <PageTitle>Создание персонажа</PageTitle>
          <RightSection>
            {userInfo && (
              <UserInfo>
                <UserName>{userInfo.username}</UserName>
                <UserCoins>💰 {userInfo.coins}</UserCoins>
              </UserInfo>
            )}
            {isAuthenticated ? (
              <AuthButton onClick={handleLogout}>Выйти</AuthButton>
            ) : (
              <AuthButton onClick={() => window.location.href = '/auth/login'}>Войти</AuthButton>
            )}
          </RightSection>
        </Header>
        
        <MainContent>
          <Form onSubmit={isCharacterCreated ? handleEditCharacter : handleSubmit}>
            <LeftColumn>
              <ColumnContent>
                <FormGroup>
                <Label htmlFor="name">Имя персонажа:</Label>
                <Input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="Введите имя персонажа..."
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="personality">Личность и характер:</Label>
                <Textarea
                  id="personality"
                  name="personality"
                  value={formData.personality}
                  onChange={handleInputChange}
                  placeholder="Опишите характер и личность персонажа..."
                  rows={4}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="situation">Ролевая ситуация:</Label>
                <Textarea
                  id="situation"
                  name="situation"
                  value={formData.situation}
                  onChange={handleInputChange}
                  placeholder="Опишите ситуацию, в которой находится персонаж..."
                  rows={3}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="instructions">Инструкции для персонажа:</Label>
                <Textarea
                  id="instructions"
                  name="instructions"
                  value={formData.instructions}
                  onChange={handleInputChange}
                  placeholder="Как должен вести себя персонаж, что говорить..."
                  rows={4}
                  required
                />
              </FormGroup>

              <FormGroup>
                <Label htmlFor="style">Стиль ответа (необязательно):</Label>
                <Input
                  type="text"
                  id="style"
                  name="style"
                  value={formData.style}
                  onChange={handleInputChange}
                  placeholder="Например: формальный, дружелюбный, загадочный..."
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="appearance">Внешность (для фото):</Label>
                <Textarea
                  id="appearance"
                  name="appearance"
                  value={formData.appearance}
                  onChange={handleInputChange}
                  placeholder="Опишите внешность персонажа для генерации фото..."
                  rows={3}
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="location">Локация (для фото):</Label>
                <Textarea
                  id="location"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="Опишите локацию персонажа для генерации фото..."
                  rows={3}
                />
              </FormGroup>

              {userInfo && (
                <CoinsDisplay>
                  <CoinsText>Ваши монеты: {userInfo.coins}</CoinsText>
                </CoinsDisplay>
              )}

              {error && <ErrorMessage>{error}</ErrorMessage>}
              {success && <SuccessMessage>{success}</SuccessMessage>}

              <ButtonGroup>
                <Button type="button" $variant="secondary" onClick={onBackToMain} disabled={isLoading}>
                  Отмена
                </Button>
                <Button type="submit" $variant="primary" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <LoadingSpinner /> {isCharacterCreated ? 'Обновление...' : 'Создание...'}
                    </>
                  ) : (
                    isCharacterCreated ? 'Редактировать' : 'Создать персонажа'
                  )}
                </Button>
              </ButtonGroup>
              </ColumnContent>
            </LeftColumn>

            <RightColumn>
              <ColumnContent>
                {/* Секция генерации фото */}
                <PhotoGenerationBox>
                  <PhotoGenerationBoxTitle>Генерация фото для персонажа (30 монет за фото)</PhotoGenerationBoxTitle>
                  <PhotoGenerationDescription>
                    {isCharacterCreated ? 'Генерируйте фото для вашего персонажа' : 'После создания персонажа здесь появится возможность генерировать фото'}
                  </PhotoGenerationDescription>
                  
                  <GenerateSection>
                    <GenerateButton 
                      onClick={generatePhoto} 
                      disabled={isGeneratingPhoto || !userInfo || userInfo.coins < 30 || !isCharacterCreated}
                    >
                      {isGeneratingPhoto ? (
                        <>
                          <LoadingSpinner /> Генерация...
                        </>
                      ) : (
                        'Сгенерировать фото'
                      )}
                    </GenerateButton>
                  </GenerateSection>

                  <LargeTextLabel htmlFor="photo-prompt-unified">
                    Промпт для генерации фото:
                  </LargeTextLabel>
                  <LargeTextInput
                    id="photo-prompt-unified"
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    placeholder={`${createdCharacterData?.character_appearance || ''} ${createdCharacterData?.location || ''}`.trim() || 'portrait, high quality, detailed'}
                  />

                  {/* Область для отображения сгенерированных фото */}
                  {console.log('Generated photos count:', generatedPhotos.length)}
                  {console.log('Generated photos:', generatedPhotos)}
                  {generatedPhotos.length > 0 ? (
                    <FullSizePhotoSlider>
                      {/* Стрелки навигации */}
                      {generatedPhotos.length > 1 && (
                        <>
                          <SliderButton 
                            direction="left" 
                            onClick={prevSwiperSlide}
                            disabled={swiperTranslateX >= 0}
                          >
                            ‹
                          </SliderButton>
                          <SliderButton 
                            direction="right" 
                            onClick={nextSwiperSlide}
                            disabled={swiperTranslateX <= -((generatedPhotos.length - 1) * 100)}
                          >
                            ›
                          </SliderButton>
                        </>
                      )}
                      
                      {/* Контейнер слайдера */}
                      <SliderContainer>
                        <SliderWrapper translateX={swiperTranslateX}>
                          {generatedPhotos.map((photo) => (
                            <SliderSlide key={photo.id}>
                              <FullSizePhoto 
                                src={photo.url} 
                                alt="Generated photo" 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  console.log('Photo clicked:', photo);
                                  openPhotoModal(photo);
                                }}
                                style={{ cursor: 'pointer' }}
                                onError={(e) => {
                                  console.error('Ошибка загрузки изображения:', photo.url);
                                  console.error('Error event:', e);
                                }}
                                onLoad={() => {
                                  console.log('Изображение успешно загружено:', photo.url);
                                }}
                              />
                              <PhotoActions>
                                <SelectButton
                                  onClick={() => togglePhotoSelection(photo.id)}
                                  $isSelected={photo.isSelected}
                                >
                                  {photo.isSelected ? 'Выбрано' : 'Выбрать'}
                                </SelectButton>
                              </PhotoActions>
                            </SliderSlide>
                          ))}
                        </SliderWrapper>
                      </SliderContainer>
                      
                      {/* Описание под слайдером */}
                      <SliderDescription>
                        <DescriptionTitle>Карточка персонажа</DescriptionTitle>
                        <DescriptionText>
                          Вы можете выбрать до 3 фотографий для карточки персонажа. Выбранные фото будут отображаться на главном экране.
                        </DescriptionText>
                        {selectedPhotos.length > 0 && (
                          <SavePhotosButton onClick={saveSelectedPhotos}>
                            Сохранить выбранные фото ({selectedPhotos.length}/3)
                          </SavePhotosButton>
                        )}
                      </SliderDescription>
                    </FullSizePhotoSlider>
                  ) : (
                    <PhotoGenerationPlaceholder>
                      Фотографии будут здесь
                    </PhotoGenerationPlaceholder>
                  )}
                </PhotoGenerationBox>
              </ColumnContent>
            </RightColumn>
          </Form>
        </MainContent>
      </ContentArea>
      
      {/* Модальное окно для просмотра фото в полный размер */}
      {selectedPhotoForView && (
        <PhotoModal onClick={closePhotoModal}>
          <PhotoModalContent onClick={(e) => e.stopPropagation()}>
            <PhotoModalClose onClick={closePhotoModal}>×</PhotoModalClose>
            <PhotoModalImage 
              src={selectedPhotoForView.url} 
              alt="Generated photo full size"
              onLoad={() => console.log('Modal image loaded:', selectedPhotoForView.url)}
            />
          </PhotoModalContent>
        </PhotoModal>
      )}
      
      {/* Отладочная информация */}
      {console.log('Selected photo for view:', selectedPhotoForView)}
    </MainContainer>
  );
};