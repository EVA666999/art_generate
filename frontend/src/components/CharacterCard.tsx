import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { theme } from '../theme';
import ElectricBorder from './ElectricBorder';

const CardContainer = styled.div`
  background: rgba(22, 33, 62, 0.3); /* Очень прозрачный */
  backdrop-filter: blur(5px);
  border-radius: ${theme.borderRadius.lg};
  padding: 0; /* Убираем padding чтобы фото занимало всю карточку */
  box-shadow: ${theme.colors.shadow.message};
  transition: ${theme.transition.fast};
  cursor: pointer;
  position: relative;
  overflow: hidden;
  height: 300px; /* Фиксированная высота карточки */
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${theme.colors.shadow.glow};
  }
`;

const PhotoBackground = styled.div<{ $imageUrl: string }>`
  width: 100%;
  height: 100%;
  background-image: url(${props => props.$imageUrl});
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
`;

const ActionButtons = styled.div`
  position: absolute;
  top: ${theme.spacing.sm};
  right: ${theme.spacing.sm};
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
  opacity: 0; /* Возвращаем к нормальному состоянию */
  transform: translateY(-10px); /* Возвращаем анимацию */
  transition: all ${theme.transition.fast};
  pointer-events: auto; /* Включаем клики для кнопок */
  z-index: 10; /* Поверх всех элементов */
  
  ${CardContainer}:hover & {
    opacity: 1;
    transform: translateY(0);
  }
`;

const ActionButton = styled.button<{ variant?: 'edit' | 'delete' }>`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
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
  white-space: nowrap;
  min-width: 80px;
  z-index: 11;
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
  right: -10px;
  top: 50%;
  transform: translateY(-50%) translateX(100%);
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

const ActionButtonWithTooltip = styled.div`
  position: relative;
  
  &:hover ${Tooltip} {
    opacity: 1;
  }
`;

const ContentOverlay = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  padding: ${theme.spacing.md};
  z-index: 2;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
`;

const SlideShowContainer = styled.div`
  width: 100%;
  height: 100%;
  position: relative;
`;

const SlideImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
  opacity: 0;
  transition: opacity 0.5s ease-in-out;
  
  &.active {
    opacity: 1;
  }
`;

const SlideDots = styled.div`
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 4px;
  z-index: 3;
`;

const Dot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  transition: background 0.3s ease;
  
  &.active {
    background: rgba(255, 255, 255, 0.9);
  }
`;

const CharacterAvatar = styled.div`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: ${theme.colors.gradients.primary};
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: ${theme.spacing.sm};
  position: relative;
  overflow: hidden;
  font-size: ${theme.fontSize.xl};
  font-weight: bold;
  color: white;
`;

const CharacterName = styled.h3`
  font-size: ${theme.fontSize.lg};
  font-weight: 600;
  color: white;
  margin-bottom: ${theme.spacing.xs};
  line-height: 1.3;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
`;

const CharacterDescription = styled.p`
  font-size: ${theme.fontSize.sm};
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.4;
  margin-bottom: ${theme.spacing.sm};
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
`;

const TagsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${theme.spacing.xs};
  margin-bottom: ${theme.spacing.xs};
`;

const Tag = styled.span`
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 2px 6px;
  border-radius: ${theme.borderRadius.sm};
  font-size: ${theme.fontSize.xs};
  backdrop-filter: blur(5px);
`;

const StatsContainer = styled.div`
  display: flex;
  justify-content: space-between;
  width: 100%;
`;

const StatItem = styled.div`
  display: flex;
  align-items: center;
  gap: 2px;
  color: rgba(255, 255, 255, 0.9);
  font-size: ${theme.fontSize.xs};
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
`;

const StatIcon = styled.span`
  font-size: ${theme.fontSize.sm};
  color: white;
