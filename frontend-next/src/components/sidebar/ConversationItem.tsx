'use client';

// ============================================================
// Conversation Item Component
// ============================================================

import { useState, useRef, useEffect } from 'react';
import { MessageSquare, Edit2, Trash2, Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

interface ConversationItemProps {
  id: string;
  title: string;
  isActive: boolean;
  onSelect: (id: string) => void;
  onDelete: (e: React.MouseEvent, id: string) => Promise<void>;
  onRename?: (id: string, newTitle: string) => Promise<void>;
}

export function ConversationItem({
  id,
  title,
  isActive,
  onSelect,
  onDelete,
  onRename,
}: ConversationItemProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(title);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setEditTitle(title);
  }, [title]);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleRename = async () => {
    if (editTitle.trim() && editTitle !== title && onRename) {
      try {
        await onRename(id, editTitle.trim());
        setIsEditing(false);
      } catch (error) {
        console.error('Rename failed:', error);
      }
    } else {
      setIsEditing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleRename();
    } else if (e.key === 'Escape') {
      setEditTitle(title);
      setIsEditing(false);
    }
  };

  return (
    <div
      className={cn(
        'group relative cursor-pointer rounded-lg px-3 py-2 hover:bg-sidebar-accent min-h-10',
        isActive && 'bg-sidebar-accent'
      )}
      style={{ maxWidth: '100%' }}
      onClick={() => !isEditing && onSelect(id)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 使用 Grid 布局：图标 | 标题 | 按钮 */}
      <div className="grid grid-cols-[16px_1fr_auto] items-center gap-2 w-full">
        {/* 图标 */}
        <MessageSquare className="h-4 w-4 text-muted-foreground" />

        {/* 标题区域 */}
        {isEditing ? (
          <Input
            ref={inputRef}
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onKeyDown={handleKeyDown}
            className="h-6 px-1 text-sm"
            onClick={(e) => e.stopPropagation()}
          />
        ) : (
          <span
            className="truncate text-sm"
            title={title}
          >
            {title}
          </span>
        )}

        {/* 操作按钮 */}
        <div
          className={cn(
            "flex items-center gap-1 transition-opacity duration-150",
            (isHovered || isEditing) ? "opacity-100" : "opacity-0"
          )}
        >
          {isEditing ? (
            <>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRename();
                }}
              >
                <Check className="h-3 w-3 text-green-600" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={(e) => {
                  e.stopPropagation();
                  setEditTitle(title);
                  setIsEditing(false);
                }}
              >
                <X className="h-3 w-3 text-destructive" />
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsEditing(true);
                }}
              >
                <Edit2 className="h-3 w-3" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 text-destructive hover:text-destructive hover:bg-destructive/10"
                onClick={(e) => onDelete(e, id)}
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
