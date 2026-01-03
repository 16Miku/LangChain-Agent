'use client';

// ============================================================
// Presentation Player Component
// ============================================================

import React, { useEffect, useCallback, useState } from 'react';
import { X, ChevronLeft, ChevronRight, Expand } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { Presentation } from '@/lib/types/presentations';
import { SlidePreview } from './SlidePreview';

interface PresentationPlayerProps {
  presentation: Presentation;
  initialIndex: number;
  onClose: () => void;
}

export function PresentationPlayer({
  presentation,
  initialIndex,
  onClose,
}: PresentationPlayerProps) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showControls, setShowControls] = useState(true);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowRight':
      case ' ':
      case 'Enter':
        e.preventDefault();
        setCurrentIndex((i) => Math.min(presentation.slides.length - 1, i + 1));
        break;
      case 'ArrowLeft':
        e.preventDefault();
        setCurrentIndex((i) => Math.max(0, i - 1));
        break;
      case 'Escape':
        if (isFullscreen) {
          setIsFullscreen(false);
        } else {
          onClose();
        }
        break;
      case 'f':
      case 'F':
        setIsFullscreen((prev) => !prev);
        break;
    }
  }, [presentation.slides.length, isFullscreen, onClose]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Auto-hide controls
  useEffect(() => {
    if (!isFullscreen) return;

    const timer = setTimeout(() => setShowControls(false), 3000);
    return () => clearTimeout(timer);
  }, [showControls, isFullscreen]);

  const currentSlide = presentation.slides[currentIndex];

  const goToPrev = () => setCurrentIndex((i) => Math.max(0, i - 1));
  const goToNext = () => setCurrentIndex((i) => Math.min(presentation.slides.length - 1, i + 1));

  const containerClass = cn(
    'fixed inset-0 z-50 bg-black flex flex-col',
    isFullscreen && 'fullscreen'
  );

  return (
    <div
      className={containerClass}
      onMouseMove={() => isFullscreen && setShowControls(true)}
    >
      {/* Header Controls */}
      <div
        className={cn(
          'flex items-center justify-between p-4 bg-gradient-to-b from-black/50 to-transparent transition-opacity',
          !showControls && 'opacity-0'
        )}
      >
        <div className="text-white/80 text-sm">
          {presentation.title} • {currentIndex + 1} / {presentation.slides.length}
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="text-white hover:text-white"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            <Expand className="h-5 w-5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-white hover:text-white"
            onClick={onClose}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>
      </div>

      {/* Slide Display */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-6xl aspect-video">
          <SlidePreview
            slide={currentSlide}
            theme={presentation.theme}
            className="w-full h-full"
          />
        </div>
      </div>

      {/* Footer Controls */}
      <div
        className={cn(
          'flex items-center justify-between p-4 bg-gradient-to-t from-black/50 to-transparent transition-opacity',
          !showControls && 'opacity-0'
        )}
      >
        <Button
          variant="ghost"
          size="icon"
          className="text-white hover:text-white"
          onClick={goToPrev}
          disabled={currentIndex === 0}
        >
          <ChevronLeft className="h-6 w-6" />
        </Button>

        {/* Progress Bar */}
        <div className="flex-1 mx-8">
          <div className="bg-white/20 rounded-full h-1 overflow-hidden">
            <div
              className="bg-white h-full transition-all"
              style={{
                width: `${((currentIndex + 1) / presentation.slides.length) * 100}%`,
              }}
            />
          </div>
          <div className="flex justify-between mt-2">
            {presentation.slides.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentIndex(i)}
                className={cn(
                  'w-2 h-2 rounded-full transition-all',
                  i === currentIndex
                    ? 'bg-white scale-125'
                    : 'bg-white/40 hover:bg-white/60'
                )}
              />
            ))}
          </div>
        </div>

        <Button
          variant="ghost"
          size="icon"
          className="text-white hover:text-white"
          onClick={goToNext}
          disabled={currentIndex === presentation.slides.length - 1}
        >
          <ChevronRight className="h-6 w-6" />
        </Button>
      </div>

      {/* Keyboard Hints */}
      {!isFullscreen && (
        <div className="absolute bottom-20 left-1/2 -translate-x-1/2 text-white/60 text-xs">
          使用方向键或点击导航 • 按 F 全屏 • ESC 退出
        </div>
      )}
    </div>
  );
}
