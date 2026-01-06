// ============================================================
// Presentation Store for Stream-Agent V9
// Zustand 状态管理
// ============================================================

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Presentation, Slide, PresentationTheme } from '@/lib/types/presentations';
import { presentationApi } from '@/lib/api/presentations';

// ============================================================
// Presentation Store State
// ============================================================

interface PresentationState {
  // 数据状态
  presentations: Presentation[];
  currentPresentation: Presentation | null;
  currentSlideIndex: number;
  isLoading: boolean;
  error: string | null;
  total: number;

  // UI 状态
  isGenerating: boolean;
  isEditorMode: boolean;
  showPreview: boolean;

  // 获取演示文稿列表
  fetchPresentations: (skip?: number, limit?: number) => Promise<void>;

  // 获取单个演示文稿
  fetchPresentation: (id: string) => Promise<void>;

  // 创建空白演示文稿
  createPresentation: (title: string, description?: string) => Promise<Presentation>;

  // AI 生成演示文稿
  generatePresentation: (data: {
    topic: string;
    title?: string;
    slideCount?: number;
    targetAudience?: string;
    presentationType?: 'informative' | 'persuasive' | 'instructional';
    theme?: PresentationTheme;
    includeImages?: boolean;
    imageStyle?: string;
    language?: 'zh-CN' | 'en-US';
  }) => Promise<Presentation>;

  // 更新演示文稿基本信息
  updatePresentation: (id: string, data: { title?: string; description?: string }) => Promise<void>;

  // 删除演示文稿
  deletePresentation: (id: string) => Promise<void>;

  // 设置当前演示文稿
  setCurrentPresentation: (presentation: Presentation | null) => void;

  // 设置当前幻灯片索引
  setCurrentSlideIndex: (index: number) => void;

  // 更新幻灯片
  updateSlide: (presentationId: string, slideIndex: number, data: {
    title?: string;
    content?: string;
    layout?: Slide['layout'];
    background?: string;
    notes?: string;
    images?: Slide['images'];
  }) => Promise<void>;

  // 添加幻灯片
  addSlide: (presentationId: string, slide: Slide, position?: number) => Promise<void>;

  // 删除幻灯片
  deleteSlide: (presentationId: string, slideIndex: number) => Promise<void>;

  // 重新生成幻灯片
  regenerateSlide: (presentationId: string, slideIndex: number, feedback: string) => Promise<void>;

  // 更换主题
  changeTheme: (presentationId: string, theme: PresentationTheme) => Promise<void>;

  // 静默更新当前演示文稿的幻灯片（不触发 isLoading）
  updateCurrentPresentationSlides: (slides: Slide[]) => void;

  // 清除错误
  clearError: () => void;

  // 重置状态
  reset: () => void;
}

// 初始状态
const initialState = {
  presentations: [],
  currentPresentation: null,
  currentSlideIndex: 0,
  isLoading: false,
  error: null,
  total: 0,
  isGenerating: false,
  isEditorMode: false,
  showPreview: false,
};

// ============================================================
// Create Store
// ============================================================

