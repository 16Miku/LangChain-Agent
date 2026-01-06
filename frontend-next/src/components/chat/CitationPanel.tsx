'use client';

// ============================================================
// Citation Panel Component - 引用追溯展示
// ============================================================

import { useState, useCallback } from 'react';
import {
  FileText,
  ChevronDown,
  ChevronRight,
  BookOpen,
  Hash,
  Loader2,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { ragApi, type CitationDetail } from '@/lib/api/rag';

export interface CitationInfo {
  chunkId: string;
  documentId: string;
  documentName: string;
  pageNumber?: number;
  section?: string;
  content: string;
  contentPreview?: string;
  score: number;
}

interface CitationPanelProps {
  citations: CitationInfo[];
  className?: string;
}

export function CitationPanel({ citations, className }: CitationPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [expandedCitation, setExpandedCitation] = useState<string | null>(null);
  const [citationDetails, setCitationDetails] = useState<Record<string, CitationDetail>>({});
  const [loadingDetail, setLoadingDetail] = useState<string | null>(null);

  // 加载引用详情（包含上下文）
  const loadCitationDetail = useCallback(async (chunkId: string) => {
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
  }, [citationDetails, expandedCitation]);

  if (!citations || citations.length === 0) {
    return null;
  }

  return (
    <div className={cn('rounded-lg border bg-card text-card-foreground', className)}>
      {/* Header */}
      <button
        className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-muted/50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-primary" />
          <span className="font-medium text-sm">引用来源</span>
          <span className="text-xs text-muted-foreground">({citations.length})</span>
        </div>
        {isExpanded ? (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
        )}
      </button>

      {/* Citation List */}
      {isExpanded && (
        <div className="border-t">
          {citations.map((citation, index) => (
            <CitationItem
              key={citation.chunkId}
              citation={citation}
              index={index}
              isExpanded={expandedCitation === citation.chunkId}
              isLoading={loadingDetail === citation.chunkId}
              detail={citationDetails[citation.chunkId]}
              onToggle={() => loadCitationDetail(citation.chunkId)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================
// Citation Item Component - 单条引用
// ============================================================

interface CitationItemProps {
  citation: CitationInfo;
  index: number;
  isExpanded: boolean;
  isLoading: boolean;
  detail?: CitationDetail;
  onToggle: () => void;
}

function CitationItem({
  citation,
  index,
  isExpanded,
  isLoading,
  detail,
  onToggle,
}: CitationItemProps) {
  // 截取预览内容
  const preview = citation.contentPreview || citation.content.slice(0, 100) + '...';

  // 分数转换为百分比
  const scorePercent = Math.round(citation.score * 100);

  return (
    <div className={cn('border-b last:border-b-0', isExpanded && 'bg-muted/30')}>
      {/* Citation Header */}
      <button
        className="flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-muted/50 transition-colors"
        onClick={onToggle}
      >
        {/* Index Badge */}
        <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary text-xs font-medium">
          {index + 1}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Document Info */}
          <div className="flex items-center gap-2 mb-1">
            <FileText className="h-3 w-3 text-muted-foreground" />
            <span className="text-sm font-medium truncate">{citation.documentName}</span>
            {citation.pageNumber && (
              <span className="flex items-center gap-0.5 text-xs text-muted-foreground">
                <Hash className="h-3 w-3" />
                第 {citation.pageNumber} 页
              </span>
            )}
            {citation.section && (
              <span className="text-xs text-muted-foreground truncate">
                · {citation.section}
              </span>
            )}
          </div>

          {/* Preview */}
          <p className="text-xs text-muted-foreground line-clamp-2">{preview}</p>

          {/* Score Badge */}
          <div className="flex items-center gap-2 mt-2">
            <div
              className={cn(
                'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium',
                scorePercent >= 80
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                  : scorePercent >= 60
                  ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                  : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400'
              )}
            >
              相关度 {scorePercent}%
            </div>
          </div>
        </div>

        {/* Expand Icon */}
        <div className="shrink-0">
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          ) : isExpanded ? (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
      </button>

      {/* Expanded Detail */}
      {isExpanded && detail && (
        <div className="px-4 pb-4">
          <CitationDetailView detail={detail} />
        </div>
      )}
    </div>
  );
}

// ============================================================
// Citation Detail View - 引用详情展示
// ============================================================

interface CitationDetailViewProps {
  detail: CitationDetail;
}

function CitationDetailView({ detail }: CitationDetailViewProps) {
  return (
    <div className="space-y-3 pl-8">
      {/* Context: Previous Chunks */}
      {detail.prevChunks && detail.prevChunks.length > 0 && (
        <div className="rounded-lg border border-dashed border-muted-foreground/30 p-3">
          <div className="text-xs text-muted-foreground mb-2">前文</div>
          {detail.prevChunks.map((chunk, idx) => (
            <p key={idx} className="text-xs text-muted-foreground/70">
              {chunk}
            </p>
          ))}
        </div>
      )}

      {/* Main Content */}
      <div className="rounded-lg bg-primary/5 border border-primary/20 p-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-primary">引用内容</span>
          <span className="text-xs text-muted-foreground">
            分块 {detail.chunkIndex + 1} / {detail.totalChunks}
          </span>
        </div>
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{detail.content}</p>
      </div>

      {/* Context: Next Chunks */}
      {detail.nextChunks && detail.nextChunks.length > 0 && (
        <div className="rounded-lg border border-dashed border-muted-foreground/30 p-3">
          <div className="text-xs text-muted-foreground mb-2">后文</div>
          {detail.nextChunks.map((chunk, idx) => (
            <p key={idx} className="text-xs text-muted-foreground/70">
              {chunk}
            </p>
          ))}
        </div>
      )}

      {/* Metadata */}
      {detail.metadata && Object.keys(detail.metadata).length > 0 && (
        <div className="rounded-lg bg-muted/50 p-3">
          <div className="text-xs text-muted-foreground mb-2">元数据</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {Object.entries(detail.metadata).map(([key, value]) => (
              <div key={key} className="flex items-center gap-1">
                <span className="text-muted-foreground">{key}:</span>
                <span className="font-medium">{String(value)}</span>
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
        'inline-flex items-center gap-1 rounded-md bg-primary/10 px-1.5 py-0.5 text-xs font-medium text-primary hover:bg-primary/20 transition-colors',
        className
      )}
    >
      <span>[{index}]</span>
      <span className="max-w-[100px] truncate">{documentName}</span>
      {pageNumber && <span>p.{pageNumber}</span>}
    </button>
  );
}
