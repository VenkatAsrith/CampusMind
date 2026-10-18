export type UserRole = 'student' | 'faculty' | 'admin';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Citation {
  document_id: number;
  document_title: string;
  page_number?: number | null;
  section_heading?: string | null;
  chunk_id?: number | null;
  similarity_score?: number | null;
}

export interface Message {
  id?: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  insufficient_evidence?: boolean;
  created_at?: string;
  error?: boolean;
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail {
  id: string;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ChatQueryResponse {
  answer: string;
  conversation_id: string;
  message_id: number;
  insufficient_evidence: boolean;
  citations: Citation[];
  retrieval_count: number;
  total_latency_ms: number;
}

export interface DocumentRead {
  id: number;
  filename: string;
  title: string;
  document_type: string;
  file_size_bytes: number;
  content_hash: string;
  uploader_id: number;
  audience_role: UserRole;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string | null;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  total: number;
  documents: DocumentRead[];
}

export interface AdminStats {
  total_documents: number;
  completed_documents: number;
  pending_documents: number;
  failed_documents: number;
  total_chunks: number;
  supported_extensions: string[];
}

export interface MentionItem {
  key: string;
  label: string;
  description: string;
  required_role: string;
  workflow: string;
}

export interface StudentRecord {
  roll_number: string;
  full_name: string;
  email: string;
  program: string;
  semester: string;
  academic_standing: string;
  attendance_percentage: number;
  registered_courses: string[];
}
