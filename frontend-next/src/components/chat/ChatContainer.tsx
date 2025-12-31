'use client';

// ============================================================
// Chat Container Component
// ============================================================

import { useEffect } from 'react';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import { useChatStore } from '@/lib/stores';

interface ChatContainerProps {
  conversationId?: string;
}

export function ChatContainer({ conversationId }: ChatContainerProps) {
  const {
    messages,
    isStreaming,
    selectConversation,
    sendMessage,
    stopStreaming,
    clearMessages,
  } = useChatStore();

  useEffect(() => {
    if (conversationId) {
      selectConversation(conversationId);
    } else {
      clearMessages();
    }
  }, [conversationId, selectConversation, clearMessages]);

  const handleSend = async (content: string, images?: string[]) => {
    await sendMessage(content, images);
  };

  const handleStop = () => {
    stopStreaming();
  };

  return (
    <div className="flex h-full flex-col">
      <MessageList messages={messages} />
      <InputArea
        onSend={handleSend}
        onStop={handleStop}
        isStreaming={isStreaming}
      />
    </div>
  );
}
