'use client';

// ============================================================
// Slide Preview Component
// Phase 5.10 美学优化版本
// - 移除随机图片，专注纯文字布局
// - 优化封面页布局：标题居中，副标题下方
// - 增强视觉层次：标题字体、列表间距、装饰元素
// - 移除"演讲者备注可用"提示
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
const THEME_STYLES: Record<string, {
  bg: string;
  text: string;
  accent: string;
  decorLine?: string;  // 装饰线颜色
}> = {
  // 商务专业
  modern_business: {
    bg: 'bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-blue-950',
    text: 'text-gray-900 dark:text-gray-100',
    accent: 'text-blue-600 dark:text-blue-400',
    decorLine: 'bg-blue-500',
  },
  corporate_blue: {
    bg: 'bg-gradient-to-br from-blue-600 to-blue-800',
    text: 'text-white',
    accent: 'text-blue-200',
    decorLine: 'bg-blue-300',
  },
  elegant_dark: {
    bg: 'bg-gradient-to-br from-gray-900 via-gray-800 to-amber-900',
    text: 'text-amber-50',
    accent: 'text-amber-400',
    decorLine: 'bg-amber-500',
  },
  academic_classic: {
    bg: 'bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-900 dark:to-slate-800',
    text: 'text-slate-900 dark:text-slate-100',
    accent: 'text-slate-700 dark:text-slate-300',
    decorLine: 'bg-slate-500',
  },
  // 科技创新
  dark_tech: {
    bg: 'bg-gradient-to-br from-gray-900 to-emerald-900',
    text: 'text-emerald-50',
    accent: 'text-emerald-400',
    decorLine: 'bg-emerald-500',
  },
  gradient_purple: {
    bg: 'bg-gradient-to-br from-purple-600 via-pink-500 to-orange-400',
    text: 'text-white',
    accent: 'text-yellow-200',
    decorLine: 'bg-yellow-300',
  },
  neon_future: {
    bg: 'bg-gradient-to-br from-violet-900 via-purple-800 to-fuchsia-900',
    text: 'text-fuchsia-50',
    accent: 'text-cyan-400',
    decorLine: 'bg-cyan-400',
  },
  // 简约清新
  minimal_white: {
    bg: 'bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800',
    text: 'text-gray-900 dark:text-gray-100',
    accent: 'text-gray-600 dark:text-gray-400',
    decorLine: 'bg-gray-400',
  },
  nature_green: {
    bg: 'bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-950 dark:to-emerald-900',
    text: 'text-green-900 dark:text-green-100',
    accent: 'text-emerald-600 dark:text-emerald-400',
    decorLine: 'bg-emerald-500',
  },
  soft_pastel: {
    bg: 'bg-gradient-to-br from-pink-100 via-purple-100 to-blue-100 dark:from-pink-950 dark:via-purple-950 dark:to-blue-950',
    text: 'text-purple-900 dark:text-purple-100',
    accent: 'text-pink-600 dark:text-pink-400',
    decorLine: 'bg-pink-400',
  },
  // 创意活力
  creative_colorful: {
    bg: 'bg-gradient-to-br from-yellow-400 via-red-500 to-pink-500',
    text: 'text-white',
    accent: 'text-yellow-100',
    decorLine: 'bg-white',
  },
  warm_sunset: {
    bg: 'bg-gradient-to-br from-orange-400 via-red-400 to-pink-400',
    text: 'text-white',
    accent: 'text-orange-100',
    decorLine: 'bg-white',
  },
  // 二次元/动漫主题
  anime_dark: {
    bg: 'bg-gradient-to-br from-slate-900 via-purple-900 to-pink-900',
    text: 'text-pink-50',
    accent: 'text-cyan-400',
    decorLine: 'bg-cyan-400',
  },
  anime_cute: {
    bg: 'bg-gradient-to-br from-pink-200 via-purple-200 to-blue-200 dark:from-pink-900 dark:via-purple-900 dark:to-blue-900',
    text: 'text-purple-900 dark:text-purple-100',
    accent: 'text-pink-500 dark:text-pink-400',
    decorLine: 'bg-pink-400',
  },
  cyberpunk: {
    bg: 'bg-gradient-to-br from-purple-900 via-cyan-800 to-pink-800',
    text: 'text-cyan-50',
    accent: 'text-pink-400',
    decorLine: 'bg-pink-500',
  },
  eva_nerv: {
    bg: 'bg-gradient-to-br from-purple-800 via-green-700 to-orange-600',
    text: 'text-green-50',
    accent: 'text-orange-400',
    decorLine: 'bg-orange-500',
  },
  retro_pixel: {
    bg: 'bg-gradient-to-br from-indigo-800 via-purple-700 to-pink-600',
    text: 'text-green-300',
    accent: 'text-yellow-400',
    decorLine: 'bg-yellow-400',
  },
  // 兼容旧主题名称
  creative: {
    bg: 'bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 dark:from-purple-950 dark:via-pink-950 dark:to-orange-950',
    text: 'text-gray-900 dark:text-gray-100',
    accent: 'text-purple-600 dark:text-purple-400',
    decorLine: 'bg-purple-400',
  },
  minimalist: {
    bg: 'bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800',
    text: 'text-gray-900 dark:text-gray-100',
    accent: 'text-gray-600 dark:text-gray-400',
    decorLine: 'bg-gray-400',
  },
  dark_professional: {
    bg: 'bg-gradient-to-br from-gray-900 to-gray-800',
    text: 'text-gray-100',
    accent: 'text-emerald-400',
    decorLine: 'bg-emerald-500',
  },
  colorful: {
    bg: 'bg-gradient-to-br from-yellow-50 via-green-50 to-blue-50 dark:from-yellow-950 dark:via-green-950 dark:to-blue-950',
    text: 'text-gray-900 dark:text-gray-100',
    accent: 'text-teal-600 dark:text-teal-400',
    decorLine: 'bg-teal-500',
  },
  academic: {
    bg: 'bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900',
    text: 'text-slate-900 dark:text-slate-100',
    accent: 'text-slate-700 dark:text-slate-300',
    decorLine: 'bg-slate-500',
  },
};

