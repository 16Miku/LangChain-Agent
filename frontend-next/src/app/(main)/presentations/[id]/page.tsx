'use client';

// ============================================================
// Presentation Editor Page
// ============================================================

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft,
  Save,
  Play,
  Plus,
  Palette,
  Bot,
  Download,
  ExternalLink,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
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
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

import { usePresentationStore } from '@/lib/stores/presentationStore';
import type { Slide, PresentationTheme } from '@/lib/types/presentations';
import { presentationApi } from '@/lib/api/presentations';
import { SlidePreview } from '@/components/presentations/SlidePreview';
import { SlideEditor } from '@/components/presentations/SlideEditor';
import { ThemeSelector } from '@/components/presentations/ThemeSelector';
import { PresentationPlayer } from '@/components/presentations/PresentationPlayer';
import { AssistantPanel } from '@/components/presentations/AssistantPanel';

const THEMES: { value: PresentationTheme; label: string }[] = [
  { value: 'modern_business', label: '现代商务' },
  { value: 'creative', label: '创意设计' },
  { value: 'minimalist', label: '极简主义' },
  { value: 'dark_professional', label: '暗色专业' },
  { value: 'colorful', label: '多彩活泼' },
  { value: 'academic', label: '学术风格' },
];

export default function PresentationEditorPage() {
  const params = useParams();
  const router = useRouter();
  const presentationId = params.id as string;

  const {
    currentPresentation,
    currentSlideIndex,
    isLoading,
    isGenerating,
    error,
    fetchPresentation,
    setCurrentSlideIndex,
    updateSlide,
    addSlide,
    deleteSlide,
    regenerateSlide,
    changeTheme,
    updatePresentation,
    updateCurrentPresentationSlides,
  } = usePresentationStore();

  const [showPlayer, setShowPlayer] = useState(false);
  const [showThemeSelector, setShowThemeSelector] = useState(false);
  const [showRegenerateDialog, setShowRegenerateDialog] = useState(false);
  const [showAssistant, setShowAssistant] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [hasChanges, setHasChanges] = useState(false);
  // 本地标题状态：null 表示使用 store 的标题，非 null 表示用户正在编辑
  const [localTitle, setLocalTitle] = useState<string | null>(null);

  useEffect(() => {
    if (presentationId) {
      fetchPresentation(presentationId);
    }
  }, [presentationId, fetchPresentation]);

  // 获取显示的标题（优先使用本地编辑状态）
  const displayTitle = localTitle ?? currentPresentation?.title ?? '';

  const handleTitleChange = (value: string) => {
    setLocalTitle(value);
    setHasChanges(true);
  };

  const handleSave = async () => {
    if (currentPresentation) {
      await updatePresentation(currentPresentation.id, {
        title: displayTitle,
        description: currentPresentation.description,
      });
      setLocalTitle(null); // 保存后重置本地状态
      setHasChanges(false);
    }
  };

  const handleSlideChange = async (slideIndex: number, data: Partial<Slide>) => {
    if (currentPresentation) {
      await updateSlide(currentPresentation.id, slideIndex, data);
      setHasChanges(true);
    }
  };

  const handleAddSlide = async () => {
    if (currentPresentation) {
      const newSlide: Slide = {
        title: '新幻灯片',
        content: '- 要点一\\n- 要点二\\n- 要点三',
        layout: 'bullet_points',
      };
      await addSlide(currentPresentation.id, newSlide, currentSlideIndex + 1);
      setCurrentSlideIndex(currentSlideIndex + 1);
      setHasChanges(true);
    }
  };

  const handleDeleteSlide = async () => {
    if (currentPresentation && currentPresentation.slides.length > 1) {
      await deleteSlide(currentPresentation.id, currentSlideIndex);
      setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1));
      setHasChanges(true);
    }
  };

  const handleRegenerate = async () => {
    if (currentPresentation && feedback.trim()) {
      await regenerateSlide(currentPresentation.id, currentSlideIndex, feedback);
      setFeedback('');
      setShowRegenerateDialog(false);
      setHasChanges(true);
    }
  };

  const handleThemeChange = async (theme: PresentationTheme) => {
    if (currentPresentation) {
      await changeTheme(currentPresentation.id, theme);
      setShowThemeSelector(false);
      setHasChanges(true);
    }
  };

  const handleExportHtml = async () => {
    if (currentPresentation) {
      await presentationApi.exportToHtml(currentPresentation.id, true);
    }
  };

  const handleExportSimpleHtml = async () => {
    if (currentPresentation) {
      await presentationApi.exportToHtml(currentPresentation.id, false);
    }
  };

  const handleOpenPreview = async () => {
    if (currentPresentation) {
      await presentationApi.openPreview(currentPresentation.id);
    }
  };

  // AI 助手更新演示文稿的回调（静默更新，不触发 isLoading）
  const handleAssistantUpdate = useCallback((updatedSlides: unknown[]) => {
    // 直接更新 store 中的幻灯片数据，不重新获取
    updateCurrentPresentationSlides(updatedSlides as Slide[]);
    setHasChanges(true);
  }, [updateCurrentPresentationSlides]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground">加载中...</p>
        </div>
      </div>
    );
  }

  if (error && !currentPresentation) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-destructive mb-4">{error}</p>
          <Button variant="outline" onClick={() => router.push('/presentations')}>
            返回列表
          </Button>
        </div>
      </div>
    );
  }

  if (!currentPresentation) {
    return null;
  }

  const currentSlide = currentPresentation.slides[currentSlideIndex];

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b px-4 py-2">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={() => router.push('/presentations')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <Input
            value={displayTitle}
            onChange={(e) => handleTitleChange(e.target.value)}
            className="w-64 font-semibold border-none shadow-none focus-visible:ring-0"
          />
          {hasChanges && (
            <span className="text-xs text-muted-foreground">未保存</span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowThemeSelector(true)}
            className="gap-2"
          >
            <Palette className="h-4 w-4" />
            {THEMES.find(t => t.value === currentPresentation.theme)?.label || currentPresentation.theme}
          </Button>

          <Separator orientation="vertical" className="h-6" />

          <Button
            variant="outline"
            size="sm"
            onClick={handleAddSlide}
            disabled={isGenerating}
          >
            <Plus className="h-4 w-4 mr-2" />
            添加幻灯片
          </Button>

          <Button
            variant={showAssistant ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowAssistant(!showAssistant)}
            className="gap-2"
          >
            <Bot className="h-4 w-4" />
            AI 助手
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleSave}
            disabled={!hasChanges}
          >
            <Save className="h-4 w-4 mr-2" />
            保存
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-2">
                <Download className="h-4 w-4" />
                导出
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleExportHtml}>
                <Download className="h-4 w-4 mr-2" />
                导出 HTML (含 Reveal.js)
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleExportSimpleHtml}>
                <Download className="h-4 w-4 mr-2" />
                导出 HTML (简洁版)
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleOpenPreview}>
                <ExternalLink className="h-4 w-4 mr-2" />
                浏览器预览
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button
            size="sm"
            onClick={() => setShowPlayer(true)}
            className="gap-2"
          >
            <Play className="h-4 w-4" />
            播放
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Slide Thumbnails */}
        <div className="w-48 border-r bg-muted/20 p-2 overflow-y-auto">
          <div className="space-y-2">
            {currentPresentation.slides.map((slide, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlideIndex(index)}
                className={`
                  w-full rounded-lg border-2 p-2 text-left transition-all
                  ${currentSlideIndex === index
                    ? 'border-primary bg-primary/10'
                    : 'border-transparent hover:border-border'
                  }
                `}
              >
                <div className="text-xs font-medium truncate mb-1">
                  {index + 1}. {slide.title}
                </div>
                <div className="text-xs text-muted-foreground line-clamp-2">
                  {slide.content.replace(/\\n/g, ' ')}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Slide Editor & Preview */}
        <div className="flex-1 flex overflow-hidden">
          {/* Editor Panel */}
          <div className="flex-1 p-4 overflow-y-auto">
            <SlideEditor
              key={currentSlideIndex}
              slide={currentSlide}
              slideIndex={currentSlideIndex}
              totalSlides={currentPresentation.slides.length}
              onChange={(data) => handleSlideChange(currentSlideIndex, data)}
              onAddSlide={handleAddSlide}
              onDeleteSlide={handleDeleteSlide}
              canDelete={currentPresentation.slides.length > 1}
              isSaving={isLoading}
            />
          </div>

          <Separator orientation="vertical" />

          {/* Preview Panel */}
          <div className={`${showAssistant ? 'w-1/3' : 'w-1/2'} p-4 bg-muted/10 overflow-y-auto transition-all`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium">预览</h3>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1))}
                  disabled={currentSlideIndex === 0}
                >
                  ‹
                </Button>
                <span className="text-sm self-center px-2">
                  {currentSlideIndex + 1} / {currentPresentation.slides.length}
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setCurrentSlideIndex(
                    Math.min(currentPresentation.slides.length - 1, currentSlideIndex + 1)
                  )}
                  disabled={currentSlideIndex === currentPresentation.slides.length - 1}
                >
                  ›
                </Button>
              </div>
            </div>
            <SlidePreview
              slide={currentSlide}
              theme={currentPresentation.theme}
            />
          </div>
        </div>

        {/* AI Assistant Panel */}
        {showAssistant && (
          <div className="w-80">
            <AssistantPanel
              presentationId={currentPresentation.id}
              currentSlideIndex={currentSlideIndex}
              onPresentationUpdate={handleAssistantUpdate}
              isOpen={showAssistant}
              onClose={() => setShowAssistant(false)}
            />
          </div>
        )}
      </div>

      {/* Theme Selector Dialog */}
      <Dialog open={showThemeSelector} onOpenChange={setShowThemeSelector}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>更换主题</DialogTitle>
            <DialogDescription>
              选择一个主题应用到整个演示文稿
            </DialogDescription>
          </DialogHeader>
          <ThemeSelector
            currentTheme={currentPresentation.theme}
            onThemeChange={handleThemeChange}
          />
        </DialogContent>
      </Dialog>

      {/* Regenerate Slide Dialog */}
      <Dialog open={showRegenerateDialog} onOpenChange={setShowRegenerateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>重新生成幻灯片</DialogTitle>
            <DialogDescription>
              描述你希望如何改进这张幻灯片
            </DialogDescription>
          </DialogHeader>
          <Textarea
            placeholder="例如：添加更多细节、使用更简洁的语言、添加图表说明..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            rows={4}
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRegenerateDialog(false)}>
              取消
            </Button>
            <Button onClick={handleRegenerate} disabled={isGenerating || !feedback.trim()}>
              {isGenerating ? '生成中...' : '重新生成'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Presentation Player */}
      {showPlayer && (
        <PresentationPlayer
          presentation={currentPresentation}
          initialIndex={currentSlideIndex}
          onClose={() => {
            setShowPlayer(false);
            setCurrentSlideIndex(currentSlideIndex);
          }}
        />
      )}
    </div>
  );
}
