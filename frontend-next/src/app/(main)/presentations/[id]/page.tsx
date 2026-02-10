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
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
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
  const [showThumbnails, setShowThumbnails] = useState(false); // 移动端缩略图面板
  const [mobileView, setMobileView] = useState<'editor' | 'preview'>('editor'); // 移动端视图切换
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

  const handleExportPptx = async () => {
    if (currentPresentation) {
      await presentationApi.exportToPptx(currentPresentation.id);
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
      {/* Header - 响应式优化 */}
      <div className="flex items-center justify-between border-b px-2 sm:px-4 py-2">
        <div className="flex items-center gap-1 sm:gap-2 min-w-0">
          <Button variant="ghost" size="icon" onClick={() => router.push('/presentations')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          {/* 移动端显示缩略图按钮 */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setShowThumbnails(!showThumbnails)}
          >
            <Menu className="h-4 w-4" />
          </Button>
          <Input
            value={displayTitle}
            onChange={(e) => handleTitleChange(e.target.value)}
            className="w-32 sm:w-64 font-semibold border-none shadow-none focus-visible:ring-0 text-sm sm:text-base"
          />
          {hasChanges && (
            <span className="text-xs text-muted-foreground hidden sm:inline">未保存</span>
          )}
        </div>

        {/* 桌面端工具栏 */}
        <div className="hidden md:flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowThemeSelector(true)}
            className="gap-2"
          >
            <Palette className="h-4 w-4" />
            <span className="hidden lg:inline">
              {THEMES.find(t => t.value === currentPresentation.theme)?.label || currentPresentation.theme}
            </span>
          </Button>

          <Separator orientation="vertical" className="h-6" />

          <Button
            variant="outline"
            size="sm"
            onClick={handleAddSlide}
            disabled={isGenerating}
          >
            <Plus className="h-4 w-4 lg:mr-2" />
            <span className="hidden lg:inline">添加幻灯片</span>
          </Button>

          <Button
            variant={showAssistant ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowAssistant(!showAssistant)}
            className="gap-2"
          >
            <Bot className="h-4 w-4" />
            <span className="hidden lg:inline">AI 助手</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleSave}
            disabled={!hasChanges}
          >
            <Save className="h-4 w-4 lg:mr-2" />
            <span className="hidden lg:inline">保存</span>
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-2">
                <Download className="h-4 w-4" />
                <span className="hidden lg:inline">导出</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleExportPptx}>
                <Download className="h-4 w-4 mr-2" />
                导出 PPTX (PowerPoint)
              </DropdownMenuItem>
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
            <span className="hidden lg:inline">播放</span>
          </Button>
        </div>

        {/* 移动端工具栏 - 精简版 */}
        <div className="flex md:hidden items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setShowThemeSelector(true)}
          >
            <Palette className="h-4 w-4" />
          </Button>
          <Button
            variant={showAssistant ? 'default' : 'ghost'}
            size="icon"
            onClick={() => setShowAssistant(!showAssistant)}
          >
            <Bot className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleSave}
            disabled={!hasChanges}
          >
            <Save className="h-4 w-4" />
          </Button>
          <Button
            size="icon"
            onClick={() => setShowPlayer(true)}
          >
            <Play className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Main Content - 响应式布局 */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Slide Thumbnails - 移动端抽屉式 */}
        <div className={`
          absolute md:relative inset-y-0 left-0 z-20
          w-48 border-r bg-background p-2 overflow-y-auto
          transform transition-transform duration-300
          ${showThumbnails ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}>
          {/* 移动端关闭按钮 */}
          <div className="flex justify-between items-center mb-2 md:hidden">
            <span className="text-sm font-medium">幻灯片</span>
            <Button variant="ghost" size="icon" onClick={() => setShowThumbnails(false)}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="space-y-2">
            {currentPresentation.slides.map((slide, index) => (
              <button
                key={index}
                onClick={() => {
                  setCurrentSlideIndex(index);
                  setShowThumbnails(false); // 移动端选择后关闭
                }}
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

        {/* 移动端缩略图遮罩 */}
        {showThumbnails && (
          <div
            className="absolute inset-0 bg-black/50 z-10 md:hidden"
            onClick={() => setShowThumbnails(false)}
          />
        )}

        {/* Slide Editor & Preview */}
        <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
          {/* 移动端视图切换标签 */}
          <div className="flex md:hidden border-b">
            <button
              onClick={() => setMobileView('editor')}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${
                mobileView === 'editor'
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-muted-foreground'
              }`}
            >
              编辑
            </button>
            <button
              onClick={() => setMobileView('preview')}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${
                mobileView === 'preview'
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-muted-foreground'
              }`}
            >
              预览
            </button>
          </div>

          {/* Editor Panel */}
          <div className={`
            flex-1 p-2 sm:p-4 overflow-y-auto
            ${mobileView === 'editor' ? 'block' : 'hidden'} md:block
          `}>
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

          <Separator orientation="vertical" className="hidden md:block" />

          {/* Preview Panel */}
          <div className={`
            flex-1 md:w-1/3 lg:w-1/2 p-2 sm:p-4 bg-muted/10 overflow-y-auto
            ${mobileView === 'preview' ? 'block' : 'hidden'} md:block
            ${showAssistant ? 'md:w-1/3' : 'md:w-1/2'}
            transition-all
          `}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-sm sm:text-base">预览</h3>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1))}
                  disabled={currentSlideIndex === 0}
                >
                  <ChevronLeft className="h-4 w-4" />
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
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <SlidePreview
              slide={currentSlide}
              theme={currentPresentation.theme}
            />
          </div>
        </div>

        {/* AI Assistant Panel - 移动端全屏覆盖 */}
        {showAssistant && (
          <>
            {/* 移动端遮罩 */}
            <div
              className="absolute inset-0 bg-black/50 z-20 md:hidden"
              onClick={() => setShowAssistant(false)}
            />
            <div className={`
              absolute md:relative inset-y-0 right-0 z-30
              w-full sm:w-80 md:w-80
              transform transition-transform duration-300
            `}>
              <AssistantPanel
                presentationId={currentPresentation.id}
                currentSlideIndex={currentSlideIndex}
                onPresentationUpdate={handleAssistantUpdate}
                isOpen={showAssistant}
                onClose={() => setShowAssistant(false)}
              />
            </div>
          </>
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
