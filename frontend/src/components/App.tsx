import React, { useState } from 'react';
import styled from 'styled-components';
import { theme } from '../theme';
import { MainPage } from './MainPage';
import { ChatContainer } from './ChatContainer';

const AppContainer = styled.div`
  width: 100vw;
  height: 100vh;
  overflow: hidden;
`;

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<'main' | 'chat'>('main');
  const [selectedCharacter, setSelectedCharacter] = useState<any>(null);

  const handleCharacterSelect = (character: any) => {
    setSelectedCharacter(character);
    setCurrentPage('chat');
  };

  const handleBackToMain = () => {
    setCurrentPage('main');
    setSelectedCharacter(null);
  };

  return (
    <AppContainer>
      {currentPage === 'main' ? (
        <MainPage />
      ) : (
        <ChatContainer />
      )}
    </AppContainer>
  );
};
