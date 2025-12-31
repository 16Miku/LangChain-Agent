'use client';

// ============================================================
// Image Renderer Component - Handles Base64 Images & Charts
// ============================================================

import { useState } from 'react';
import { Download, Maximize2, X, ZoomIn, ZoomOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ImageRendererProps {
  src: string;
  alt?: string;
  className?: string;
}

// Single image component with zoom and download
export function ImageRenderer({ src, alt = 'Image', className }: ImageRendererProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [zoom, setZoom] = useState(1);

  // Handle base64 or URL
  const imageSrc = src.startsWith('data:') || src.startsWith('http')
    ? src
    : `data:image/png;base64,${src}`;

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = imageSrc;
    link.download = `image-${Date.now()}.png`;
    link.click();
  };

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.25, 3));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.25, 0.5));

  return (
    <>
      {/* Thumbnail */}
      <div className={cn('group relative inline-block', className)}>
        <img
          src={imageSrc}
          alt={alt}
          className="max-w-full rounded-lg border cursor-pointer transition-transform hover:scale-[1.02]"
          onClick={() => setIsModalOpen(true)}
        />
        <div className="absolute bottom-2 right-2 flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
          <Button
            variant="secondary"
            size="icon"
            className="h-7 w-7 bg-background/80 backdrop-blur-sm"
            onClick={(e) => {
              e.stopPropagation();
              setIsModalOpen(true);
            }}
          >
            <Maximize2 className="h-3.5 w-3.5" />
          </Button>
          <Button
            variant="secondary"
            size="icon"
            className="h-7 w-7 bg-background/80 backdrop-blur-sm"
            onClick={(e) => {
              e.stopPropagation();
              handleDownload();
            }}
          >
            <Download className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
          onClick={() => setIsModalOpen(false)}
        >
          {/* Controls */}
          <div className="absolute top-4 right-4 flex gap-2">
            <Button
              variant="secondary"
              size="icon"
              className="h-9 w-9"
              onClick={(e) => {
                e.stopPropagation();
                handleZoomOut();
              }}
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            <Button
              variant="secondary"
              size="icon"
              className="h-9 w-9"
              onClick={(e) => {
                e.stopPropagation();
                handleZoomIn();
              }}
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button
              variant="secondary"
              size="icon"
              className="h-9 w-9"
              onClick={(e) => {
                e.stopPropagation();
                handleDownload();
              }}
            >
              <Download className="h-4 w-4" />
            </Button>
            <Button
              variant="secondary"
              size="icon"
              className="h-9 w-9"
              onClick={() => setIsModalOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Image */}
          <div
            className="max-h-[90vh] max-w-[90vw] overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={imageSrc}
              alt={alt}
              className="rounded-lg"
              style={{ transform: `scale(${zoom})`, transformOrigin: 'center' }}
            />
          </div>
        </div>
      )}
    </>
  );
}

// Extract and render images from text content (for tool output)
interface ImageExtractorProps {
  content: string;
  className?: string;
}

export function ImageExtractor({ content, className }: ImageExtractorProps) {
  // Match [IMAGE_BASE64:...] pattern - use more permissive pattern
  // The base64 string can be very long, so we need to handle it carefully
  const imagePattern = /\[IMAGE_BASE64:([A-Za-z0-9+/=\s]+)\]/g;
  const matches = [...content.matchAll(imagePattern)];

  if (matches.length === 0) {
    // Debug: log if we expected to find images but didn't
    if (content.includes('IMAGE_BASE64')) {
      console.warn('ImageExtractor: Found IMAGE_BASE64 text but regex did not match');
      console.warn('Content snippet:', content.substring(0, 500));
    }
    return null;
  }

  return (
    <div className={cn('flex flex-wrap gap-3', className)}>
      {matches.map((match, index) => {
        // Clean up the base64 string (remove any whitespace)
        const cleanBase64 = match[1].replace(/\s/g, '');
        return (
          <ImageRenderer
            key={index}
            src={cleanBase64}
            alt={`Generated Chart ${index + 1}`}
            className="max-w-md"
          />
        );
      })}
    </div>
  );
}

// Chart container for matplotlib output
interface ChartContainerProps {
  base64Data: string;
  title?: string;
  className?: string;
}

export function ChartContainer({ base64Data, title, className }: ChartContainerProps) {
  return (
    <div className={cn('rounded-lg border bg-card p-4', className)}>
      {title && (
        <h4 className="mb-3 text-sm font-medium text-muted-foreground">{title}</h4>
      )}
      <ImageRenderer src={base64Data} alt={title || 'Chart'} />
    </div>
  );
}
