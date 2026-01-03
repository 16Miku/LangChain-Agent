'use client';

// ============================================================
// Sidebar Component - Conversation List & Navigation
// ============================================================

import { useEffect } from 'react';
import { PlusCircle, MessageSquare, Settings, LogOut, Menu, Presentation } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useChatStore, useAuthStore, useSettingsStore } from '@/lib/stores';
import { cn } from '@/lib/utils';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ConversationItem } from './ConversationItem';

export function Sidebar() {
  const router = useRouter();
  const { sidebarOpen, toggleSidebar } = useSettingsStore();
  const { user, logout } = useAuthStore();
  const {
    conversations,
    currentConversationId,
    loadConversations,
    createConversation,
    selectConversation,
    deleteConversation,
  } = useChatStore();

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const handleNewChat = async () => {
    try {
      const id = await createConversation();
      router.push(`/chat/${id}`);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleSelectConversation = (id: string) => {
    selectConversation(id);
    router.push(`/chat/${id}`);
  };

  const handleRenameConversation = async (id: string, newTitle: string) => {
    // TODO: Implement rename API call
    console.log('Rename conversation:', id, 'to', newTitle);
    // For now, just update the local state
    const { conversations } = useChatStore.getState();
    const conv = conversations.find(c => c.id === id);
    if (conv) {
      useChatStore.setState({
        conversations: conversations.map(c =>
          c.id === id ? { ...c, title: newTitle } : c
        )
      });
    }
  };

  const handleDeleteConversation = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    await deleteConversation(id);
    if (currentConversationId === id) {
      router.push('/chat');
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  // Group conversations by date
  const groupedConversations = conversations.reduce(
    (groups, conv) => {
      const date = new Date(conv.createdAt);
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);

      let groupKey: string;
      if (date.toDateString() === today.toDateString()) {
        groupKey = 'Today';
      } else if (date.toDateString() === yesterday.toDateString()) {
        groupKey = 'Yesterday';
      } else {
        groupKey = date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' });
      }

      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(conv);
      return groups;
    },
    {} as Record<string, typeof conversations>
  );

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="fixed left-4 top-4 z-50 md:hidden"
        onClick={toggleSidebar}
      >
        <Menu className="h-5 w-5" />
      </Button>

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r bg-sidebar transition-transform duration-300 md:relative md:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Header */}
        <div className="flex h-16 items-center justify-between border-b px-4">
          <Link href="/chat" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <MessageSquare className="h-4 w-4" />
            </div>
            <span className="text-lg font-semibold">Stream-Agent</span>
          </Link>
          <Button variant="ghost" size="icon" className="md:hidden" onClick={toggleSidebar}>
            <Menu className="h-5 w-5" />
          </Button>
        </div>

        {/* New Chat Button */}
        <div className="p-4 space-y-2">
          <Button onClick={handleNewChat} className="w-full justify-start gap-2" variant="outline">
            <PlusCircle className="h-4 w-4" />
            New Chat
          </Button>
          <Button asChild className="w-full justify-start gap-2" variant="ghost">
            <Link href="/presentations">
              <Presentation className="h-4 w-4" />
              Presentations
            </Link>
          </Button>
        </div>

        {/* Conversation List */}
        <ScrollArea className="flex-1 px-2 w-full overflow-hidden">
          {Object.entries(groupedConversations).map(([group, convs]) => (
            <div key={group} className="mb-4">
              <p className="mb-2 px-2 text-xs font-medium text-muted-foreground">{group}</p>
              {convs.map((conv) => (
                <ConversationItem
                  key={conv.id}
                  id={conv.id}
                  title={conv.title}
                  isActive={currentConversationId === conv.id}
                  onSelect={handleSelectConversation}
                  onDelete={handleDeleteConversation}
                  onRename={handleRenameConversation}
                />
              ))}
            </div>
          ))}
        </ScrollArea>

        <Separator />

        {/* Footer - User Menu */}
        <div className="p-4">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="w-full justify-start gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                  {user?.username?.charAt(0).toUpperCase() || 'U'}
                </div>
                <span className="truncate">{user?.username || 'User'}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-56">
              <DropdownMenuItem asChild>
                <Link href="/settings" className="flex items-center gap-2">
                  <Settings className="h-4 w-4" />
                  Settings
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </aside>

      {/* Backdrop for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 md:hidden"
          onClick={toggleSidebar}
        />
      )}
    </>
  );
}
