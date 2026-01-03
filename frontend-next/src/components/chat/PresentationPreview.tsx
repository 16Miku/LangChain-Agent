'use client';

// ============================================================
// Presentation Preview Component - Reveal.js PPT Viewer
// ============================================================

import { useState, useCallback, useMemo } from 'react';
import {
  Maximize2,
  Minimize2,
  ExternalLink,
  Download,
  X,
  FileText,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface PresentationPreviewProps {
  htmlBase64: string;
  className?: string;
}

/**
 * Extract [PRESENTATION_HTML:...] markers from text and render them
 */
export function PresentationExtractor({
  content,
  className,
}: {
  content: string;
  className?: string;
}) {
  // Extract presentation HTML base64 data
  const regex = /\[PRESENTATION_HTML:([A-Za-z0-9+/=]+)\]/g;
  const matches = [...content.matchAll(regex)];

  if (matches.length === 0) {
    return null;
  }

  return (
    <div className={cn('space-y-4', className)}>
      {matches.map((match, index) => (
        <PresentationPreview key={index} htmlBase64={match[1]} />
      ))}
    </div>
  );
}

/**
 * Preview a Reveal.js presentation from base64-encoded HTML
 */
export function PresentationPreview({
  htmlBase64,
  className,
}: PresentationPreviewProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Decode HTML from base64 (handle UTF-8 correctly)
  const htmlContent = useMemo(() => {
    try {
      // Decode base64 to binary string, then to UTF-8
      const binaryString = atob(htmlBase64);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      return new TextDecoder('utf-8').decode(bytes);
    } catch {
      return null;
    }
  }, [htmlBase64]);

  // Create blob URL for iframe (memoized)
  const blobUrl = useMemo(() => {
    if (!htmlContent) return null;
    const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
    return URL.createObjectURL(blob);
  }, [htmlContent]);

  // Handle decoding error
  if (!htmlContent || !blobUrl) {
    return (
      <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-500">
        Failed to decode presentation HTML
      </div>
    );
  }

  // Download the presentation
  const handleDownload = () => {
    const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'presentation.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Open in new tab
  const handleOpenNewTab = () => {
    const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  // Handle iframe load
  const handleIframeLoad = () => {
    setIsLoading(false);
  };

  return (
    <>
      {/* Inline Preview */}
      <div
        className={cn(
          'group relative overflow-hidden rounded-lg border bg-background',
          className
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b bg-muted/50 px-3 py-2">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">演示文稿预览</span>
          </div>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={handleDownload}
              title="下载 HTML"
            >
              <Download className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={handleOpenNewTab}
              title="在新标签页打开"
            >
              <ExternalLink className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={() => setIsFullscreen(true)}
              title="全屏"
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Preview iframe */}
        <div className="relative aspect-video w-full">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-muted">
              <div className="flex flex-col items-center gap-2">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                <span className="text-sm text-muted-foreground">
                  加载演示文稿...
                </span>
              </div>
            </div>
          )}
          <iframe
            src={blobUrl}
            className="h-full w-full border-0"
            sandbox="allow-scripts allow-same-origin"
            onLoad={handleIframeLoad}
            title="Presentation Preview"
          />
        </div>

        {/* Tips */}
        <div className="border-t bg-muted/30 px-3 py-1.5">
          <p className="text-xs text-muted-foreground">
            使用方向键或空格键导航。按 F 全屏，按 S 打开演讲者备注。
          </p>
        </div>
      </div>

      {/* Fullscreen Modal */}
      {isFullscreen && (
        <div className="fixed inset-0 z-50 bg-black">
          {/* Close button */}
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-4 top-4 z-10 h-10 w-10 rounded-full bg-white/10 text-white hover:bg-white/20"
            onClick={() => setIsFullscreen(false)}
          >
            <X className="h-5 w-5" />
          </Button>

          {/* Minimize button */}
          <Button
            variant="ghost"
            size="icon"
            className="absolute left-4 top-4 z-10 h-10 w-10 rounded-full bg-white/10 text-white hover:bg-white/20"
            onClick={() => setIsFullscreen(false)}
            title="退出全屏"
          >
            <Minimize2 className="h-5 w-5" />
          </Button>

          {/* Fullscreen iframe */}
          <iframe
            src={blobUrl}
            className="h-full w-full border-0"
            sandbox="allow-scripts allow-same-origin"
            title="Presentation Fullscreen"
          />
        </div>
      )}
    </>
  );
}
