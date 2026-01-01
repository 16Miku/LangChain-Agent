// Audio Player Component
// 音频播放器组件，用于播放 TTS 生成的语音

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AudioPlayerProps {
  src: string;
  onEnded?: () => void;
  className?: string;
}

export function AudioPlayer({ src, onEnded, className }: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);

  const audioRef = useRef<HTMLAudioElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => setCurrentTime(audio.currentTime);
    const handleLoadedMetadata = () => setDuration(audio.duration);
    const handleEnded = () => {
      setIsPlaying(false);
      onEnded?.();
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [onEnded]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current;
    const progress = progressRef.current;
    if (!audio || !progress) return;

    const rect = progress.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    audio.currentTime = percentage * duration;
  };

  const toggleMute = () => {
    const audio = audioRef.current;
    if (!audio) return;

    audio.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const formatTime = (time: number) => {
    if (isNaN(time)) return '0:00';
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className={cn('flex items-center gap-3 bg-muted/50 rounded-lg p-2', className)}>
      <audio ref={audioRef} src={src} />

      {/* 播放/暂停按钮 */}
      <button
        type="button"
        onClick={togglePlay}
        className="p-2 rounded-full hover:bg-background transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
        aria-label={isPlaying ? '暂停' : '播放'}
      >
        {isPlaying ? (
          <Pause className="w-5 h-5" />
        ) : (
          <Play className="w-5 h-5" />
        )}
      </button>

      {/* 进度条 */}
      <div
        ref={progressRef}
        onClick={handleSeek}
        className="flex-1 h-2 bg-background rounded-full cursor-pointer relative overflow-hidden group"
      >
        <div
          className="absolute left-0 top-0 h-full bg-primary transition-all duration-100 group-hover:bg-primary/80"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* 时间显示 */}
      <div className="text-xs text-muted-foreground min-w-[80px] text-right">
        {formatTime(currentTime)} / {formatTime(duration)}
      </div>

      {/* 音量控制 */}
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={toggleMute}
          className="p-1.5 rounded-full hover:bg-background transition-colors focus:outline-none"
          aria-label={isMuted ? '取消静音' : '静音'}
        >
          {isMuted ? (
            <VolumeX className="w-4 h-4" />
          ) : (
            <Volume2 className="w-4 h-4" />
          )}
        </button>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={volume}
          onChange={(e) => {
            const newVolume = parseFloat(e.target.value);
            setVolume(newVolume);
            if (audioRef.current) {
              audioRef.current.volume = newVolume;
            }
          }}
          className="w-16 h-1.5 accent-primary cursor-pointer"
        />
      </div>
    </div>
  );
}

// 简化的播放按钮组件（用于消息气泡内）
interface PlayButtonProps {
  onClick: () => void;
  isPlaying?: boolean;
  className?: string;
}

export function PlayButton({ onClick, isPlaying = false, className }: PlayButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'p-1.5 rounded-full hover:bg-accent transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-primary',
        className
      )}
      aria-label={isPlaying ? '暂停' : '播放'}
    >
      {isPlaying ? (
        <Pause className="w-4 h-4" />
      ) : (
        <Play className="w-4 h-4" />
      )}
    </button>
  );
}

// 重新生成语音按钮
export function RegenerateSpeechButton({
  onRegenerate,
  isGenerating = false,
  className,
}: {
  onRegenerate: () => void;
  isGenerating?: boolean;
  className?: string;
}) {
  return (
    <button
      type="button"
      onClick={onRegenerate}
      disabled={isGenerating}
      className={cn(
        'p-1.5 rounded-full hover:bg-accent transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-primary',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className
      )}
      title="重新生成语音"
    >
      <RotateCcw className={cn('w-4 h-4', isGenerating && 'animate-spin')} />
    </button>
  );
}
