import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { theme } from '../theme';
import { CompactSidebar } from './CompactSidebar';
import { CharacterCard } from './CharacterCard';
import { EditCharacterModal } from './EditCharacterModal';
import { ConfirmModal } from './ConfirmModal';

const MainContainer = styled.div`
  width: 100vw;
  height: 100vh;
  display: flex;
  position: relative;
  overflow: hidden;
`;

const ContentArea = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: transparent;
  overflow: hidden;
`;

const Header = styled.div`
  background: rgba(102, 126, 234, 0.1);
  backdrop-filter: blur(3px);
  padding: ${theme.spacing.lg} ${theme.spacing.xl};
  border-bottom: 1px solid ${theme.colors.border.accent};
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Title = styled.h1`
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.xl};
  font-weight: 700;
  margin: 0;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.lg};
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
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
  
  &:hover {
    transform: scale(1.05);
    border-image: linear-gradient(45deg, #8b5cf6 50%, #7f1d1d 50%) 1;
    color: ${theme.colors.text.primary};
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

const CharactersGrid = styled.div`
  flex: 1;
  padding: ${theme.spacing.lg};
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: ${theme.spacing.md};
  align-content: start;
`;

const EmptyState = styled.div`
  grid-column: 1 / -1;
  text-align: center;
  padding: 4rem 2rem;
  color: ${theme.colors.text.secondary};
`;

const EmptyTitle = styled.h3`
  color: ${theme.colors.text.primary};
  font-size: ${theme.fontSize.lg};
  margin-bottom: ${theme.spacing.md};
`;

const EmptyDescription = styled.p`
  color: ${theme.colors.text.secondary};
  font-size: ${theme.fontSize.md};
  margin-bottom: ${theme.spacing.lg};
`;

const CreateButton = styled.button`
  background: ${theme.colors.gradients.button};
  color: ${theme.colors.text.primary};
  border: none;
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.fontSize.md};
  font-weight: 600;
  cursor: pointer;
  transition: ${theme.transition.fast};
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${theme.colors.shadow.button};
  }
