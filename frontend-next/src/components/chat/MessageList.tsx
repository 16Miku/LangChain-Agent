'use client';

// ============================================================
// Message List Component
// ============================================================

import { useEffect, useRef } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageBubble } from './MessageBubble';
import type { Message } from '@/lib/types';
import { MessageSquare } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
  onRegenerate?: (messageId: string) => void;
}

export function MessageList({ messages, onRegenerate }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom on new messages
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-4 p-8 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
          <MessageSquare className="h-8 w-8 text-muted-foreground" />
        </div>
        <div className="space-y-2">
          <h3 className="text-xl font-semibold">Start a Conversation</h3>
          <p className="text-sm text-muted-foreground max-w-md">
            Ask me anything! I can help with research, code execution, data analysis,
            web search, and much more.
          </p>
        </div>
        <div className="flex flex-wrap justify-center gap-2 max-w-lg">
          {[
            'Analyze a CSV file',
            'Search for research papers',
            'Write Python code',
            'Generate a chart',
          ].map((suggestion) => (
            <button
              key={suggestion}
              className="rounded-full border bg-card px-4 py-2 text-sm hover:bg-accent transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <ScrollArea ref={scrollRef} className="flex-1 px-4">
      <div className="mx-auto max-w-3xl py-4">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onRegenerate={
              message.role === 'assistant' && onRegenerate
                ? () => onRegenerate(message.id)
                : undefined
            }
          />
        ))}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
