// Voice Recorder Component
// 语音录制组件，支持录音并转换为文字

'use client';

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Mic, MicOff, Loader2, AlertCircle } from 'lucide-react';
import { transcribeAudio } from '@/lib/api/voice';
import { cn } from '@/lib/utils';

interface VoiceRecorderProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
  className?: string;
}

export function VoiceRecorder({ onTranscript, disabled = false, className }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // 清理定时器
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  // 处理音频数据
  const processAudio = useCallback(async (audioBlob: Blob) => {
    setIsProcessing(true);
    setError(null);

    try {
      // 转换为 WAV 文件格式（如果需要）
      const audioFile = new File(
        [audioBlob],
        `recording-${Date.now()}.webm`,
        { type: audioBlob.type }
      );

      // 调用 STT API
      const result = await transcribeAudio(audioFile, 'auto');

      if (result.text && result.text.trim().length > 0) {
        onTranscript(result.text.trim());
      } else {
        setError('未能识别到语音，请重试');
      }

    } catch (err) {
      console.error('语音识别失败:', err);
      setError('语音识别失败，请稍后重试');
    } finally {
      setIsProcessing(false);
    }
  }, [onTranscript]);

  // 开始录音
  const startRecording = useCallback(async () => {
    setError(null);

    try {
      // 请求麦克风权限
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      // 创建 MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: getSupportedMimeType(),
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // 收集音频数据
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // 录音停止处理
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: mediaRecorder.mimeType,
        });

        // 停止所有音频轨道
        stream.getTracks().forEach((track) => track.stop());

        // 处理音频
        await processAudio(audioBlob);
      };

      // 开始录音
      mediaRecorder.start(100); // 每100ms收集一次数据
      setIsRecording(true);

      // 开始计时
      setRecordingTime(0);
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);

    } catch (err) {
      console.error('录音启动失败:', err);
      setError('无法访问麦克风，请检查权限设置');
      setIsRecording(false);
    }
  }, [processAudio]);

  // 停止录音
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      // 停止计时
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  }, []);

  // 获取支持的 MIME 类型
  function getSupportedMimeType(): string {
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/ogg',
      'audio/mp4',
      'audio/wav',
    ];

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }

    return '';
  }

  // 格式化录音时间
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={cn('relative', className)}>
      <button
        type="button"
        onClick={isRecording ? stopRecording : startRecording}
        disabled={disabled || isProcessing}
        className={cn(
          'p-2 rounded-full transition-all duration-200',
          'hover:bg-accent',
          'focus:outline-none focus:ring-2 focus:ring-primary',
          isRecording && 'bg-red-500 hover:bg-red-600 text-white',
          (disabled || isProcessing) && 'opacity-50 cursor-not-allowed'
        )}
        title={isRecording ? '停止录音' : '开始录音'}
      >
        {isProcessing ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : isRecording ? (
          <Mic className="w-5 h-5" />
        ) : (
          <MicOff className="w-5 h-5" />
        )}
      </button>

      {/* 录音指示器 */}
      {isRecording && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 flex items-center gap-2 bg-background border rounded-full px-3 py-1.5 shadow-lg">
          <div className="flex gap-1">
            <span className="w-1 h-3 bg-red-500 rounded-full animate-pulse" />
            <span className="w-1 h-3 bg-red-500 rounded-full animate-pulse delay-75" />
            <span className="w-1 h-3 bg-red-500 rounded-full animate-pulse delay-150" />
          </div>
          <span className="text-xs font-medium">{formatTime(recordingTime)}</span>
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 flex items-center gap-2 bg-destructive text-destructive-foreground rounded-lg px-3 py-2 shadow-lg max-w-xs">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span className="text-xs">{error}</span>
        </div>
      )}

      {/* 处理中提示 */}
      {isProcessing && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 flex items-center gap-2 bg-muted rounded-lg px-3 py-2 shadow-lg">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-xs">识别中...</span>
        </div>
      )}
    </div>
  );
}
