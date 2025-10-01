import React from 'react';
import styled, { keyframes } from 'styled-components';
import { theme } from '../theme';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

const SpinnerContainer = styled.div<{ $size?: 'sm' | 'md' | 'lg' }>`
  display: inline-block;
  width: ${props => {
    switch (props.$size) {
      case 'sm': return '20px';
      case 'lg': return '40px';
      default: return '30px';
    }
  }};
  height: ${props => {
    switch (props.$size) {
      case 'sm': return '20px';
      case 'lg': return '40px';
      default: return '30px';
    }
  }};
  border: 3px solid rgba(139, 92, 246, 0.2);
  border-radius: 50%;
  border-top-color: ${theme.colors.accent.primary};
  animation: ${spin} 1s ease-in-out infinite;
`;

const PulseContainer = styled.div`
  display: flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
`;

const PulseDot = styled.div<{ $delay: number }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${theme.colors.accent.primary};
  animation: ${pulse} 1.4s ease-in-out infinite;
  animation-delay: ${props => props.$delay}s;
`;

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'spinner' | 'dots';
  text?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  variant = 'spinner',
  text 
}) => {
  if (variant === 'dots') {
    return (
      <PulseContainer>
        <PulseDot $delay={0} />
        <PulseDot $delay={0.2} />
        <PulseDot $delay={0.4} />
        {text && <span style={{ marginLeft: theme.spacing.md, color: theme.colors.text.muted }}>{text}</span>}
      </PulseContainer>
    );
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.md }}>
      <SpinnerContainer $size={size} />
      {text && <span style={{ color: theme.colors.text.muted }}>{text}</span>}
    </div>
  );
};
