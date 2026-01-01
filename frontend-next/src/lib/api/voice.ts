// Voice API 客户端

import axios from 'axios';
import { VOICE_API_URL } from './client';

// 创建独立的 voice API 客户端
const voiceApiClient = axios.create({
  baseURL: VOICE_API_URL,
  timeout: 60000, // 语音处理可能需要更长时间
});

// 添加认证拦截器
voiceApiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('accessToken');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export interface TranscribeResponse {
  text: string;
  language: string;
  duration: number;
  confidence?: number;
}

export interface VoiceInfo {
  id: string;
  name: string;
  language: string;
  description: string;
  gender: 'Male' | 'Female';
}

export interface TTSRequest {
  text: string;
  voice?: string;
  rate?: string;
  volume?: string;
  pitch?: string;
}

export interface VoicesResponse {
  voices: VoiceInfo[];
}

/**
 * 语音转文字
 * @param audioFile 音频文件
 * @language 语言代码 (auto, zh, en, ja, ko)
 */
export async function transcribeAudio(
  audioFile: File,
  language: string = 'auto'
): Promise<TranscribeResponse> {
  const formData = new FormData();
  formData.append('file', audioFile);
  formData.append('language', language);

  const response = await voiceApiClient.post<TranscribeResponse>(
    '/api/v1/voice/transcribe',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
}

/**
 * 文字转语音
 * @param request TTS 请求参数
 * @returns 音频 Blob URL
 */
export async function synthesizeSpeech(request: TTSRequest): Promise<string> {
  const response = await voiceApiClient.post('/api/v1/voice/synthesize', request, {
    responseType: 'blob',
  });

  // 创建 Blob URL
  const blob = new Blob([response.data], { type: 'audio/mpeg' });
  return URL.createObjectURL(blob);
}

/**
 * 获取可用语音列表
 * @param language 可选的语言筛选
 */
export async function getVoices(language?: string): Promise<VoicesResponse> {
  const params = language ? { language } : {};
  const response = await voiceApiClient.get<VoicesResponse>('/api/v1/voice/voices', { params });
  return response.data;
}

/**
 * 服务健康检查
 */
export async function checkVoiceHealth(): Promise<{
  status: string;
  service: string;
  version: string;
  whisper_loaded: boolean;
  tts_available: boolean;
}> {
  const response = await voiceApiClient.get('/api/v1/voice/health');
  return response.data;
}
