'use client';

// ============================================================
// Chat Page - Specific Conversation
// ============================================================

import { ChatContainer } from '@/components/chat';
import { use } from 'react';

interface ChatIdPageProps {
  params: Promise<{ id: string }>;
}

export default function ChatIdPage({ params }: ChatIdPageProps) {
  const { id } = use(params);
  return <ChatContainer conversationId={id} />;
}