export function SlidePreview({ slide, theme, className }: SlidePreviewProps) {
  const themeStyle = THEME_STYLES[theme] || THEME_STYLES.modern_business;

  // Parse content into bullet points - 处理 \n 和实际换行符
  const contentLines = slide.content
    .replace(/\\n/g, '\n')
    .split('\n')
    .filter(line => line.trim());

  // 判断是否为封面页或章节页
  const isCoverPage = slide.layout === 'title_cover';
  const isSectionPage = slide.layout === 'title_section';
  const isQuotePage = slide.layout === 'quote_center';
  const isThankYouPage = slide.layout === 'thank_you';

  return (
    <div
      className={cn(
        'aspect-video rounded-lg shadow-lg overflow-hidden relative',
        themeStyle.bg,
        themeStyle.text,
        className
      )}
      style={{
        background: slide.background || undefined,
      }}
    >
      {/* 封面页布局 */}
      {isCoverPage && (
        <div className="h-full flex flex-col items-center justify-center px-12 py-8">
          {/* 装饰线 - 上 */}
          <div className={cn('w-24 h-1 rounded-full mb-8', themeStyle.decorLine)} />

          {/* 主标题 */}
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-center mb-6 leading-tight">
            {slide.title}
          </h1>

          {/* 副标题/内容 */}
          {contentLines.length > 0 && (
            <div className="text-center space-y-2 mt-4">
              {contentLines.map((line, i) => (
                <p
                  key={i}
                  className={cn(
                    'text-lg md:text-xl opacity-80',
                    themeStyle.accent
                  )}
                >
                  {line.replace(/^- /gm, '')}
                </p>
              ))}
            </div>
          )}

          {/* 装饰线 - 下 */}
          <div className={cn('w-16 h-1 rounded-full mt-8', themeStyle.decorLine, 'opacity-60')} />
        </div>
      )}

      {/* 章节页布局 */}
      {isSectionPage && (
        <div className="h-full flex flex-col items-center justify-center px-12 py-8">
          {/* 章节标题 */}
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-center mb-4">
            {slide.title}
          </h1>

          {/* 装饰线 */}
          <div className={cn('w-32 h-1 rounded-full my-6', themeStyle.decorLine)} />

          {/* 章节描述 */}
          {contentLines.length > 0 && (
            <div className="text-center space-y-2">
              {contentLines.map((line, i) => (
                <p
                  key={i}
                  className={cn('text-lg md:text-xl opacity-70', themeStyle.accent)}
                >
                  {line.replace(/^- /gm, '')}
                </p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 引用页布局 */}
      {isQuotePage && (
        <div className="h-full flex flex-col items-center justify-center px-16 py-8">
          {/* 引号装饰 */}
          <span className={cn('text-6xl opacity-30 mb-4', themeStyle.accent)}>"</span>

          {/* 引用内容 */}
          <blockquote className="text-2xl md:text-3xl italic text-center leading-relaxed opacity-90 max-w-4xl">
            {slide.content.replace(/^- /gm, '').replace(/\\n/g, ' ')}
          </blockquote>

          {/* 引用来源 */}
          {slide.title && slide.title !== '引用' && (
            <p className={cn('mt-6 text-lg opacity-60', themeStyle.accent)}>
              — {slide.title}
            </p>
          )}
        </div>
      )}

      {/* 感谢页布局 */}
      {isThankYouPage && (
        <div className="h-full flex flex-col items-center justify-center px-12 py-8">
          {/* 装饰线 */}
          <div className={cn('w-24 h-1 rounded-full mb-8', themeStyle.decorLine)} />

          {/* 感谢标题 */}
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-center mb-4">
            {slide.title || '感谢观看'}
          </h1>

          {/* 副标题 */}
          {contentLines.length > 0 && (
            <div className="text-center space-y-2 mt-4">
              {contentLines.map((line, i) => (
                <p
                  key={i}
                  className={cn('text-lg md:text-xl opacity-70', themeStyle.accent)}
                >
                  {line.replace(/^- /gm, '')}
                </p>
              ))}
            </div>
          )}

          {/* 装饰线 */}
          <div className={cn('w-16 h-1 rounded-full mt-8', themeStyle.decorLine, 'opacity-60')} />
        </div>
      )}

      {/* 普通内容页布局 (bullet_points, two_column, image_text 等) */}
      {!isCoverPage && !isSectionPage && !isQuotePage && !isThankYouPage && (
        <div className="h-full flex flex-col px-10 py-8">
          {/* 标题区域 */}
          <div className="mb-6">
            <h2 className="text-2xl md:text-3xl font-bold mb-3">
              {slide.title}
            </h2>
            {/* 标题下装饰线 */}
            <div className={cn('w-16 h-1 rounded-full', themeStyle.decorLine)} />
          </div>

          {/* 内容区域 - 优化间距和排版 */}
          <div className="flex-1 overflow-hidden">
            <ul className="space-y-4">
              {contentLines.map((line, i) => (
                <li
                  key={i}
                  className="flex items-start text-lg leading-relaxed"
                >
                  {/* 自定义列表标记 */}
                  <span className={cn(
                    'inline-block w-2 h-2 rounded-full mt-2.5 mr-4 flex-shrink-0',
                    themeStyle.decorLine
                  )} />
                  <span className={cn('flex-1', themeStyle.accent)}>
                    {line.replace(/^- /gm, '')}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* 页码指示器 (非封面页显示) */}
      {!isCoverPage && (
        <div className="absolute bottom-4 right-6 text-xs opacity-30">
          •
        </div>
      )}
    </div>
  );
}
