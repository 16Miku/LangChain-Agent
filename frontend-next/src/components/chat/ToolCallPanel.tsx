'use client';

// ============================================================
// Tool Call Panel Component - Enhanced Tool Visualization
// ============================================================

import { useState } from 'react';
import {
  Check,
  ChevronDown,
  ChevronUp,
  Loader2,
  AlertCircle,
  Search,
  Code,
  Database,
  Globe,
  FileText,
  Image,
  Terminal,
  Zap,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ToolCall } from '@/lib/types';
import { ImageExtractor } from './ImageRenderer';
import { PresentationExtractor } from './PresentationPreview';

interface ToolCallPanelProps {
  toolCalls: ToolCall[];
  className?: string;
}

// Tool category icons
const toolIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  search: Search,
  search_engine: Search,
  scrape: Globe,
  scrape_as_markdown: Globe,
  scrape_as_html: Globe,
  execute: Terminal,
  execute_python_code: Code,
  execute_shell_command: Terminal,
  analyze: Database,
  analyze_csv_data: Database,
  query: Database,
  query_knowledge_base: FileText,
  ingest: FileText,
  ingest_knowledge: FileText,
  format: FileText,
  format_paper_analysis: FileText,
  format_linkedin_profile: FileText,
  install: Zap,
  install_python_package: Zap,
  upload: Image,
  download: Image,
  presentation: FileText,
  generate_presentation: FileText,
  default: Terminal,
};

// Get icon for a tool
function getToolIcon(toolName: string) {
  const lowerName = toolName.toLowerCase();

  // Check exact match first
  if (toolIcons[lowerName]) {
    return toolIcons[lowerName];
  }

  // Check prefix match
  for (const [key, icon] of Object.entries(toolIcons)) {
    if (lowerName.includes(key)) {
      return icon;
    }
  }

  return toolIcons.default;
}

export function ToolCallPanel({ toolCalls, className }: ToolCallPanelProps) {
  const [expanded, setExpanded] = useState(false);

  if (!toolCalls || toolCalls.length === 0) {
    return null;
  }

  // Count by status
  const running = toolCalls.filter((t) => t.status === 'running').length;
  const success = toolCalls.filter((t) => t.status === 'success').length;
  const error = toolCalls.filter((t) => t.status === 'error').length;

  return (
    <div className={cn('w-full', className)}>
      {/* Summary Header */}
      <button
        className="flex w-full items-center gap-2 rounded-lg border bg-muted/50 px-3 py-2 text-left transition-colors hover:bg-muted"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-1.5">
          {running > 0 && (
            <span className="flex items-center gap-1 text-xs text-blue-500">
              <Loader2 className="h-3 w-3 animate-spin" />
              {running}
            </span>
          )}
          {success > 0 && (
            <span className="flex items-center gap-1 text-xs text-green-500">
              <Check className="h-3 w-3" />
              {success}
            </span>
          )}
          {error > 0 && (
            <span className="flex items-center gap-1 text-xs text-red-500">
              <AlertCircle className="h-3 w-3" />
              {error}
            </span>
          )}
        </div>
        <span className="text-xs text-muted-foreground">
          {toolCalls.length} tool{toolCalls.length > 1 ? 's' : ''} called
        </span>
        <div className="ml-auto">
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
      </button>

      {/* Expanded Tool List */}
      {expanded && (
        <div className="mt-2 space-y-2">
          {toolCalls.map((tool) => (
            <ToolCallItem key={tool.id} toolCall={tool} />
          ))}
        </div>
      )}
    </div>
  );
}

// Individual Tool Call Item
interface ToolCallItemProps {
  toolCall: ToolCall;
}

