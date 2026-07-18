/** TypeScript types for NirmanMitr data models. */

// ─── DSR Item ───
export interface DSRItem {
  id: string;
  item_number: string;
  chapter: string;
  official_description: string;
  simple_title: string | null;
  summary: string | null;
  purpose: string | null;
  where_used: string[];
  materials: MaterialItem[];
  execution_steps: string[];
  common_mistakes: string[];
  measurement_unit: string | null;
  specification_reference: string | null;
  images: ImageItem[];
  future_video: string | null;
  search_keywords: string[];
  created_at: string;
  updated_at: string;
  is_ai_generated?: boolean;
}

export interface DSRItemSummary {
  id: string;
  item_number: string;
  chapter: string;
  simple_title: string | null;
  official_description: string;
  measurement_unit: string | null;
  is_populated: boolean;
}

export interface MaterialItem {
  name: string;
  quantity?: string;
  grade?: string;
}

export interface ImageItem {
  url: string;
  caption?: string;
}

// ─── Project ───
export interface Project {
  id: string;
  name: string;
  file_type: string;
  file_size: number;
  total_items: number;
  dsr_matches: number;
  unknown_items: number;
  status: "uploading" | "parsing" | "completed" | "failed";
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

// ─── Parsed Item ───
export interface ParsedItem {
  id: string;
  order_index: number;
  item_number: string | null;
  description: string;
  quantity: number | null;
  unit: string | null;
  rate: number | null;
  amount: number | null;
  depth: number;
  dsr_item_number: string | null;
  dsr_match_confidence: "exact" | "partial" | "none";
  is_matched: boolean;
}

// ─── API Responses ───
export interface ProjectListResponse {
  items: Project[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProjectDetailResponse {
  project: Project;
  items: ParsedItem[];
  total_items: number;
  page: number;
  page_size: number;
}

export interface SearchResponse {
  items: DSRItemSummary[];
  total: number;
  page: number;
  page_size: number;
  query: string;
}

export interface DashboardStats {
  total_projects: number;
  total_items: number;
  total_matches: number;
  total_unknown: number;
}

export interface UploadResponse {
  project_id: string;
  name: string;
  file_type: string;
  file_size: number;
  status: string;
  message: string;
}

export interface ParseResponse {
  project_id: string;
  status: string;
  total_items: number;
  dsr_matches: number;
  unknown_items: number;
  message: string;
}