`;

const Author = styled.div`
  font-size: ${theme.fontSize.xs};
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: ${theme.spacing.xs};
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
`;

interface Character {
  id: string;
  name: string;
  description: string;
  avatar: string;
  photos?: string[]; // Массив фотографий для слайд-шоу
  tags: string[];
  author: string;
  likes: number;
  views: number;
  comments: number;
}

interface CharacterCardProps {
  character: Character;
  onClick: (character: Character) => void;
  isAuthenticated?: boolean;
  showEditButton?: boolean;
  onEdit?: (character: Character) => void;
  onDelete?: (character: Character) => void;
  onAddPhoto?: (character: Character) => void; // New prop for adding photos
}

// Компонент слайд-шоу
const SlideShow: React.FC<{ photos: string[]; characterName: string }> = ({ photos, characterName }) => {
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    if (photos.length <= 1) return;
    
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % photos.length);
    }, 3000); // Меняем слайд каждые 3 секунды

    return () => clearInterval(interval);
  }, [photos.length]);

  if (!photos || photos.length === 0) {
    return (
      <PhotoBackground $imageUrl="" />
    );
  }

  return (
    <>
      <PhotoBackground $imageUrl={photos[currentSlide]} />
      {photos.length > 1 && (
        <SlideDots>
          {photos.map((_, index) => (
            <Dot
              key={index}
              className={index === currentSlide ? 'active' : ''}
            />
          ))}
        </SlideDots>
      )}
    </>
  );
};
export const CharacterCard: React.FC<CharacterCardProps> = ({ 
  character, 
  onClick, 
  showEditButton = false, 
  onEdit, 
  onDelete,
  onAddPhoto // New prop
}) => {
  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  return (
    <ElectricBorder
      color="#4a148c"
      speed={1}
      chaos={0.3}
      thickness={2}
      style={{ borderRadius: 16 }}
    >
      <CardContainer onClick={() => onClick(character)}>
        <SlideShow photos={character.photos || []} characterName={character.name} />
        
        {showEditButton && (
          <ActionButtons>
            {onAddPhoto && (
              <ActionButtonWithTooltip>
                <ActionButton 
                  variant="edit"
                  onClick={(e) => {
                    e.stopPropagation();
                    console.log('Add photo button clicked for character:', character.name);
                    onAddPhoto(character);
                  }}
                >
                  Фото
                </ActionButton>
                <Tooltip>Добавить фото (30 💎)</Tooltip>
              </ActionButtonWithTooltip>
            )}
            {onEdit && (
              <ActionButtonWithTooltip>
                <ActionButton 
                  variant="edit"
                  onClick={(e) => {
                    e.stopPropagation();
                    console.log('Edit button clicked for character:', character.name);
                    onEdit(character);
                  }}
                >
                  Редактировать
                </ActionButton>
                <Tooltip>Редактировать персонажа</Tooltip>
              </ActionButtonWithTooltip>
            )}
            {onDelete && (
              <ActionButtonWithTooltip>
                <ActionButton 
                  variant="delete"
                  onClick={(e) => {
                    e.stopPropagation();
                    console.log('Delete button clicked for character:', character.name);
                    onDelete(character);
                  }}
                >
                  Удалить
                </ActionButton>
                <Tooltip>Удалить персонажа</Tooltip>
              </ActionButtonWithTooltip>
            )}
          </ActionButtons>
        )}
        
        <ContentOverlay>
          <CharacterName>{character.name}</CharacterName>
          <CharacterDescription>{character.description}</CharacterDescription>
          
          <TagsContainer>
            {character.tags.slice(0, 2).map((tag, index) => (
              <Tag key={index}>{tag}</Tag>
            ))}
            {character.tags.length > 2 && (
              <Tag>+{character.tags.length - 2}</Tag>
            )}
          </TagsContainer>
          
          <Author>@{character.author}</Author>
          
          <StatsContainer>
            <StatItem>
              <StatIcon>*</StatIcon>
              {formatNumber(character.likes)}
            </StatItem>
            <StatItem>
              <StatIcon>V</StatIcon>
              {formatNumber(character.views)}
            </StatItem>
            <StatItem>
              <StatIcon>C</StatIcon>
              {character.comments}
            </StatItem>
          </StatsContainer>
        </ContentOverlay>
      </CardContainer>
    </ElectricBorder>
  );
};
