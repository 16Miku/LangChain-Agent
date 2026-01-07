'use client';

// ============================================================
// Slide Preview Component
// 支持 17 种主题样式和图片显示
// ============================================================

import React from 'react';
import type { Slide, PresentationTheme } from '@/lib/types/presentations';
import { cn } from '@/lib/utils';

interface SlidePreviewProps {
  slide: Slide;
  theme: PresentationTheme;
  className?: string;
}

// 17 种主题样式定义
const THEME_STYLES: Record<string, { bg: string; text: string; accent: string }> = {
  // 商务专业
  modern_business: {
    bg: 'bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-blue-950',
    text: 'text-gray-900 dark:text-gray-100',
    accent: 'text-blue-600 dark:text-blue-400',
  },
  corporate_blue: {
    bg: 'bg-gradient-to-br from-blue-600 to-blue-800',
    text: 'text-white',
    accent: 'text-blue-200',
  },
  elegant_dark: {
    bg: 'bg-gradient-to-br from-gray-900 via-gray-800 to-amber-900',
    text: 'text-amber-50',
    accent: 'text-amber-400',
  },
  academic_classic: {
    bg: 'bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-900 dark:to-slate-800',
    text: 'text-slate-900 dark:text-slate-100',
    accent: 'text-slate-700 dark:text-slate-300',
  },
  // 科技创新
  dark_tech: {
    bg: 'bg-gradient-to-br from-gray-900 to-emerald-900',
    text: 'text-emerald-50',
    accent: 'text-emerald-400',
  },
  gradient_purple: {
    bg: 'bg-gradient-to-br from-purple-600 via-pink-500 to-orange-400',
    text: 'text-white',
    accent: 'text-yellow-200',
  },
  neon_future: {
    bg: 'bg-gradient-to-br from-violet-900 via-purple-800 to-fuchsia-900',
    text: 'text-fuchsia-50',
    accent: 'text-cyan-400',
  },
  // 简约清新
  minimal_white: {
    bg: 'bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800',
    text: 'text-gray-900 dark:text-gray-100',
    accent: 'text-gray-600 dark:text-gray-400',
  },
  nature_green: {
    bg: 'bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-950 dark:to-emerald-900',
    text: 'text-green-900 dark:text-green-100',
    accent: 'text-emerald-600 dark:text-emerald-400',
  },
  soft_pastel: {
    bg: 'bg-gradient-to-br from-pink-100 via-purple-100 to-blue-100 dark:from-pink-950 dark:via-purple-950 dark:to-blue-950',
    text: 'text-purple-900 dark:text-purple-100',
    accent: 'text-pink-600 dark:text-pink-400',
  },
  // 创意活力
  creative_colorful: {
    bg: 'bg-gradient-to-br from-yellow-400 via-red-500 to-pink-500',
    text: 'text-white',
    accent: 'text-yellow-100',
  },
  warm_sunset: {
    bg: 'bg-gradient-to-br from-orange-400 via-red-400 to-pink-400',
    text: 'text-white',
    accent: 'text-orange-100',
  },
  // 二次元/动漫主题
  anime_dark: {
    bg: 'bg-gradient-to-br from-slate-900 via-purple-900 to-pink-900',
    text: 'text-pink-50',
    accent: 'text-cyan-400',
  },
  anime_cute: {
    bg: 'bg-gradient-to-br from-pink-200 via-purple-200 to-blue-200 dark:from-pink-900 dark:via-purple-900 dark:to-blue-900',
    text: 'text-purple-900 dark:text-purple-100',
    accent: 'text-pink-500 dark:text-pink-400',
  },
  cyberpunk: {
    bg: 'bg-gradient-to-br from-purple-900 via-cyan-800 to-pink-800',
    text: 'text-cyan-50',
    accent: 'text-pink-400',
  },
  eva_nerv: {
    bg: 'bg-gradient-to-br from-purple-800 via-green-700 to-orange-600',
    text: 'text-green-50',
    accent: 'text-orange-400',
  },
  retro_pixel: {
    bg: 'bg-gradient-to-br from-indigo-800 via-purple-700 to-pink-600',
    text: 'text-green-300',
    accent: 'text-yellow-400',
  },
  // 兼容旧主题名称
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

const LAYOUT_TEMPLATES: Record<string, string> = {
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
  const layoutClass = LAYOUT_TEMPLATES[slide.layout || 'bullet_points'] || LAYOUT_TEMPLATES.bullet_points;

  // Parse content into bullet points - 处理 \n 和实际换行符
  const contentLines = slide.content
    .replace(/\\n/g, '\n')
    .split('\n')
    .filter(line => line.trim());

  // 获取幻灯片图片
  const slideImages = slide.images || [];
  const hasImages = slideImages.length > 0;

  return (
    <div
      className={cn(
        'aspect-video rounded-lg shadow-lg p-8 flex flex-col justify-center overflow-hidden',
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

        {/* Content with optional image */}
        <div className={cn(hasImages && 'flex gap-6')}>
          {/* Text content */}
          <div className={cn(hasImages && 'flex-1')}>
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
          </div>

          {/* Images */}
          {hasImages && (
            <div className="flex-shrink-0 w-1/3">
              {slideImages.slice(0, 1).map((img, i) => (
                <img
                  key={i}
                  src={img.url}
                  alt={img.alt || `Slide image ${i + 1}`}
                  className="w-full h-auto rounded-lg shadow-md object-cover max-h-48"
                  onError={(e) => {
                    // 图片加载失败时隐藏
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              ))}
            </div>
          )}
        </div>

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
