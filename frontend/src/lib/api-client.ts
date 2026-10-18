import type {
  AuthResponse,
  User,
  ConversationSummary,
  ConversationDetail,
  ChatQueryResponse,
  DocumentListResponse,
  DocumentRead,
  AdminStats,
  MentionItem,
  StudentRecord,
  UserRole,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

class ApiClient {
  private token: string | null = null;

  constructor() {
    if (typeof window !== 'undefined' && window.sessionStorage) {
      this.token = window.sessionStorage.getItem('campusmind_token');
    }
  }

  public setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined' && window.sessionStorage) {
      if (token) {
        window.sessionStorage.setItem('campusmind_token', token);
      } else {
        window.sessionStorage.removeItem('campusmind_token');
      }
    }
  }

  public getToken(): string | null {
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = new Headers(options.headers || {});

    if (this.token && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${this.token}`);
    }

    if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMessage = `HTTP error ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // use status text
        errorMessage = response.statusText || errorMessage;
      }

      if (response.status === 401) {
        // Token expired or invalid
        this.setToken(null);
      }

      throw new Error(errorMessage);
    }

    // Check for 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // --- Authentication ---
  public async login(username: string, password: string):Promise<AuthResponse> {
    const data = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  public async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  public logout() {
    this.setToken(null);
  }

  // --- Student Personal Records ---
  public async getStudentRecord(identifier: string): Promise<StudentRecord> {
    return this.request<StudentRecord>(`/auth/student/${encodeURIComponent(identifier)}`);
  }

  // --- Chat & Mentions ---
  public async sendQuery(
    question: string,
    conversationId?: string,
    topK?: number
  ): Promise<ChatQueryResponse> {
    return this.request<ChatQueryResponse>('/chat/query', {
      method: 'POST',
      body: JSON.stringify({
        question,
        conversation_id: conversationId,
        top_k: topK,
      }),
    });
  }

  public async getMentions(): Promise<MentionItem[]> {
    return this.request<MentionItem[]>('/chat/mentions');
  }

  // --- Conversations ---
  public async getConversations(): Promise<ConversationSummary[]> {
    return this.request<ConversationSummary[]>('/conversations');
  }

  public async getConversation(conversationId: string): Promise<ConversationDetail> {
    return this.request<ConversationDetail>(`/conversations/${conversationId}`);
  }

  public async renameConversation(
    conversationId: string,
    title: string
  ): Promise<ConversationSummary> {
    return this.request<ConversationSummary>(`/conversations/${conversationId}`, {
      method: 'PATCH',
      body: JSON.stringify({ title }),
    });
  }

  public async deleteConversation(conversationId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/conversations/${conversationId}`, {
      method: 'DELETE',
    });
  }

  // --- Admin Knowledge Studio ---
  public async getAdminStats(): Promise<AdminStats> {
    return this.request<AdminStats>('/admin/documents/stats');
  }

  public async getAdminDocuments(): Promise<DocumentListResponse> {
    return this.request<DocumentListResponse>('/admin/documents');
  }

  public async uploadDocument(
    file: File,
    audienceRole: UserRole,
    title?: string
  ): Promise<{ message: string; document: DocumentRead }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('audience_role', audienceRole);
    if (title) {
      formData.append('title', title);
    }

    return this.request<{ message: string; document: DocumentRead }>('/admin/documents', {
      method: 'POST',
      body: formData,
    });
  }

  public async deleteDocument(documentId: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/admin/documents/${documentId}`, {
      method: 'DELETE',
    });
  }
}

export const api = new ApiClient();
