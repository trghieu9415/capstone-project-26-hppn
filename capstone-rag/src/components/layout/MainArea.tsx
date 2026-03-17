import React from 'react';
import { ChatInterface } from '../features/chat/ChatInterface';

export const MainArea: React.FC = () => {
  return (
    <main className="flex-1 flex flex-col h-full overflow-hidden">
      <ChatInterface />
    </main>
  );
};
