'use client';

// ============================================================
// Presentations List Page
// ============================================================

import React, { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Plus,
  FileText,
  Trash2,
  MoreVertical,
  Sparkles,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

import { usePresentationStore } from '@/lib/stores/presentationStore';
import type { PresentationTheme } from '@/lib/types/presentations';

// 格式化日期为相对时间
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return '刚刚';
  if (diffMins < 60) return `${diffMins} 分钟前`;
  if (diffHours < 24) return `${diffHours} 小时前`;
  if (diffDays < 7) return `${diffDays} 天前`;

  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
  });
}

export default function PresentationsPage() {
  const router = useRouter();
  const {
    presentations,
    isLoading,
    fetchPresentations,
    deletePresentation,
    createPresentation,
    generatePresentation,
    isGenerating,
  } = usePresentationStore();

  useEffect(() => {
    fetchPresentations();
  }, [fetchPresentations]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (confirm('确定要删除这个演示文稿吗？')) {
      await deletePresentation(id);
    }
  };

  const handleCreateBlank = async (title: string) => {
    try {
      const presentation = await createPresentation(title);
      router.push(`/presentations/${presentation.id}`);
    } catch (error) {
      console.error('Failed to create presentation:', error);
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b px-6 py-4">
        <div>
          <h1 className="text-2xl font-semibold">演示文稿</h1>
          <p className="text-sm text-muted-foreground">
            创建和管理 AI 生成的演示文稿
          </p>
        </div>
        <CreatePresentationDialog
          onCreate={handleCreateBlank}
          onGenerate={async (data) => {
            try {
              const presentation = await generatePresentation(data);
              router.push(`/presentations/${presentation.id}`);
            } catch (error) {
              console.error('Failed to generate presentation:', error);
            }
          }}
          isGenerating={isGenerating}
        />
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
              <p className="text-muted-foreground">加载中...</p>
            </div>
          </div>
        ) : presentations.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full">
            <FileText className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">还没有演示文稿</h3>
            <p className="text-muted-foreground mb-6">
              创建一个空白演示文稿或使用 AI 生成
            </p>
            <CreatePresentationDialog
              onCreate={handleCreateBlank}
              onGenerate={async (data) => {
                try {
                  const presentation = await generatePresentation(data);
                  router.push(`/presentations/${presentation.id}`);
                } catch (error) {
                  console.error('Failed to generate presentation:', error);
                }
              }}
              isGenerating={isGenerating}
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {presentations.map((presentation) => (
              <Link key={presentation.id} href={`/presentations/${presentation.id}`}>
                <Card className="h-full transition-all hover:shadow-md hover:border-primary/50 cursor-pointer group">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <CardTitle className="line-clamp-1 text-base">
                        {presentation.title}
                      </CardTitle>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild onClick={(e) => e.preventDefault()}>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={(e) => handleDelete(presentation.id, e)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            删除
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                    <CardDescription className="line-clamp-2">
                      {presentation.description || '暂无描述'}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pb-3">
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span className="px-2 py-1 rounded-full bg-secondary">
                        {presentation.slideCount} 张幻灯片
                      </span>
                      <span className="px-2 py-1 rounded-full bg-secondary">
                        {presentation.theme}
                      </span>
                    </div>
                  </CardContent>
                  <CardFooter className="pt-0 text-xs text-muted-foreground">
                    {formatDate(presentation.updatedAt)}
                  </CardFooter>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================
// Create Presentation Dialog
// ============================================================

interface CreatePresentationDialogProps {
  onCreate: (title: string) => void;
  onGenerate: (data: {
    topic: string;
    title?: string;
    slideCount?: number;
    targetAudience?: string;
    presentationType?: 'informative' | 'persuasive' | 'instructional';
    theme?: PresentationTheme;
    includeImages?: boolean;
    imageStyle?: string;
    language?: 'zh-CN' | 'en-US';
  }) => void;
  isGenerating: boolean;
}

function CreatePresentationDialog({
  onCreate,
  onGenerate,
  isGenerating,
}: CreatePresentationDialogProps) {
  const [open, setOpen] = React.useState(false);
  const [mode, setMode] = React.useState<'blank' | 'ai'>('blank');
  const [title, setTitle] = React.useState('');
  const [topic, setTopic] = React.useState('');
  const [slideCount, setSlideCount] = React.useState(10);

  const handleCreate = () => {
    if (mode === 'blank') {
      if (title.trim()) {
        onCreate(title.trim());
        setTitle('');
        setOpen(false);
      }
    } else {
      if (topic.trim()) {
        onGenerate({
          topic: topic.trim(),
          title: title.trim() || undefined,
          slideCount,
          targetAudience: 'general',
          presentationType: 'informative',
          theme: 'modern_business',
          includeImages: false,  // 暂时禁用图片 (Picsum 随机图片与内容不相关)
          language: 'zh-CN',
        });
        setTopic('');
        setTitle('');
        setSlideCount(10);
        setOpen(false);
      }
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          创建
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>创建演示文稿</DialogTitle>
          <DialogDescription>
            选择创建方式
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Mode Toggle */}
          <div className="flex gap-2">
            <Button
              type="button"
              variant={mode === 'blank' ? 'default' : 'outline'}
              className="flex-1"
              onClick={() => setMode('blank')}
            >
              空白演示文稿
            </Button>
            <Button
              type="button"
              variant={mode === 'ai' ? 'default' : 'outline'}
              className="flex-1 gap-2"
              onClick={() => setMode('ai')}
            >
              <Sparkles className="h-4 w-4" />
              AI 生成
            </Button>
          </div>

          {/* Common Fields */}
          <div className="space-y-2">
            {mode === 'blank' ? (
              <>
                <label htmlFor="title" className="text-sm font-medium">
                  标题
                </label>
                <Input
                  id="title"
                  placeholder="输入演示文稿标题"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </>
            ) : (
              <>
                <label htmlFor="topic" className="text-sm font-medium">
                  主题
                </label>
                <Textarea
                  id="topic"
                  placeholder="描述你想要生成的演示文稿主题..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  rows={3}
                />
                <label htmlFor="slideCount" className="text-sm font-medium mt-2">
                  幻灯片数量: {slideCount}
                </label>
                <input
                  id="slideCount"
                  type="range"
                  min="3"
                  max="20"
                  value={slideCount}
                  onChange={(e) => setSlideCount(Number(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>3</span>
                  <span>20</span>
                </div>
              </>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            取消
          </Button>
          <Button onClick={handleCreate} disabled={isGenerating}>
            {isGenerating ? '生成中...' : mode === 'ai' ? '生成演示文稿' : '创建'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
