'use client';

// ============================================================
// Slide Editor Component
// ============================================================

import React, { useState } from 'react';
import { Wand2, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import type { Slide, SlideLayout } from '@/lib/types/presentations';

interface SlideEditorProps {
  slide: Slide;
  slideIndex: number;
  totalSlides: number;
  onChange: (data: Partial<Slide>) => void;
  onAddSlide: () => void;
  onDeleteSlide: () => void;
  canDelete: boolean;
}

const LAYOUT_OPTIONS: { value: Slide['layout']; label: string; description: string }[] = [
  { value: 'title_cover', label: '封面页', description: '演示文稿首页，包含大标题' },
  { value: 'title_section', label: '章节页', description: '新章节开始页' },
  { value: 'bullet_points', label: '列表页', description: '要点列表布局' },
  { value: 'two_column', label: '双栏布局', description: '左右两栏内容' },
  { value: 'image_text', label: '图文混排', description: '图片和文字组合' },
  { value: 'quote_center', label: '引用页', description: '居中引用内容' },
  { value: 'thank_you', label: '结尾页', description: '感谢和问答页' },
];

export function SlideEditor({
  slide,
  slideIndex,
  totalSlides,
  onChange,
  onAddSlide,
  onDeleteSlide,
  canDelete,
}: SlideEditorProps) {
  const [activeTab, setActiveTab] = useState<'content' | 'style' | 'notes'>('content');

  const handleContentChange = (content: string) => {
    onChange({ content });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">幻灯片 {slideIndex + 1} / {totalSlides}</span>
        </div>
      </div>

      {/* Title Input */}
      <div className="space-y-2">
        <label className="text-sm font-medium">标题</label>
        <Input
          value={slide.title}
          onChange={(e) => onChange({ title: e.target.value })}
          placeholder="输入幻灯片标题..."
          className="text-lg"
        />
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="content">内容</TabsTrigger>
          <TabsTrigger value="style">样式</TabsTrigger>
          <TabsTrigger value="notes">备注</TabsTrigger>
        </TabsList>

        {/* Content Tab */}
        <TabsContent value="content" className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">
              内容
              <span className="text-muted-foreground font-normal ml-2">
                (使用 \\n 分行)
              </span>
            </label>
            <Textarea
              value={slide.content}
              onChange={(e) => handleContentChange(e.target.value)}
              placeholder="- 要点一\\n- 要点二\\n- 要点三"
              rows={10}
              className="font-mono text-sm"
            />
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const newContent = slide.content + '\\n- 新要点';
                onChange({ content: newContent });
              }}
            >
              添加要点
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const newContent = slide.content.split('\\n')
                  .filter(line => line.trim())
                  .join('\\n');
                onChange({ content: newContent || '- 新要点' });
              }}
            >
              清除空行
            </Button>
          </div>
        </TabsContent>

        {/* Style Tab */}
        <TabsContent value="style" className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">布局类型</label>
            <Select
              value={slide.layout || 'bullet_points'}
              onValueChange={(value) => onChange({ layout: value as Slide['layout'] })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LAYOUT_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <div className="flex flex-col">
                      <span>{option.label}</span>
                      <span className="text-xs text-muted-foreground">{option.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Layout Preview */}
          <div className="p-4 border rounded-lg bg-muted/20">
            <p className="text-sm text-muted-foreground mb-2">布局预览说明</p>
            <p className="text-sm">
              {LAYOUT_OPTIONS.find(o => o.value === (slide.layout || 'bullet_points'))?.description}
            </p>
          </div>
        </TabsContent>

        {/* Notes Tab */}
        <TabsContent value="notes" className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-1">
              <HelpCircle className="h-4 w-4" />
              演讲者备注
            </label>
            <p className="text-xs text-muted-foreground">
              这些备注仅供演讲者查看，不会在演示时显示
            </p>
            <Textarea
              value={slide.notes || ''}
              onChange={(e) => onChange({ notes: e.target.value })}
              placeholder="添加演讲备注..."
              rows={6}
            />
          </div>
        </TabsContent>
      </Tabs>

      {/* Slide Actions */}
      <div className="flex gap-2 pt-4 border-t">
        <Button
          variant="outline"
          onClick={onAddSlide}
          className="flex-1"
        >
          在后面添加幻灯片
        </Button>
        <Button
          variant="outline"
          onClick={onDeleteSlide}
          disabled={!canDelete}
          className="text-destructive hover:text-destructive"
        >
          删除此幻灯片
        </Button>
      </div>
    </div>
  );
}
