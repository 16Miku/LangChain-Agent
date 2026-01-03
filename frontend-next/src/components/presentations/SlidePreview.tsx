'use client';

// ============================================================
// Slide Preview Component
// ============================================================

import React from 'react';
import type { Slide, PresentationTheme } from '@/lib/types/presentations';
import { cn } from '@/lib/utils';

interface SlidePreviewProps {
  slide: Slide;
  theme: PresentationTheme;
  className?: string;
}

const THEME_STYLES: Record<PresentationTheme, { bg: string; text: string; accent: string }> = {
  modern_business: {
    bg: 'bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-blue-950',
    text: 'text-gray-900 dark:text-gray-100',
    accent: 'text-blue-600 dark:text-blue-400',
  },
  creative: {
    bg: 'bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 dark:from-purple-950 dark:via-pink-950 dark:to-orange-950',
    text: 'text-gray-900 dark:text-gray-100',
    accent: 'text-purple-600 dark:text-purple-400',
  },
  minimalist: {
    bg: 'bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800',
    text: 'text-gray-900 dark:text-gray-100',
    accent: 'text-gray-600 dark:text-gray-400',
  },
  dark_professional: {
    bg: 'bg-gradient-to-br from-gray-900 to-gray-800',
    text: 'text-gray-100',
    accent: 'text-emerald-400',
  },
  colorful: {
    bg: 'bg-gradient-to-br from-yellow-50 via-green-50 to-blue-50 dark:from-yellow-950 dark:via-green-950 dark:to-blue-950',
    text: 'text-gray-900 dark:text-gray-100',
    accent: 'text-teal-600 dark:text-teal-400',
  },
  academic: {
    bg: 'bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900',
    text: 'text-slate-900 dark:text-slate-100',
    accent: 'text-slate-700 dark:text-slate-300',
  },
};

const LAYOUT_TEMPLATES: Record<Slide['layout'], string> = {
  title_cover: 'text-center py-16',
  title_section: 'text-center py-12',
  bullet_points: 'text-left py-8',
  two_column: 'grid grid-cols-2 gap-8 py-8',
  image_text: 'flex gap-8 py-8',
  quote_center: 'text-center py-16 italic',
  thank_you: 'text-center py-16',
};

export function SlidePreview({ slide, theme, className }: SlidePreviewProps) {
  const themeStyle = THEME_STYLES[theme] || THEME_STYLES.modern_business;
  const layoutClass = LAYOUT_TEMPLATES[slide.layout] || LAYOUT_TEMPLATES.bullet_points;

  // Parse content into bullet points
  const contentLines = slide.content.split('\\n').filter(line => line.trim());

  return (
    <div
      className={cn(
        'aspect-video rounded-lg shadow-lg p-8 flex flex-col justify-center',
        themeStyle.bg,
        themeStyle.text,
        className
      )}
      style={{
        background: slide.background || undefined,
      }}
    >
      <div className={cn('flex-1', layoutClass)}>
        {/* Title */}
        {slide.layout === 'title_cover' || slide.layout === 'title_section' ? (
          <h1 className="text-4xl md:text-5xl font-bold mb-8">{slide.title}</h1>
        ) : (
          <h2 className="text-2xl md:text-3xl font-bold mb-6">{slide.title}</h2>
        )}

        {/* Content */}
        {slide.layout === 'quote_center' ? (
          <blockquote className="text-2xl md:text-3xl italic opacity-80">
            {slide.content.replace(/^- /gm, '').replace(/\\n/g, '\n')}
          </blockquote>
        ) : slide.layout === 'thank_you' ? (
          <p className="text-xl md:text-2xl opacity-80">感谢观看</p>
        ) : (
          <ul className="space-y-3">
            {contentLines.map((line, i) => (
              <li
                key={i}
                className={cn(
                  'text-lg flex items-start',
                  themeStyle.accent
                )}
              >
                <span className="mr-3">•</span>
                <span>{line.replace(/^- /gm, '')}</span>
              </li>
            ))}
          </ul>
        )}

        {/* Notes indicator */}
        {slide.notes && (
          <div className="mt-8 pt-4 border-t border-current/20">
            <p className="text-sm opacity-60">演讲者备注可用</p>
          </div>
        )}
      </div>

      {/* Slide number */}
      <div className="text-xs opacity-40 text-right">
        {slide.layout !== 'title_cover' && '•'}
      </div>
    </div>
  );
}
