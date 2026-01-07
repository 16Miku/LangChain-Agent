'use client';

// ============================================================
// Theme Selector Component
// 支持 17 种主题，包括 5 种二次元/动漫主题
// ============================================================

import React from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { PresentationTheme } from '@/lib/types/presentations';

interface ThemeSelectorProps {
  currentTheme: PresentationTheme;
  onThemeChange: (theme: PresentationTheme) => void;
}

interface ThemeOption {
  value: PresentationTheme;
  label: string;
  preview: string;
  category: 'business' | 'tech' | 'creative' | 'anime';
}

const THEMES: ThemeOption[] = [
  // 商务专业
  {
    value: 'modern_business',
    label: '现代商务',
    preview: 'from-blue-50 to-indigo-100',
    category: 'business',
  },
  {
    value: 'corporate_blue',
    label: '企业蓝',
    preview: 'from-blue-600 to-blue-800',
    category: 'business',
  },
  {
    value: 'elegant_dark',
    label: '典雅深色',
    preview: 'from-gray-900 via-gray-800 to-amber-900',
    category: 'business',
  },
  // 科技创新
  {
    value: 'dark_tech',
    label: '科技深色',
    preview: 'from-gray-900 to-emerald-900',
    category: 'tech',
  },
  {
    value: 'gradient_purple',
    label: '渐变紫',
    preview: 'from-purple-600 via-pink-500 to-orange-400',
    category: 'tech',
  },
  {
    value: 'neon_future',
    label: '霓虹未来',
    preview: 'from-violet-900 via-purple-800 to-fuchsia-900',
    category: 'tech',
  },
  // 简约清新
  {
    value: 'minimal_white',
    label: '极简白',
    preview: 'bg-white border border-gray-200',
    category: 'creative',
  },
  {
    value: 'nature_green',
    label: '自然绿',
    preview: 'from-green-50 to-emerald-100',
    category: 'creative',
  },
  {
    value: 'soft_pastel',
    label: '柔和粉彩',
    preview: 'from-pink-100 via-purple-100 to-blue-100',
    category: 'creative',
  },
  // 创意活力
  {
    value: 'creative_colorful',
    label: '创意多彩',
    preview: 'from-yellow-400 via-red-500 to-pink-500',
    category: 'creative',
  },
  {
    value: 'warm_sunset',
    label: '暖阳落日',
    preview: 'from-orange-400 via-red-400 to-pink-400',
    category: 'creative',
  },
  {
    value: 'academic_classic',
    label: '学术经典',
    preview: 'from-slate-100 to-slate-200',
    category: 'business',
  },
  // 二次元/动漫主题
  {
    value: 'anime_dark',
    label: '二次元暗黑',
    preview: 'from-slate-900 via-purple-900 to-pink-900',
    category: 'anime',
  },
  {
    value: 'anime_cute',
    label: '二次元可爱',
    preview: 'from-pink-200 via-purple-200 to-blue-200',
    category: 'anime',
  },
  {
    value: 'cyberpunk',
    label: '赛博朋克',
    preview: 'from-purple-900 via-cyan-800 to-pink-800',
    category: 'anime',
  },
  {
    value: 'eva_nerv',
    label: 'EVA NERV',
    preview: 'from-purple-800 via-green-600 to-orange-600',
    category: 'anime',
  },
  {
    value: 'retro_pixel',
    label: '复古像素',
    preview: 'from-indigo-800 via-purple-700 to-pink-600',
    category: 'anime',
  },
];

const CATEGORY_LABELS: Record<ThemeOption['category'], string> = {
  business: '商务专业',
  tech: '科技创新',
  creative: '简约创意',
  anime: '二次元/动漫',
};

export function ThemeSelector({ currentTheme, onThemeChange }: ThemeSelectorProps) {
  // 按类别分组
  const groupedThemes = THEMES.reduce((acc, theme) => {
    if (!acc[theme.category]) {
      acc[theme.category] = [];
    }
    acc[theme.category].push(theme);
    return acc;
  }, {} as Record<ThemeOption['category'], ThemeOption[]>);

  return (
    <div className="space-y-6 max-h-[60vh] overflow-y-auto pr-2">
      {(Object.keys(groupedThemes) as ThemeOption['category'][]).map((category) => (
        <div key={category}>
          <h3 className="text-sm font-medium text-muted-foreground mb-3">
            {CATEGORY_LABELS[category]}
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {groupedThemes[category].map((theme) => (
              <button
                key={theme.value}
                onClick={() => onThemeChange(theme.value)}
                className={cn(
                  'relative rounded-lg border-2 p-3 text-left transition-all',
                  currentTheme === theme.value
                    ? 'border-primary ring-2 ring-primary/20'
                    : 'border-border hover:border-primary/50'
                )}
              >
                {/* Theme Preview */}
                <div
                  className={cn(
                    'h-16 rounded-md mb-2 bg-gradient-to-br',
                    theme.preview,
                    theme.value === 'minimal_white' && theme.preview
                  )}
                />

                {/* Theme Label */}
                <div className="flex items-center justify-between">
                  <span className="font-medium text-sm">{theme.label}</span>
                  {currentTheme === theme.value && (
                    <Check className="h-4 w-4 text-primary" />
                  )}
                </div>

                {/* Theme Value */}
                <p className="text-xs text-muted-foreground mt-0.5">
                  {theme.value}
                </p>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
