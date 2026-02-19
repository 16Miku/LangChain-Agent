'use client';

// ============================================================
// Citation Panel Component - 引用追溯展示 (V10 优化版)
// ============================================================

import { useState, useCallback, useMemo } from 'react';
import {
  FileText,
  File,
  ChevronDown,
  ChevronRight,
  BookOpen,
  Hash,
  Loader2,
  Copy,
  Check,
  ExternalLink,
  Quote,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { ragApi, type CitationDetail } from '@/lib/api/rag';
import { Button } from '@/components/ui/button';

export interface CitationInfo {
  chunkId: string;
  documentId: string;
  documentName: string;
  pageNumber?: number;
  section?: string;
  content: string;
  contentPreview?: string;
  score: number;
  highlightRanges?: Array<{ start: number; end: number }>;
  metadata?: Record<string, unknown>;
}

interface CitationPanelProps {
  citations: CitationInfo[];
  className?: string;
  onCitationClick?: (citation: CitationInfo) => void;
}

export function CitationPanel({ citations, className, onCitationClick }: CitationPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [expandedCitation, setExpandedCitation] = useState<string | null>(null);
  const [citationDetails, setCitationDetails] = useState<Record<string, CitationDetail>>({});
  const [loadingDetail, setLoadingDetail] = useState<string | null>(null);

  // 加载引用详情（包含上下文）
  const loadCitationDetail = useCallback(
    async (chunkId: string) => {
      if (citationDetails[chunkId]) {
        // 已加载，直接展开/收起
        setExpandedCitation(expandedCitation === chunkId ? null : chunkId);
        return;
      }

      setLoadingDetail(chunkId);
      try {
        const detail = await ragApi.getCitationDetail(chunkId, 1);
        setCitationDetails((prev) => ({ ...prev, [chunkId]: detail }));
        setExpandedCitation(chunkId);
      } catch (error) {
        console.error('加载引用详情失败:', error);
        // 加载失败时仍然展开，显示错误提示
        setExpandedCitation(chunkId);
      } finally {
        setLoadingDetail(null);
      }
    },
    [citationDetails, expandedCitation]
  );

  if (!citations || citations.length === 0) {
    return null;
  }

  return (
    <div
      className={cn(
        'rounded-xl border border-border/50 bg-gradient-to-br from-card to-muted/20 shadow-sm',
        className
      )}
    >
      {/* Header */}
      <button
        className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-muted/30 transition-colors rounded-t-xl"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
            <BookOpen className="h-4 w-4 text-primary" />
          </div>
          <span className="font-medium text-sm">引用来源</span>
          <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
            {citations.length}
          </span>
        </div>
        <div
          className={cn(
            'flex h-6 w-6 items-center justify-center rounded-full transition-colors',
            isExpanded ? 'bg-muted' : 'bg-muted/50'
          )}
        >
          {isExpanded ? (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
      </button>

      {/* Citation List */}
      {isExpanded && (
        <div className="border-t border-border/50 p-3 space-y-2">
          {citations.map((citation, index) => (
            <CitationCard
              key={citation.chunkId}
              citation={citation}
              index={index}
              isExpanded={expandedCitation === citation.chunkId}
              isLoading={loadingDetail === citation.chunkId}
              detail={citationDetails[citation.chunkId]}
              onToggle={() => loadCitationDetail(citation.chunkId)}
              onClick={() => onCitationClick?.(citation)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================
// Citation Card Component - 单条引用卡片
// ============================================================

interface CitationCardProps {
  citation: CitationInfo;
  index: number;
  isExpanded: boolean;
  isLoading: boolean;
  detail?: CitationDetail;
  onToggle: () => void;
  onClick?: () => void;
}

function CitationCard({
  citation,
  index,
  isExpanded,
  isLoading,
  detail,
  onToggle,
  onClick,
}: CitationCardProps) {
  const [copied, setCopied] = useState(false);

  // 获取文件类型图标和颜色
  const fileTypeInfo = useMemo(() => {
    const ext = citation.documentName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf':
        return { icon: FileText, color: 'text-red-500', bg: 'bg-red-50 dark:bg-red-950/30' };
      case 'doc':
      case 'docx':
        return { icon: FileText, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-950/30' };
      case 'md':
      case 'txt':
        return { icon: File, color: 'text-gray-500', bg: 'bg-gray-50 dark:bg-gray-950/30' };
      default:
        return { icon: File, color: 'text-primary', bg: 'bg-primary/5' };
    }
  }, [citation.documentName]);

  const FileIcon = fileTypeInfo.icon;

  // 截取预览内容
  const preview = citation.contentPreview || citation.content.slice(0, 120) + '...';

  // 分数转换为百分比
  const scorePercent = Math.round(citation.score * 100);

  // 复制引用内容
  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(citation.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('复制失败:', err);
    }
  };

  // 获取相关度颜色
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    if (score >= 40) return 'bg-orange-500';
    return 'bg-gray-400';
  };

  return (
    <div
      className={cn(
        'group rounded-lg border border-border/50 bg-card transition-all duration-200',
        'hover:border-primary/30 hover:shadow-md',
        isExpanded && 'border-primary/30 shadow-sm'
      )}
    >
      {/* Card Header */}
      <div
        className={cn(
          'flex items-start gap-3 p-3 cursor-pointer',
          'transition-colors duration-150',
          'hover:bg-muted/30'
        )}
        onClick={onToggle}
      >
        {/* Index Badge with File Icon */}
        <div
          className={cn(
            'flex h-10 w-10 shrink-0 items-center justify-center rounded-lg',
            fileTypeInfo.bg
          )}
        >
          <FileIcon className={cn('h-5 w-5', fileTypeInfo.color)} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Document Name */}
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-sm font-medium truncate flex-1">
              {citation.documentName}
            </span>
            {/* Index Tag */}
            <span className="shrink-0 inline-flex items-center justify-center h-5 w-5 rounded-full bg-muted text-xs font-medium text-muted-foreground">
              {index + 1}
            </span>
          </div>

          {/* Page & Section Info */}
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            {citation.pageNumber && (
              <span className="inline-flex items-center gap-1 rounded-md bg-blue-50 dark:bg-blue-950/30 px-1.5 py-0.5 text-xs text-blue-600 dark:text-blue-400">
                <Hash className="h-3 w-3" />
                第 {citation.pageNumber} 页
              </span>
            )}
            {citation.section && (
              <span className="inline-flex items-center rounded-md bg-purple-50 dark:bg-purple-950/30 px-1.5 py-0.5 text-xs text-purple-600 dark:text-purple-400 truncate max-w-[150px]">
                {citation.section}
              </span>
            )}
          </div>

          {/* Content Preview - 显示完整内容 */}
          <div className="max-h-32 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-muted-foreground/20 scrollbar-track-transparent">
            <p className="text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap">
              {citation.content}
            </p>
          </div>

          {/* Score Progress Bar */}
          <div className="flex items-center gap-2 mt-2">
            <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
              <div
                className={cn('h-full rounded-full transition-all duration-300', getScoreColor(scorePercent))}
                style={{ width: `${scorePercent}%` }}
              />
            </div>
            <span className="text-xs font-medium text-muted-foreground shrink-0">
              {scorePercent}%
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col items-center gap-1 shrink-0">
          {/* Copy Button */}
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={handleCopy}
          >
            {copied ? (
              <Check className="h-3.5 w-3.5 text-green-500" />
            ) : (
              <Copy className="h-3.5 w-3.5" />
            )}
          </Button>

          {/* Expand Icon */}
          <div className="h-7 w-7 flex items-center justify-center">
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            ) : isExpanded ? (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            )}
          </div>
        </div>
      </div>

      {/* Expanded Detail */}
      {isExpanded && (
        <div className="border-t border-border/50 px-3 pb-3 pt-3">
          <CitationDetailView
            detail={detail}
            isLoading={isLoading}
            highlightRanges={citation.highlightRanges}
          />
        </div>
      )}
    </div>
  );
}

// ============================================================
// Citation Detail View - 引用详情展示
// ============================================================

interface CitationDetailViewProps {
  detail?: CitationDetail;
  isLoading?: boolean;
  highlightRanges?: Array<{ start: number; end: number }>;
}

function CitationDetailView({ detail, isLoading, highlightRanges }: CitationDetailViewProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-4">
        <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
        <span className="ml-2 text-sm text-muted-foreground">加载中...</span>
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="text-center py-4 text-sm text-muted-foreground">
        暂无详情
      </div>
    );
  }

  // 高亮处理函数
  const highlightContent = (content: string) => {
    if (!highlightRanges || highlightRanges.length === 0) {
      return content;
    }

    // 简单实现：将需要高亮的部分用 mark 标签包裹
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;

    highlightRanges.forEach((range, idx) => {
      if (range.start > lastIndex) {
        parts.push(content.slice(lastIndex, range.start));
      }
      parts.push(
        <mark key={idx} className="bg-yellow-200 dark:bg-yellow-800/50 rounded px-0.5">
          {content.slice(range.start, range.end)}
        </mark>
      );
      lastIndex = range.end;
    });

    if (lastIndex < content.length) {
      parts.push(content.slice(lastIndex));
    }

    return parts;
  };

  return (
    <div className="space-y-3">
      {/* Context: Previous Chunks */}
      {detail.prevChunks && detail.prevChunks.length > 0 && (
        <div className="rounded-lg border border-dashed border-muted-foreground/20 bg-muted/20 p-3">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-2">
            <Quote className="h-3 w-3" />
            <span>前文上下文</span>
          </div>
          <div className="text-xs text-muted-foreground/80 leading-relaxed">
            {detail.prevChunks.map((chunk, idx) => (
              <p key={idx} className="mb-1 last:mb-0">
                {chunk}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Main Content - 完整显示 */}
      <div className="rounded-lg bg-primary/5 border border-primary/20 p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Quote className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">完整引用内容</span>
          </div>
          <div className="flex items-center gap-2">
            {/* 位置信息 */}
            <span className="inline-flex items-center gap-1 rounded-md bg-blue-50 dark:bg-blue-950/30 px-2 py-0.5 text-xs text-blue-600 dark:text-blue-400">
              <Hash className="h-3 w-3" />
              分块 {detail.chunkIndex + 1} / {detail.totalChunks}
            </span>
            {detail.pageNumber && (
              <span className="inline-flex items-center gap-1 rounded-md bg-green-50 dark:bg-green-950/30 px-2 py-0.5 text-xs text-green-600 dark:text-green-400">
                <FileText className="h-3 w-3" />
                第 {detail.pageNumber} 页
              </span>
            )}
          </div>
        </div>
        {/* 完整内容显示区域 */}
        <div className="max-h-96 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-muted-foreground/20 scrollbar-track-transparent">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {highlightContent(detail.content)}
          </p>
        </div>
        {/* 字符统计 */}
        <div className="mt-2 pt-2 border-t border-primary/10 text-xs text-muted-foreground flex items-center justify-between">
          <span>内容长度：{detail.content.length} 字符</span>
          <span>分块 ID：{detail.chunkId.slice(0, 8)}...</span>
        </div>
      </div>

      {/* Context: Next Chunks */}
      {detail.nextChunks && detail.nextChunks.length > 0 && (
        <div className="rounded-lg border border-dashed border-muted-foreground/20 bg-muted/20 p-3">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-2">
            <Quote className="h-3 w-3 rotate-180" />
            <span>后文上下文</span>
          </div>
          <div className="text-xs text-muted-foreground/80 leading-relaxed">
            {detail.nextChunks.map((chunk, idx) => (
              <p key={idx} className="mb-1 last:mb-0">
                {chunk}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Metadata */}
      {detail.metadata && Object.keys(detail.metadata).length > 0 && (
        <div className="rounded-lg bg-muted/50 p-3">
          <div className="text-xs text-muted-foreground mb-2">元数据</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {Object.entries(detail.metadata).map(([key, value]) => (
              <div key={key} className="flex items-center gap-1.5">
                <span className="text-muted-foreground shrink-0">{key}:</span>
                <span className="font-medium truncate">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================
// Inline Citation Badge - 内联引用标记
// ============================================================

interface CitationBadgeProps {
  index: number;
  documentName: string;
  pageNumber?: number;
  onClick?: () => void;
  className?: string;
}

export function CitationBadge({
  index,
  documentName,
  pageNumber,
  onClick,
  className,
}: CitationBadgeProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-1 rounded-md bg-primary/10 px-1.5 py-0.5',
        'text-xs font-medium text-primary',
        'hover:bg-primary/20 hover:underline',
        'transition-colors',
        className
      )}
    >
      <span className="font-bold">[{index + 1}]</span>
      <span className="max-w-[100px] truncate">{documentName}</span>
      {pageNumber && (
        <span className="text-primary/70">p.{pageNumber}</span>
      )}
    </button>
  );
}