`;

interface Character {
  id: string;
  name: string;
  description: string;
  avatar: string;
  photos?: string[];
  tags: string[];
  author: string;
  likes: number;
  views: number;
  comments: number;
}

interface MyCharactersPageProps {
  onBackToMain: () => void;
  onCreateCharacter: () => void;
  onShop: () => void;
}

export const MyCharactersPage: React.FC<MyCharactersPageProps> = ({
  onBackToMain,
  onCreateCharacter,
  onShop
}) => {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userInfo, setUserInfo] = useState<{username: string, coins: number} | null>(null);
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [deletingCharacter, setDeletingCharacter] = useState<Character | null>(null);
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);

  // Загрузка персонажей пользователя
  const loadMyCharacters = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('authToken');
      if (!token) {
        setIsAuthenticated(false);
        return;
      }

      const response = await fetch('/api/v1/characters/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const charactersData = await response.json();
        // Фильтруем только персонажей текущего пользователя
        const myCharacters = charactersData.filter((char: any) => char.user_id);
        
        const formattedCharacters: Character[] = myCharacters.map((char: any) => ({
          id: char.id.toString(),
          name: char.name,
          description: char.character_appearance || 'No description available',
          avatar: char.name.charAt(0).toUpperCase(),
          photos: [],
          tags: ['My Character'],
          author: 'Me',
          likes: 0,
          views: 0,
          comments: 0
        }));
        
        setCharacters(formattedCharacters);
        setIsAuthenticated(true);
      } else {
        console.error('Failed to load characters:', response.status);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Error loading characters:', error);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Проверка авторизации
  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setIsAuthenticated(false);
        return;
      }

      const response = await fetch('/auth/me/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUserInfo({
          username: userData.email,
          coins: userData.coins
        });
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
        localStorage.removeItem('authToken');
      }
    } catch (error) {
      console.error('Auth check error:', error);
      setIsAuthenticated(false);
    }
  };

  // Обработчики
  const handleCardClick = (character: Character) => {
    // Если показываются кнопки редактирования, не открываем модальное окно при клике на карточку
    // Кнопки редактирования будут обрабатывать клики
    return;
  };

  const handleEditCharacter = (character: Character) => {
    setEditingCharacter(character);
    setIsEditModalOpen(true);
  };

  const handleDeleteCharacter = async (character: Character) => {
    console.log('Delete character clicked:', character.name);
    setDeletingCharacter(character);
    setIsConfirmModalOpen(true);
  };

  const confirmDelete = async () => {
    if (!deletingCharacter) return;

    try {
      const token = localStorage.getItem('authToken');
      if (!token) return;

      console.log('Sending delete request for:', deletingCharacter.name);

      const response = await fetch(`/api/v1/characters/${deletingCharacter.name}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('Delete response status:', response.status);

      if (response.ok) {
        // Перезагружаем список персонажей
        await loadMyCharacters();
        await checkAuth(); // Обновляем информацию о пользователе
        console.log('Character deleted successfully');
      } else {
        const errorData = await response.json();
        console.error('Delete error:', errorData);
        alert(`Ошибка удаления: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Delete character error:', error);
      alert('Ошибка при удалении персонажа');
    } finally {
      setIsConfirmModalOpen(false);
      setDeletingCharacter(null);
    }
  };

  const cancelDelete = () => {
    setIsConfirmModalOpen(false);
    setDeletingCharacter(null);
  };

  const handleCharacterUpdated = async () => {
    // Перезагружаем список персонажей после редактирования
    await loadMyCharacters();
    await checkAuth();
  };

  const handleAddPhoto = async (character: Character) => {
    console.log('Add photo clicked for character:', character.name);
    // Здесь можно добавить логику для загрузки фото
    // Пока что просто показываем alert
    alert(`Добавление фото для персонажа "${character.name}" (30 💎)`);
  };

  const handleLogout = () => {
    // Удаляем токен из localStorage
    localStorage.removeItem('authToken');
    // Перезагружаем страницу для обновления состояния
    window.location.reload();
  };

  // Загрузка данных при монтировании
  useEffect(() => {
    checkAuth();
    loadMyCharacters();
  }, []);

  if (!isAuthenticated) {
    return (
      <MainContainer>
        <CompactSidebar 
          onCreateCharacter={onCreateCharacter}
          onShop={onShop}
          onMyCharacters={() => {}}
        />
        <ContentArea>
          <Header>
            <Title>Мои персонажи</Title>
            <RightSection>
              <EmptyState>
                <EmptyTitle>Необходима авторизация</EmptyTitle>
                <EmptyDescription>
                  Войдите в систему, чтобы просматривать и редактировать своих персонажей
                </EmptyDescription>
              </EmptyState>
            </RightSection>
          </Header>
        </ContentArea>
      </MainContainer>
    );
  }

  return (
    <MainContainer>
      <CompactSidebar 
        onCreateCharacter={onCreateCharacter}
        onShop={onShop}
        onMyCharacters={() => {}}
      />
      
      <ContentArea>
        <Header>
          <Title>Мои персонажи</Title>
          <RightSection>
            <UserInfo>
              <UserName>{userInfo?.username}</UserName>
              <UserCoins>💰 {userInfo?.coins}</UserCoins>
            </UserInfo>
            <AuthButton onClick={handleLogout}>Выйти</AuthButton>
          </RightSection>
        </Header>
        
        <CharactersGrid>
          {isLoading ? (
            <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '2rem', color: '#a8a8a8' }}>
              Загрузка персонажей...
            </div>
          ) : characters.length === 0 ? (
            <EmptyState>
              <EmptyTitle>У вас пока нет персонажей</EmptyTitle>
              <EmptyDescription>
                Создайте своего первого персонажа, чтобы начать общение
              </EmptyDescription>
              <CreateButton onClick={onCreateCharacter}>
                Создать персонажа
              </CreateButton>
            </EmptyState>
          ) : (
            characters.map((character) => {
              console.log('Rendering character:', character.name, 'with edit button:', true);
              return (
                <CharacterCard
                  key={character.id}
                  character={character}
                  onClick={() => handleCardClick(character)}
                  showEditButton={true}
                  onEdit={() => {
                    console.log('Edit handler called for:', character.name);
                    handleEditCharacter(character);
                  }}
                  onDelete={() => {
                    console.log('Delete handler called for:', character.name);
                    handleDeleteCharacter(character);
                  }}
                  onAddPhoto={() => {
                    console.log('Add photo handler called for:', character.name);
                    handleAddPhoto(character);
                  }}
                />
              );
            })
          )}
        </CharactersGrid>
      </ContentArea>
      
      {editingCharacter && (
        <EditCharacterModal
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setEditingCharacter(null);
          }}
          character={editingCharacter}
          userCoins={userInfo?.coins || 0}
          onCharacterUpdated={handleCharacterUpdated}
        />
      )}
      
      <ConfirmModal
        isOpen={isConfirmModalOpen}
        title="Подтвердите действие"
        message={`Вы уверены, что хотите удалить персонажа "${deletingCharacter?.name}"?`}
        confirmText="Удалить"
        cancelText="Отмена"
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </MainContainer>
  );
};
