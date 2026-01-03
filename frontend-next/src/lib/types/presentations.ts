// ============================================================
// Presentation Types for Stream-Agent V9
// ============================================================

export interface Slide {
  title: string;
  content: string;
  layout?: SlideLayout;
  background?: string;
  notes?: string;
  images?: SlideImage[];
}

export type SlideLayout =
  | 'title_cover'
  | 'title_section'
  | 'bullet_points'
  | 'two_column'
  | 'image_text'
  | 'quote_center'
  | 'thank_you';

export interface SlideImage {
  url?: string;
  alt?: string;
  position?: 'left' | 'right' | 'top' | 'bottom' | 'background';
}

export interface Presentation {
  id: string;
  userId: string;
  title: string;
  description?: string;
  slides: Slide[];
  layoutConfig?: Record<string, unknown>;
  theme: PresentationTheme;
  customTheme?: Record<string, unknown>;
  targetAudience?: string;
  presentationType?: 'informative' | 'persuasive' | 'instructional';
  includeImages: boolean;
  imageStyle?: string;
  slideCount: number;
  thumbnail?: string;
  status: 'draft' | 'completed' | 'archived';
  createdAt: string;
  updatedAt: string;
}

export type PresentationTheme =
  | 'modern_business'
  | 'creative'
  | 'minimalist'
  | 'dark_professional'
  | 'colorful'
  | 'academic';

export interface PresentationGenerateRequest {
  topic: string;
  title?: string;
  slideCount?: number;
  targetAudience?: string;
  presentationType?: 'informative' | 'persuasive' | 'instructional';
  theme?: PresentationTheme;
  includeImages?: boolean;
  imageStyle?: string;
  language?: 'zh-CN' | 'en-US';
}

export interface RegenerateSlideRequest {
  feedback: string;
}

export interface ChangeThemeRequest {
  theme: PresentationTheme;
}

export interface UpdateSlideRequest {
  title?: string;
  content?: string;
  layout?: SlideLayout;
  background?: string;
  notes?: string;
  images?: SlideImage[];
}

export interface AddSlideRequest {
  slide: Slide;
  position?: number;
}

export interface PresentationListResponse {
  presentations: Presentation[];
  total: number;
}

// Backend response format (snake_case)
interface BackendPresentation {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  slides: Slide[];
  layout_config?: Record<string, unknown>;
  theme: PresentationTheme;
  custom_theme?: Record<string, unknown>;
  target_audience?: string;
  presentation_type?: 'informative' | 'persuasive' | 'instructional';
  include_images: boolean;
  image_style?: string;
  slide_count: number;
  thumbnail?: string;
  status: 'draft' | 'completed' | 'archived';
  created_at: string;
  updated_at: string;
}

// Convert backend presentation to frontend format
export function toPresentation(backend: BackendPresentation): Presentation {
  return {
    id: backend.id,
    userId: backend.user_id,
    title: backend.title,
    description: backend.description,
    slides: backend.slides,
    layoutConfig: backend.layout_config,
    theme: backend.theme,
    customTheme: backend.custom_theme,
    targetAudience: backend.target_audience,
    presentationType: backend.presentation_type,
    includeImages: backend.include_images,
    imageStyle: backend.image_style,
    slideCount: backend.slide_count,
    thumbnail: backend.thumbnail,
    status: backend.status,
    createdAt: backend.created_at,
    updatedAt: backend.updated_at,
  };
}
