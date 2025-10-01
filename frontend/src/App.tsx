import React, { useState } from 'react';
import styled from 'styled-components';
import { GlobalStyles } from './styles/GlobalStyles';
import { MainPage } from './components/MainPage';
import { ChatContainer } from './components/ChatContainer';
import { MyCharactersPage } from './components/MyCharactersPage';
import { CreateCharacterPage } from './components/CreateCharacterPage';
import { theme } from './theme';

const AppContainer = styled.div`
  width: 100vw;
  height: 100vh;
  display: flex;
  overflow: hidden;
  position: relative;
`;

function App() {
  const [currentPage, setCurrentPage] = useState<'main' | 'chat' | 'my-characters' | 'create-character'>('main');
  const [selectedCharacter, setSelectedCharacter] = useState<any>(null);

  const handleCharacterSelect = (character: any) => {
    setSelectedCharacter(character);
    setCurrentPage('chat');
  };

  const handleBackToMain = () => {
    setCurrentPage('main');
    setSelectedCharacter(null);
  };

  const handleMyCharacters = () => {
    setCurrentPage('my-characters');
  };

  const handleCreateCharacter = () => {
    setCurrentPage('create-character');
  };

  const handleShop = () => {
    setCurrentPage('main');
    // Здесь можно добавить логику для автоматического открытия магазина
  };

  return (
    <>
      <GlobalStyles />
      <AppContainer>
        {currentPage === 'main' ? (
          <MainPage 
            onCharacterSelect={handleCharacterSelect} 
            onMyCharacters={handleMyCharacters}
            onCreateCharacter={handleCreateCharacter}
          />
        ) : currentPage === 'chat' ? (
          <ChatContainer onBackToMain={handleBackToMain} />
        ) : currentPage === 'my-characters' ? (
          <MyCharactersPage
            onBackToMain={handleBackToMain}
            onCreateCharacter={handleCreateCharacter}
            onShop={handleShop}
          />
        ) : (
          <CreateCharacterPage
            onBackToMain={handleBackToMain}
            onCreateCharacter={handleCreateCharacter}
            onShop={handleShop}
            onMyCharacters={handleMyCharacters}
          />
        )}
      </AppContainer>
    </>
  );
}

export default App;