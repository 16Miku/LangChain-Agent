// ============================================================
// Settings Store - Zustand State Management
// ============================================================

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'light' | 'dark' | 'system';

interface SettingsState {
  // UI Settings
  theme: Theme;
  sidebarOpen: boolean;
  sidebarWidth: number;

  // Chat Settings
  defaultModel: string;
  streamingEnabled: boolean;

  // Voice Settings
  voiceEnabled: boolean;
  voiceLanguage: string;
  ttsVoice: string;
  selectedVoice: string;  // 别名，与 ttsVoice 同步

  // Actions
  setTheme: (theme: Theme) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSidebarWidth: (width: number) => void;
  setDefaultModel: (model: string) => void;
  setStreamingEnabled: (enabled: boolean) => void;
  setVoiceEnabled: (enabled: boolean) => void;
  setVoiceLanguage: (language: string) => void;
  setTtsVoice: (voice: string) => void;
  setSelectedVoice: (voice: string) => void;  // 别名方法
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      // Default values
      theme: 'system',
      sidebarOpen: true,
      sidebarWidth: 280,
      defaultModel: 'gemini-2.0-flash-lite',
      streamingEnabled: true,
      voiceEnabled: false,
      voiceLanguage: 'zh-CN',
      ttsVoice: 'zh-CN-XiaoxiaoNeural',
      selectedVoice: 'zh-CN-XiaoxiaoNeural',

      // Actions
      setTheme: (theme) => {
        set({ theme });
        // Apply theme to document
        if (typeof window !== 'undefined') {
          const root = window.document.documentElement;
          root.classList.remove('light', 'dark');

          if (theme === 'system') {
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
              ? 'dark'
              : 'light';
            root.classList.add(systemTheme);
          } else {
            root.classList.add(theme);
          }
        }
      },

      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

      setSidebarOpen: (open) => set({ sidebarOpen: open }),

      setSidebarWidth: (width) => set({ sidebarWidth: width }),

      setDefaultModel: (model) => set({ defaultModel: model }),

      setStreamingEnabled: (enabled) => set({ streamingEnabled: enabled }),

      setVoiceEnabled: (enabled) => set({ voiceEnabled: enabled }),

      setVoiceLanguage: (language) => set({ voiceLanguage: language }),

      setTtsVoice: (voice) => set({ ttsVoice: voice, selectedVoice: voice }),

      setSelectedVoice: (voice) => set({ ttsVoice: voice, selectedVoice: voice }),
    }),
    {
      name: 'settings-storage',
    }
  )
);
