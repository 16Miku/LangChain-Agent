'use client';

// ============================================================
// Input Area Component
// ============================================================

import { useState, useRef, useCallback } from 'react';
import { Send, Paperclip, X, StopCircle, Mic, Image as ImageIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

interface InputAreaProps {
  onSend: (message: string, images?: string[]) => void;
  onStop?: () => void;
  isStreaming?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export function InputArea({
  onSend,
  onStop,
  isStreaming = false,
  disabled = false,
  placeholder = 'Type your message...',
}: InputAreaProps) {
  const [input, setInput] = useState('');
  const [images, setImages] = useState<{ file: File; preview: string }[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = useCallback(() => {
    if (!input.trim() && images.length === 0) return;
    if (isStreaming || disabled) return;

    const imageBase64s = images.map((img) => img.preview.split(',')[1]);
    onSend(input.trim(), imageBase64s.length > 0 ? imageBase64s : undefined);

    setInput('');
    setImages([]);

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [input, images, isStreaming, disabled, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);

    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    Array.from(files).forEach((file) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const result = event.target?.result as string;
          setImages((prev) => [...prev, { file, preview: result }]);
        };
        reader.readAsDataURL(file);
      }
    });

    // Reset file input
    e.target.value = '';
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    const items = e.clipboardData.items;
    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) {
          const reader = new FileReader();
          reader.onload = (event) => {
            const result = event.target?.result as string;
            setImages((prev) => [...prev, { file, preview: result }]);
          };
          reader.readAsDataURL(file);
        }
      }
    }
  };

  const removeImage = (index: number) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="border-t bg-background p-4">
      <div className="mx-auto max-w-3xl">
        {/* Image Preview Bar */}
        {images.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {images.map((img, index) => (
              <div key={index} className="relative">
                <img
                  src={img.preview}
                  alt={`Preview ${index + 1}`}
                  className="h-20 w-20 rounded-lg object-cover"
                />
                <button
                  onClick={() => removeImage(index)}
                  className="absolute -right-2 -top-2 rounded-full bg-destructive p-1 text-destructive-foreground"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Input Container */}
        <div className="flex items-end gap-2 rounded-2xl border bg-card p-2">
          {/* File Upload Button */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 shrink-0"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={disabled || isStreaming}
                >
                  <Paperclip className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Attach file</TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,.pdf,.csv,.xlsx,.xls,.json,.txt,.py"
            multiple
            className="hidden"
            onChange={handleFileSelect}
          />

          {/* Image Upload Button */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 shrink-0"
                  onClick={() => {
                    const input = document.createElement('input');
                    input.type = 'file';
                    input.accept = 'image/*';
                    input.multiple = true;
                    input.onchange = (e) =>
                      handleFileSelect(e as unknown as React.ChangeEvent<HTMLInputElement>);
                    input.click();
                  }}
                  disabled={disabled || isStreaming}
                >
                  <ImageIcon className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Upload image</TooltipContent>
            </Tooltip>
          </TooltipProvider>

          {/* Textarea */}
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            onPaste={handlePaste}
            placeholder={placeholder}
            disabled={disabled}
            className={cn(
              'min-h-[40px] max-h-[200px] flex-1 resize-none border-0 bg-transparent p-2 focus-visible:ring-0',
              disabled && 'opacity-50'
            )}
            rows={1}
          />

          {/* Voice Input Button (placeholder for future) */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 shrink-0"
                  disabled={disabled || isStreaming}
                >
                  <Mic className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Voice input (coming soon)</TooltipContent>
            </Tooltip>
          </TooltipProvider>

          {/* Send / Stop Button */}
          {isStreaming ? (
            <Button
              type="button"
              variant="destructive"
              size="icon"
              className="h-9 w-9 shrink-0"
              onClick={onStop}
            >
              <StopCircle className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              type="button"
              size="icon"
              className="h-9 w-9 shrink-0"
              onClick={handleSubmit}
              disabled={disabled || (!input.trim() && images.length === 0)}
            >
              <Send className="h-4 w-4" />
            </Button>
          )}
        </div>

        {/* Hint Text */}
        <p className="mt-2 text-center text-xs text-muted-foreground">
          Press Enter to send, Shift+Enter for new line. Paste images directly.
        </p>
      </div>
    </div>
  );
}