function ToolCallItem({ toolCall }: ToolCallItemProps) {
  const [outputExpanded, setOutputExpanded] = useState(false);
  const Icon = getToolIcon(toolCall.name);

  const statusStyles = {
    running: 'border-blue-500/30 bg-blue-500/10',
    success: 'border-green-500/30 bg-green-500/10',
    error: 'border-red-500/30 bg-red-500/10',
  };

  const statusIcon = {
    running: <Loader2 className="h-4 w-4 animate-spin text-blue-500" />,
    success: <Check className="h-4 w-4 text-green-500" />,
    error: <AlertCircle className="h-4 w-4 text-red-500" />,
  };

  // Format tool name for display
  const displayName = toolCall.name
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());

  // Check if output contains image data
  const hasImage = toolCall.output?.includes('[IMAGE_BASE64:');

  // Check if output contains presentation data
  const hasPresentation = toolCall.output?.includes('[PRESENTATION_HTML:');

  // Safely truncate output for preview
  const getOutputPreview = () => {
    if (!toolCall.output) return null;

    let output = toolCall.output;

    // Remove image base64 data for preview
    if (hasImage) {
      output = output.replace(/\[IMAGE_BASE64:[A-Za-z0-9+/=]+\]/g, '[IMAGE]');
    }

    // Remove presentation base64 data for preview
    if (hasPresentation) {
      output = output.replace(/\[PRESENTATION_HTML:[A-Za-z0-9+/=]+\]/g, '[PRESENTATION]');
    }

    if (output.length > 150) {
      return output.slice(0, 150) + '...';
    }
    return output;
  };

  return (
    <div
      className={cn(
        'rounded-lg border p-3 transition-colors',
        statusStyles[toolCall.status]
      )}
    >
      {/* Tool Header */}
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-background">
          <Icon className="h-4 w-4 text-muted-foreground" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-medium text-sm truncate">{displayName}</span>
            {statusIcon[toolCall.status]}
          </div>
          {toolCall.duration && (
            <span className="text-xs text-muted-foreground">
              Completed in {(toolCall.duration / 1000).toFixed(2)}s
            </span>
          )}
        </div>
      </div>

      {/* Always show images first if present (without needing to expand) */}
      {hasImage && toolCall.status !== 'running' && (
        <div className="mt-3">
          <ImageExtractor content={toolCall.output!} className="mb-2" />
        </div>
      )}

      {/* Always show presentations if present (without needing to expand) */}
      {hasPresentation && toolCall.status !== 'running' && (
        <div className="mt-3">
          <PresentationExtractor content={toolCall.output!} className="mb-2" />
        </div>
      )}

      {/* Output Preview/Full */}
      {toolCall.output && toolCall.status !== 'running' && (
        <div className="mt-3">
          <button
            className="flex w-full items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
            onClick={() => setOutputExpanded(!outputExpanded)}
          >
            {outputExpanded ? (
              <>
                <ChevronUp className="h-3 w-3" />
                Hide output
              </>
            ) : (
              <>
                <ChevronDown className="h-3 w-3" />
                Show output
              </>
            )}
          </button>

          {outputExpanded && (
            <div className="mt-2 space-y-3">
              {/* Text output */}
              <div className="max-h-64 overflow-auto rounded-md bg-background p-3">
                <pre className="text-xs whitespace-pre-wrap break-all text-foreground/80">
                  {(() => {
                    let output = toolCall.output || '';
                    if (hasImage) {
                      output = output.replace(/\[IMAGE_BASE64:[A-Za-z0-9+/=]+\]/g, '[Chart Image]');
                    }
                    if (hasPresentation) {
                      output = output.replace(/\[PRESENTATION_HTML:[A-Za-z0-9+/=]+\]/g, '[Presentation HTML]');
                    }
                    return output;
                  })()}
                </pre>
              </div>
            </div>
          )}

          {!outputExpanded && getOutputPreview() && (
            <div className="mt-1 text-xs text-muted-foreground/70 truncate">
              {getOutputPreview()}
            </div>
          )}
        </div>
      )}

      {/* Running indicator */}
      {toolCall.status === 'running' && (
        <div className="mt-2 text-xs text-muted-foreground">
          Executing...
        </div>
      )}
    </div>
  );
}
