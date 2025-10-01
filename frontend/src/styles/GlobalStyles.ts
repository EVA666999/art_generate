import { createGlobalStyle } from 'styled-components';
import { theme } from '../theme';

export const GlobalStyles = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  html {
    font-size: 16px;
    scroll-behavior: smooth;
    height: 100%;
    width: 100%;
  }

  body {
    font-family: 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
    background-image: url('/maxresdefault.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
    color: ${theme.colors.text.primary};
    line-height: 1.6;
    height: 100vh; /* Используем viewport height */
    width: 100vw; /* Используем viewport width */
    overflow: hidden; /* Убираем скролл на body */
    margin: 0;
    padding: 0;
  }

  #root {
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  /* Стилизация скроллбара */
  ::-webkit-scrollbar {
    width: 8px;
  }

  ::-webkit-scrollbar-track {
    background: ${theme.colors.background.secondary};
    border-radius: ${theme.borderRadius.md};
  }

  ::-webkit-scrollbar-thumb {
    background: ${theme.colors.gradients.button};
    border-radius: ${theme.borderRadius.md};
    transition: ${theme.transition.fast};
  }

  ::-webkit-scrollbar-thumb:hover {
    background: ${theme.colors.gradients.buttonHover};
  }

  /* Стили для выделения текста */
  ::selection {
    background: ${theme.colors.accent.primary};
    color: ${theme.colors.text.primary};
  }

  /* Стили для фокуса */
  :focus {
    outline: 2px solid ${theme.colors.accent.primary};
    outline-offset: 2px;
  }

  /* Стили для кнопок */
  button {
    cursor: pointer;
    border: none;
    background: none;
    font-family: inherit;
    transition: ${theme.transition.fast};
  }

  button:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }

  /* Стили для инпутов */
  input, textarea {
    font-family: inherit;
    border: none;
    outline: none;
    background: transparent;
    color: inherit;
  }

  input::placeholder, textarea::placeholder {
    color: ${theme.colors.text.muted};
  }

  /* Стили для ссылок */
  a {
    color: ${theme.colors.accent.primary};
    text-decoration: none;
    transition: ${theme.transition.fast};
  }

  a:hover {
    color: ${theme.colors.accent.secondary};
  }

  /* Анимации */
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes slideIn {
    from {
      transform: translateX(-100%);
    }
    to {
      transform: translateX(0);
    }
  }

  @keyframes glow {
    0%, 100% {
      box-shadow: ${theme.colors.shadow.glow};
    }
    50% {
      box-shadow: 0 0 30px rgba(232, 121, 249, 0.8);
    }
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.7;
    }
  }

  /* Утилитарные классы */
  .fade-in {
    animation: fadeIn 0.5s ease-out;
  }

  .slide-in {
    animation: slideIn 0.3s ease-out;
  }

  .glow {
    animation: glow 2s ease-in-out infinite;
  }

  .pulse {
    animation: pulse 1.5s ease-in-out infinite;
  }

  /* Стили для модальных окон */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: ${theme.zIndex.modal};
  }

  .modal-content {
    background: ${theme.colors.gradients.card};
    border-radius: ${theme.borderRadius.xl};
    padding: ${theme.spacing.xl};
    box-shadow: ${theme.colors.shadow.card};
    border: 1px solid ${theme.colors.border.accent};
    max-width: 90vw;
    max-height: 90vh;
    overflow-y: auto;
  }

  /* Стили для уведомлений */
  .toast {
    position: fixed;
    top: ${theme.spacing.xl};
    right: ${theme.spacing.xl};
    background: ${theme.colors.gradients.card};
    color: ${theme.colors.text.primary};
    padding: ${theme.spacing.md} ${theme.spacing.lg};
    border-radius: ${theme.borderRadius.lg};
    box-shadow: ${theme.colors.shadow.card};
    border: 1px solid ${theme.colors.border.accent};
    z-index: ${theme.zIndex.toast};
    animation: fadeIn 0.3s ease-out;
  }

  /* Адаптивность */
  @media (max-width: 1024px) {
    #root {
      flex-direction: column;
    }
  }

  @media (max-width: 768px) {
    body {
      font-size: 14px;
    }
    
    .modal-content {
      margin: ${theme.spacing.md};
      padding: ${theme.spacing.lg};
    }
  }

  @media (max-width: 480px) {
    body {
      font-size: 13px;
    }
  }
`;
