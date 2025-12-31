'use client';

// ============================================================
// Message Bubble Component
// ============================================================

import { useState } from 'react';
import { Copy, Check, RotateCcw, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { Message, ToolCall } from '@/lib/types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageBubbleProps {
  message: Message;
  onRegenerate?: () => void;
}

export function MessageBubble({ message, onRegenerate }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const [toolsExpanded, setToolsExpanded] = useState(false);

  const isUser = message.role === 'user';

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={cn(
        'group flex w-full gap-4 py-4',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      {/* Avatar for Assistant */}
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
          <span className="text-sm font-medium">AI</span>
        </div>
      )}

      <div
        className={cn(
          'flex max-w-[80%] flex-col gap-2',
          isUser ? 'items-end' : 'items-start'
        )}
      >
        {/* User Images */}
        {isUser && message.images && message.images.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {message.images.map((img, idx) => (
              <img
                key={idx}
                src={img.startsWith('data:') ? img : `data:image/jpeg;base64,${img}`}
                alt={`Uploaded ${idx + 1}`}
                className="max-h-48 rounded-lg object-cover"
              />
            ))}
          </div>
        )}

        {/* Message Content */}
        <div
          className={cn(
            'rounded-2xl px-4 py-3',
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-foreground'
          )}
        >
          {message.isStreaming && !message.content ? (
            <div className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Thinking...</span>
            </div>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Tool Calls */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="w-full">
            <Button
              variant="ghost"
              size="sm"
              className="flex items-center gap-1 text-xs text-muted-foreground"
              onClick={() => setToolsExpanded(!toolsExpanded)}
            >
              {toolsExpanded ? (
                <ChevronUp className="h-3 w-3" />
              ) : (
                <ChevronDown className="h-3 w-3" />
              )}
              {message.toolCalls.length} tool{message.toolCalls.length > 1 ? 's' : ''} used
            </Button>

            {toolsExpanded && (
              <div className="mt-2 space-y-2">
                {message.toolCalls.map((tool) => (
                  <ToolCallItem key={tool.id} toolCall={tool} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        {!isUser && !message.isStreaming && (
          <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleCopy}>
              {copied ? (
                <Check className="h-3 w-3 text-green-500" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>
            {onRegenerate && (
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onRegenerate}>
                <RotateCcw className="h-3 w-3" />
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Avatar for User */}
      {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-foreground">
          <span className="text-sm font-medium">U</span>
        </div>
      )}
    </div>
  );
}

// Tool Call Item Component
function ToolCallItem({ toolCall }: { toolCall: ToolCall }) {
  const [expanded, setExpanded] = useState(false);

  const statusIcon = {
    running: <Loader2 className="h-3 w-3 animate-spin text-blue-500" />,
    success: <Check className="h-3 w-3 text-green-500" />,
    error: <span className="h-3 w-3 text-red-500">✕</span>,
  };

  return (
    <div className="rounded-lg border bg-card p-3">
      <div
        className="flex cursor-pointer items-center justify-between"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2">
          {statusIcon[toolCall.status]}
          <span className="text-sm font-medium">{toolCall.name}</span>
          {toolCall.duration && (
            <span className="text-xs text-muted-foreground">
              ({(toolCall.duration / 1000).toFixed(1)}s)
            </span>
          )}
        </div>
        {expanded ? (
          <ChevronUp className="h-4 w-4" />
        ) : (
          <ChevronDown className="h-4 w-4" />
        )}
      </div>

      {expanded && toolCall.output && (
        <div className="mt-2 max-h-48 overflow-auto rounded bg-muted p-2">
          <pre className="text-xs whitespace-pre-wrap">{toolCall.output}</pre>
        </div>
      )}
    </div>
  );
}