export const usePresentationStore = create<PresentationState>()(
  devtools(
    (set, _get) => ({
      ...initialState,

      // 获取演示文稿列表
      fetchPresentations: async (skip = 0, limit = 20) => {
        set({ isLoading: true, error: null });
        try {
          const response = await presentationApi.getPresentations(skip, limit);
          set({
            presentations: response.presentations,
            total: response.total,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch presentations',
            isLoading: false,
          });
        }
      },

      // 获取单个演示文稿
      fetchPresentation: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const presentation = await presentationApi.getPresentation(id);
          set({
            currentPresentation: presentation,
            currentSlideIndex: 0,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch presentation',
            isLoading: false,
          });
        }
      },

      // 创建空白演示文稿
      createPresentation: async (title: string, description?: string) => {
        set({ isLoading: true, error: null });
        try {
          const presentation = await presentationApi.createPresentation({ title, description });
          set((state) => ({
            presentations: [presentation, ...state.presentations],
            currentPresentation: presentation,
            isLoading: false,
          }));
          return presentation;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to create presentation',
            isLoading: false,
          });
          throw error;
        }
      },

      // AI 生成演示文稿
      generatePresentation: async (data) => {
        set({ isGenerating: true, error: null });
        try {
          const presentation = await presentationApi.generatePresentation(data);
          set((state) => ({
            presentations: [presentation, ...state.presentations],
            currentPresentation: presentation,
            isGenerating: false,
          }));
          return presentation;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to generate presentation',
            isGenerating: false,
          });
          throw error;
        }
      },

      // 更新演示文稿基本信息
      updatePresentation: async (id: string, data: { title?: string; description?: string }) => {
        set({ isLoading: true, error: null });
        try {
          const updated = await presentationApi.updatePresentation(id, data);
          set((state) => ({
            presentations: state.presentations.map((p) =>
              p.id === id ? updated : p
            ),
            currentPresentation: state.currentPresentation?.id === id ? updated : state.currentPresentation,
            isLoading: false,
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to update presentation',
            isLoading: false,
          });
        }
      },

      // 删除演示文稿
      deletePresentation: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          await presentationApi.deletePresentation(id);
          set((state) => ({
            presentations: state.presentations.filter((p) => p.id !== id),
            currentPresentation: state.currentPresentation?.id === id ? null : state.currentPresentation,
            isLoading: false,
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to delete presentation',
            isLoading: false,
          });
        }
      },

      // 设置当前演示文稿
      setCurrentPresentation: (presentation: Presentation | null) => {
        set({
          currentPresentation: presentation,
          currentSlideIndex: 0,
        });
      },

      // 设置当前幻灯片索引
      setCurrentSlideIndex: (index: number) => {
        set({ currentSlideIndex: index });
      },

      // 更新幻灯片
      updateSlide: async (presentationId: string, slideIndex: number, data) => {
        set({ isLoading: true, error: null });
        try {
          const updated = await presentationApi.updateSlide(presentationId, slideIndex, data);
          set((state) => ({
            presentations: state.presentations.map((p) =>
              p.id === presentationId ? updated : p
            ),
            currentPresentation: state.currentPresentation?.id === presentationId ? updated : state.currentPresentation,
            isLoading: false,
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to update slide',
            isLoading: false,
          });
        }
      },

      // 添加幻灯片
      addSlide: async (presentationId: string, slide: Slide, position?: number) => {
        set({ isLoading: true, error: null });
        try {
          const updated = await presentationApi.addSlide(presentationId, { slide, position });
          set((state) => ({
            presentations: state.presentations.map((p) =>
              p.id === presentationId ? updated : p
            ),
            currentPresentation: state.currentPresentation?.id === presentationId ? updated : state.currentPresentation,
            isLoading: false,
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to add slide',
            isLoading: false,
          });
        }
      },

      // 删除幻灯片
      deleteSlide: async (presentationId: string, slideIndex: number) => {
        set({ isLoading: true, error: null });
        try {
          const updated = await presentationApi.deleteSlide(presentationId, slideIndex);
          set((state) => ({
            presentations: state.presentations.map((p) =>
              p.id === presentationId ? updated : p
            ),
            currentPresentation: state.currentPresentation?.id === presentationId ? updated : state.currentPresentation,
            currentSlideIndex: Math.min(state.currentSlideIndex, updated.slides.length - 1),
            isLoading: false,
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to delete slide',
            isLoading: false,
          });
        }
      },

      // 重新生成幻灯片
      regenerateSlide: async (presentationId: string, slideIndex: number, feedback: string) => {
        set({ isGenerating: true, error: null });
        try {
          const updated = await presentationApi.regenerateSlide(presentationId, slideIndex, { feedback });
          set((state) => ({
            presentations: state.presentations.map((p) =>
              p.id === presentationId ? updated : p
            ),
            currentPresentation: state.currentPresentation?.id === presentationId ? updated : state.currentPresentation,
            isGenerating: false,
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to regenerate slide',
            isGenerating: false,
          });
        }
      },

      // 更换主题
      changeTheme: async (presentationId: string, theme: PresentationTheme) => {
        set({ isLoading: true, error: null });
        try {
          const updated = await presentationApi.changeTheme(presentationId, { theme });
          set((state) => ({
            presentations: state.presentations.map((p) =>
              p.id === presentationId ? updated : p
            ),
            currentPresentation: state.currentPresentation?.id === presentationId ? updated : state.currentPresentation,
            isLoading: false,
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to change theme',
            isLoading: false,
          });
        }
      },

      // 静默更新当前演示文稿的幻灯片（不触发 isLoading，用于 AI 助手更新）
      updateCurrentPresentationSlides: (slides: Slide[]) => {
        set((state) => {
          if (!state.currentPresentation) return state;
          return {
            currentPresentation: {
              ...state.currentPresentation,
              slides,
              slide_count: slides.length,
            },
          };
        });
      },

      // 清除错误
      clearError: () => {
        set({ error: null });
      },

      // 重置状态
      reset: () => {
        set(initialState);
      },
    }),
    { name: 'PresentationStore' }
  )
);
