'use client';

// ============================================================
// AI Assistant Panel Component
// AI 助手对话面板组件
// ============================================================

import { useState, useRef, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Bot,
  Send,
  X,
  Loader2,
  CheckCircle,
  AlertCircle,
  MessageSquare,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { presentationApi, ChatMessage, AssistantChatResponse } from '@/lib/api/presentations';

interface AssistantPanelProps {
  presentationId: string;
  currentSlideIndex: number;
  onPresentationUpdate: (slides: unknown[]) => void;
  isOpen: boolean;
  onClose: () => void;
}

interface DisplayMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  actions?: {
    type: string;
    success: boolean;
    error?: string;
  }[];
}

export function AssistantPanel({
  presentationId,
  currentSlideIndex,
  onPresentationUpdate,
  isOpen,
  onClose,
}: AssistantPanelProps) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<ChatMessage[]>([]);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // 打开时聚焦输入框
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // 添加欢迎消息
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content: '你好！我是 PPT 编辑助手。你可以用自然语言告诉我你想做什么，例如：\n\n• "把第3页的标题改成xxx"\n• "在当前页后插入一张新幻灯片"\n• "删除第5页"\n• "把布局改成双栏"\n• "换成深色主题"',
          timestamp: new Date(),
        },
      ]);
    }
  }, [isOpen, messages.length]);

  // 发送消息
  const handleSend = useCallback(async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');

    // 添加用户消息到显示列表
    const userDisplayMessage: DisplayMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userDisplayMessage]);

    // 添加到对话历史
    const userChatMessage: ChatMessage = {
      role: 'user',
      content: userMessage,
    };
    setConversationHistory((prev) => [...prev, userChatMessage]);

    setIsLoading(true);

    try {
      // 调用 AI 助手 API
      const response: AssistantChatResponse = await presentationApi.assistantChat(
        presentationId,
        {
          message: userMessage,
          current_slide_index: currentSlideIndex,
          conversation_history: conversationHistory.slice(-10), // 最近 10 条
        }
      );

      // 添加助手回复到显示列表
      const assistantDisplayMessage: DisplayMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        actions: response.actions.map((action) => ({
          type: action.action_type,
          success: action.success,
          error: action.error_message || undefined,
        })),
      };
      setMessages((prev) => [...prev, assistantDisplayMessage]);

      // 添加到对话历史
      const assistantChatMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
      };
      setConversationHistory((prev) => [...prev, assistantChatMessage]);

      // 如果演示文稿被更新，通知父组件
      if (response.presentation_updated && response.updated_slides) {
        onPresentationUpdate(response.updated_slides);
      }
    } catch (error) {
      console.error('Assistant chat error:', error);
      // 添加错误消息
      const errorMessage: DisplayMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: '抱歉，发生了错误。请稍后重试。',
        timestamp: new Date(),
        actions: [{ type: 'error', success: false, error: '网络错误' }],
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [inputValue, isLoading, presentationId, currentSlideIndex, conversationHistory, onPresentationUpdate]);

  // 处理键盘事件
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 清空对话
  const handleClear = () => {
    setMessages([]);
    setConversationHistory([]);
  };

  if (!isOpen) return null;

  return (
    <div className="flex flex-col h-full border-l bg-background">
      {/* 头部 */}
      <div className="flex items-center justify-between p-3 border-b">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-primary" />
          <span className="font-medium">AI 助手</span>
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleClear}
            title="清空对话"
          >
            <MessageSquare className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            title="关闭"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* 消息列表 */}
      <ScrollArea className="flex-1 p-3" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                'flex',
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              <div
                className={cn(
                  'max-w-[85%] rounded-lg px-3 py-2 text-sm',
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                )}
              >
                {/* 消息内容 */}
                <div className="whitespace-pre-wrap">{message.content}</div>

                {/* 操作结果 */}
                {message.actions && message.actions.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-border/50 space-y-1">
                    {message.actions.map((action, index) => (
                      <div
                        key={index}
                        className={cn(
                          'flex items-center gap-1 text-xs',
                          action.success ? 'text-green-600' : 'text-red-600'
                        )}
                      >
                        {action.success ? (
                          <CheckCircle className="h-3 w-3" />
                        ) : (
                          <AlertCircle className="h-3 w-3" />
                        )}
                        <span>
                          {action.type === 'edit_title' && '修改标题'}
                          {action.type === 'edit_content' && '修改内容'}
                          {action.type === 'edit_notes' && '修改备注'}
                          {action.type === 'insert_slide' && '插入幻灯片'}
                          {action.type === 'delete_slide' && '删除幻灯片'}
                          {action.type === 'change_layout' && '更改布局'}
                          {action.type === 'change_theme' && '更换主题'}
                          {action.type === 'regenerate' && '重新生成'}
                          {action.type === 'chat' && '对话'}
                          {action.type === 'error' && '错误'}
                          {action.error && `: ${action.error}`}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* 加载指示器 */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg px-3 py-2">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* 输入区域 */}
      <div className="p-3 border-t">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入指令，如：把标题改成..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            size="icon"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          当前选中：第 {currentSlideIndex + 1} 页
        </p>
      </div>
    </div>
  );
}

export default AssistantPanel;
