'use client';

// ============================================================
// Message Bubble Component - Enhanced with CodeBlock & ToolCallPanel
// ============================================================

import { useState, useMemo, useRef, useCallback, useEffect } from 'react';
import { Copy, Check, RotateCcw, Loader2, Volume2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { Message } from '@/lib/types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { CodeBlock, InlineCode } from './CodeBlock';
import { ToolCallPanel } from './ToolCallPanel';
import { CitationPanel, type CitationInfo } from './CitationPanel';
import { PlayButton, AudioPlayer } from '@/components/voice';
import { synthesizeSpeech } from '@/lib/api/voice';

interface MessageBubbleProps {
  message: Message;
  onRegenerate?: () => void;
}

export function MessageBubble({ message, onRegenerate }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);

  const isUser = message.role === 'user';
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // 生成语音
  const handleGenerateSpeech = useCallback(async () => {
    if (audioUrl) return; // 已有音频

    setIsGeneratingAudio(true);
    try {
      const url = await synthesizeSpeech({
        text: message.content,
      });
      setAudioUrl(url);
    } catch (error) {
      console.error('生成语音失败:', error);
    } finally {
      setIsGeneratingAudio(false);
    }
  }, [audioUrl, message.content]);

  // 播放/暂停音频
  const handleToggleAudio = useCallback(() => {
    if (audioRef.current) {
      if (isPlayingAudio) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlayingAudio(!isPlayingAudio);
    }
  }, [isPlayingAudio]);

  // 清理音频 URL
  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  // Custom components for ReactMarkdown
  const markdownComponents = useMemo(
    () => ({
      // Code block and inline code
      code: ({
        inline,
        className,
        children,
        ...props
      }: {
        inline?: boolean;
        className?: string;
        children?: React.ReactNode;
      }) => {
        const match = /language-(\w+)/.exec(className || '');
        const language = match ? match[1] : 'plaintext';
        const codeString = String(children).replace(/\n$/, '');

        if (!inline && codeString.includes('\n')) {
          return <CodeBlock code={codeString} language={language} className="my-4" />;
        }

        return <InlineCode>{children}</InlineCode>;
      },

      // Enhanced pre handling
      pre: ({ children }: { children?: React.ReactNode }) => {
        return <>{children}</>;
      },

      // Images - handle both URLs and data URLs (base64)
      // 使用 React.ImgHTMLAttributes 类型来匹配 ReactMarkdown 要求
      img: (props: React.ImgHTMLAttributes<HTMLImageElement>) => {
        const { src, alt, ...rest } = props;
        if (!src || typeof src !== 'string') return null;
        return (
          <img
            src={src}
            alt={alt || 'Image'}
            className="my-3 max-w-full rounded-lg border"
            loading="lazy"
            {...rest}
          />
        );
      },

      // Links
      a: ({ href, children }: { href?: string; children?: React.ReactNode }) => (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary underline hover:no-underline"
        >
          {children}
        </a>
      ),

      // Tables
      table: ({ children }: { children?: React.ReactNode }) => (
        <div className="my-4 overflow-x-auto">
          <table className="min-w-full border-collapse border border-border">
            {children}
          </table>
        </div>
      ),
      th: ({ children }: { children?: React.ReactNode }) => (
        <th className="border border-border bg-muted px-3 py-2 text-left font-medium">
          {children}
        </th>
      ),
      td: ({ children }: { children?: React.ReactNode }) => (
        <td className="border border-border px-3 py-2">{children}</td>
      ),

      // Lists
      ul: ({ children }: { children?: React.ReactNode }) => (
        <ul className="my-2 ml-4 list-disc space-y-1">{children}</ul>
      ),
      ol: ({ children }: { children?: React.ReactNode }) => (
        <ol className="my-2 ml-4 list-decimal space-y-1">{children}</ol>
      ),

      // Headings
      h1: ({ children }: { children?: React.ReactNode }) => (
        <h1 className="mb-4 mt-6 text-2xl font-bold">{children}</h1>
      ),
      h2: ({ children }: { children?: React.ReactNode }) => (
        <h2 className="mb-3 mt-5 text-xl font-bold">{children}</h2>
      ),
      h3: ({ children }: { children?: React.ReactNode }) => (
        <h3 className="mb-2 mt-4 text-lg font-bold">{children}</h3>
      ),

      // Blockquote
      blockquote: ({ children }: { children?: React.ReactNode }) => (
        <blockquote className="my-4 border-l-4 border-primary/50 pl-4 italic text-muted-foreground">
          {children}
        </blockquote>
      ),

      // Paragraph
      p: ({ children }: { children?: React.ReactNode }) => (
        <p className="mb-3 last:mb-0">{children}</p>
      ),
    }),
    []
  );

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
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={markdownComponents}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Tool Calls Panel */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <ToolCallPanel toolCalls={message.toolCalls} className="mt-1" />
        )}

        {/* Citations Panel - 引用展示 */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <CitationPanel
            citations={message.citations.map((c) => ({
              chunkId: c.chunkId,
              documentId: c.documentId,
              documentName: c.documentName,
              pageNumber: c.pageNumber,
              section: c.section,
              content: c.content,
              contentPreview: c.contentPreview,
              score: c.score,
            }))}
            className="mt-2 max-w-full"
          />
        )}

        {/* Actions */}
        {!isUser && !message.isStreaming && message.content && (
          <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
            {/* Copy Button */}
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleCopy}>
              {copied ? (
                <Check className="h-3 w-3 text-green-500" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>

            {/* TTS Play Button */}
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={audioUrl ? handleToggleAudio : handleGenerateSpeech}
              disabled={isGeneratingAudio}
            >
              {isGeneratingAudio ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : audioUrl ? (
                <Volume2 className="h-3 w-3" />
              ) : (
                <Volume2 className="h-3 w-3 opacity-50" />
              )}
            </Button>

            {/* Regenerate Button */}
            {onRegenerate && (
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onRegenerate}>
                <RotateCcw className="h-3 w-3" />
              </Button>
            )}
          </div>
        )}

        {/* Audio Player (when audio is generated) */}
        {audioUrl && !isUser && (
          <div className="mt-2">
            <audio
              ref={audioRef}
              src={audioUrl}
              onEnded={() => setIsPlayingAudio(false)}
              onPlay={() => setIsPlayingAudio(true)}
              onPause={() => setIsPlayingAudio(false)}
            />
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
