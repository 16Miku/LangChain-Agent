'use client';

// ============================================================
// Theme Selector Component
// ============================================================

import React from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { PresentationTheme } from '@/lib/types/presentations';

interface ThemeSelectorProps {
  currentTheme: PresentationTheme;
  onThemeChange: (theme: PresentationTheme) => void;
}

const THEMES: { value: PresentationTheme; label: string; preview: string }[] = [
  {
    value: 'modern_business',
    label: '现代商务',
    preview: 'from-blue-50 to-indigo-100',
  },
  {
    value: 'creative',
    label: '创意设计',
    preview: 'from-purple-50 via-pink-50 to-orange-50',
  },
  {
    value: 'minimalist',
    label: '极简主义',
    preview: 'bg-white border border-gray-200',
  },
  {
    value: 'dark_professional',
    label: '暗色专业',
    preview: 'from-gray-900 to-gray-800',
  },
  {
    value: 'colorful',
    label: '多彩活泼',
    preview: 'from-yellow-50 via-green-50 to-blue-50',
  },
  {
    value: 'academic',
    label: '学术风格',
    preview: 'from-slate-50 to-slate-100',
  },
];

export function ThemeSelector({ currentTheme, onThemeChange }: ThemeSelectorProps) {
  return (
    <div className="grid grid-cols-2 gap-4">
      {THEMES.map((theme) => (
        <button
          key={theme.value}
          onClick={() => onThemeChange(theme.value)}
          className={cn(
            'relative rounded-lg border-2 p-4 text-left transition-all',
            currentTheme === theme.value
              ? 'border-primary ring-2 ring-primary/20'
              : 'border-border hover:border-primary/50'
          )}
        >
          {/* Theme Preview */}
          <div
            className={cn(
              'h-20 rounded-md mb-3 bg-gradient-to-br',
              theme.preview,
              theme.value === 'minimalist' && theme.preview
            )}
          />

          {/* Theme Label */}
          <div className="flex items-center justify-between">
            <span className="font-medium">{theme.label}</span>
            {currentTheme === theme.value && (
              <Check className="h-5 w-5 text-primary" />
            )}
          </div>

          {/* Theme Value */}
          <p className="text-xs text-muted-foreground mt-1">
            {theme.value}
          </p>
        </button>
      ))}
    </div>
  );
}
