import {
  AuthResponse,
  User,
  Subject,
  Topic,
  RevisionQueueResponse,
  TopicPriorityBreakdown,
  PlanSession,
  StudySession,
  StudySessionSummary,
  AnalyticsSummary,
  SubjectMasteryItem,
  DayStudyTimeItem,
  MaterialItem,
  NoteItem,
  QuizItem,
  QuizAttemptResult,
  FlashcardItem,
  QuestionPaperItem,
  RoadmapItem,
  TutorConversationItem,
  TutorMessageItem,
} from "@/types";

const rawApiUrl = String((import.meta as any).env?.VITE_API_URL || "").trim();
const normalizedApiUrl = rawApiUrl.replace(/\/+$/, "");
const API_BASE = normalizedApiUrl ? `${normalizedApiUrl}/api/v1` : "/api/v1";

class ApiClient {
  private token: string | null = null;
  private isRefreshing = false;
  private refreshSubscribers: ((token: string) => void)[] = [];
  private authFailureCallback: (() => void) | null = null;

  constructor() {
    this.token = localStorage.getItem("studypilot_token");
  }

  /** Register a callback to be invoked when token refresh fails (session expired). */
  onAuthFailure(cb: () => void) {
    this.authFailureCallback = cb;
  }

  private notifyAuthFailure() {
    this.setToken(null);
    if (this.authFailureCallback) {
      this.authFailureCallback();
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem("studypilot_token", token);
    } else {
      localStorage.removeItem("studypilot_token");
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private onRefreshed(token: string) {
    this.refreshSubscribers.forEach((cb) => cb(token));
    this.refreshSubscribers = [];
  }

  private addRefreshSubscriber(cb: (token: string) => void) {
    this.refreshSubscribers.push(cb);
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers || {});
    if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }

    if (this.token) {
      headers.set("Authorization", `Bearer ${this.token}`);
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401 && !endpoint.includes("/auth/login") && !endpoint.includes("/auth/refresh")) {
      // Attempt token refresh
      if (!this.isRefreshing) {
        this.isRefreshing = true;
        try {
          const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
          });

          if (refreshRes.ok) {
            const data: AuthResponse = await refreshRes.json();
            this.setToken(data.access_token);
            this.onRefreshed(data.access_token);
            headers.set("Authorization", `Bearer ${data.access_token}`);
            const retryRes = await fetch(`${API_BASE}${endpoint}`, {
              ...options,
              headers,
            });
            if (!retryRes.ok) throw await retryRes.json();
            return (await retryRes.json()) as T;
          } else {
            this.setToken(null);
          }
        } catch (err) {
          this.setToken(null);
        } finally {
          this.isRefreshing = false;
        }
      } else {
        // Wait for active refresh
        return new Promise<T>((resolve, reject) => {
          this.addRefreshSubscriber(async (newToken) => {
            headers.set("Authorization", `Bearer ${newToken}`);
            try {
              const retryRes = await fetch(`${API_BASE}${endpoint}`, {
                ...options,
                headers,
              });
              if (!retryRes.ok) throw await retryRes.json();
              resolve((await retryRes.json()) as T);
            } catch (err) {
              reject(err);
            }
          });
        });
      }
    }

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { error: { message: response.statusText || "Request failed" } };
      }
      throw errorData;
    }

    return (await response.json()) as T;
  }
}

export const apiClient = new ApiClient();

// API Resource Methods
export const api = {
  // Auth
  auth: {
    register: (payload: { email: string; password: string; full_name: string }) =>
      apiClient.request<AuthResponse>("/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    login: (payload: { email: string; password: string }) =>
      apiClient.request<AuthResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    logout: () => apiClient.request<{ message: string; success: boolean }>("/auth/logout", { method: "POST" }),
    getMe: () => apiClient.request<User>("/auth/me"),
  },

  // Subjects
  subjects: {
    list: (params?: { page?: number; page_size?: number; search?: string }) => {
      const q = new URLSearchParams();
      if (params?.page) q.set("page", params.page.toString());
      if (params?.page_size) q.set("page_size", params.page_size.toString());
      if (params?.search) q.set("search", params.search);
      return apiClient.request<{ items: Subject[]; total: number; page: number; page_size: number; pages: number }>(
        `/subjects?${q.toString()}`
      );
    },
    get: (id: number) => apiClient.request<Subject>(`/subjects/${id}`),
    create: (payload: { name: string; description?: string; exam_date?: string; color?: string }) =>
      apiClient.request<Subject>("/subjects", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    update: (id: number, payload: Partial<{ name: string; description: string; exam_date: string; color: string }>) =>
      apiClient.request<Subject>(`/subjects/${id}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      }),
    delete: (id: number) =>
      apiClient.request<{ message: string; success: boolean }>(`/subjects/${id}`, { method: "DELETE" }),
  },

  // Topics
  topics: {
    listForSubject: (subjectId: number) =>
      apiClient.request<{ items: Topic[]; total: number }>(`/subjects/${subjectId}/topics`),
    create: (
      subjectId: number,
      payload: { name: string; description?: string; difficulty: "easy" | "medium" | "hard"; order_index?: number }
    ) =>
      apiClient.request<Topic>(`/subjects/${subjectId}/topics`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    get: (id: number) => apiClient.request<Topic>(`/topics/${id}`),
    update: (id: number, payload: Partial<Topic>) =>
      apiClient.request<Topic>(`/topics/${id}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      }),
    delete: (id: number) =>
      apiClient.request<{ message: string; success: boolean }>(`/topics/${id}`, { method: "DELETE" }),
  },

  // Plan
  plan: {
    generate: (payload: { daily_minutes: number; start_date?: string; days_horizon?: number }) =>
      apiClient.request<{ message: string; total_sessions_created: number; start_date: string; end_date: string }>(
        "/plan/generate",
        {
          method: "POST",
          body: JSON.stringify(payload),
        }
      ),
    getSchedule: (params?: { from_date?: string; to_date?: string; status?: string; subject_id?: number }) => {
      const q = new URLSearchParams();
      if (params?.from_date) q.set("from_date", params.from_date);
      if (params?.to_date) q.set("to_date", params.to_date);
      if (params?.status) q.set("status", params.status);
      if (params?.subject_id) q.set("subject_id", params.subject_id.toString());
      return apiClient.request<PlanSession[]>(`/plan/schedule?${q.toString()}`);
    },
    updateSessionStatus: (id: number, status: "pending" | "completed" | "skipped") =>
      apiClient.request<PlanSession>(`/plan/sessions/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
  },

  // Revision
  revision: {
    getQueue: (minutes = 60) => apiClient.request<RevisionQueueResponse>(`/revision/queue?minutes=${minutes}`),
    explainTopic: (topicId: number) => apiClient.request<TopicPriorityBreakdown>(`/revision/explain/${topicId}`),
  },

  // Mastery
  mastery: {
    record: (payload: {
      topic_id: number;
      event_type: "quiz_answer" | "card_rating";
      is_correct?: boolean;
      rating?: number;
      flashcard_id?: number;
      review_duration_ms?: number;
    }) =>
      apiClient.request("/mastery/record", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },

  // Focus Timer / Study Sessions
  studySessions: {
    create: (payload: {
      subject_id?: number | null;
      topic_id?: number | null;
      duration_minutes: number;
      session_type: "pomodoro" | "review" | "quiz" | "free";
      notes?: string;
    }) =>
      apiClient.request<StudySession>("/study-sessions", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    list: (params?: { page?: number; page_size?: number; subject_id?: number }) => {
      const q = new URLSearchParams();
      if (params?.page) q.set("page", params.page.toString());
      if (params?.page_size) q.set("page_size", params.page_size.toString());
      if (params?.subject_id) q.set("subject_id", params.subject_id.toString());
      return apiClient.request<{ items: StudySession[]; total: number }>(`/study-sessions?${q.toString()}`);
    },
    getSummary: () => apiClient.request<StudySessionSummary>("/study-sessions/summary"),
  },

  // Analytics
  analytics: {
    getSummary: () => apiClient.request<AnalyticsSummary>("/analytics/summary"),
    getMastery: () => apiClient.request<{ subjects: SubjectMasteryItem[] }>("/analytics/mastery"),
    getStudyTimeByDay: (days = 14) =>
      apiClient.request<{ days: DayStudyTimeItem[]; total_period_minutes: number }>(
        `/analytics/study-time-by-day?days=${days}`
      ),
  },

  // Materials
  materials: {
    upload: (formData: FormData) =>
      apiClient.request<MaterialItem>("/materials/upload", {
        method: "POST",
        body: formData,
      }),
    listForTopic: (topicId: number) =>
      apiClient.request<MaterialItem[]>(`/materials/topic/${topicId}`),
    getStatus: (id: number) =>
      apiClient.request<{ id: number; title: string; status: string; chunk_count: number; file_size: number }>(
        `/materials/${id}/status`
      ),
    delete: (id: number) =>
      apiClient.request<void>(`/materials/${id}`, { method: "DELETE" }),
  },

  // Study Notes
  notes: {
    generate: (payload: { topic_id: number; academic_level?: string; custom_instructions?: string }) =>
      apiClient.request<NoteItem>("/notes/generate", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    list: (params?: { topic_id?: number; search?: string }) => {
      const q = new URLSearchParams();
      if (params?.topic_id) q.set("topic_id", params.topic_id.toString());
      if (params?.search) q.set("search", params.search);
      return apiClient.request<NoteItem[]>(`/notes?${q.toString()}`);
    },
    get: (id: number) => apiClient.request<NoteItem>(`/notes/${id}`),
    update: (id: number, payload: { title?: string; content_markdown?: string }) =>
      apiClient.request<NoteItem>(`/notes/${id}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      }),
    delete: (id: number) => apiClient.request<void>(`/notes/${id}`, { method: "DELETE" }),
    getExportUrl: (id: number, format = "md") => `${API_BASE}/notes/${id}/export?format=${format}`,
  },

  // Quizzes
  quizzes: {
    generate: (payload: { topic_id: number; count?: number; difficulty?: string; question_types?: string[] }) =>
      apiClient.request<QuizItem>("/quizzes/generate", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    list: (topicId?: number) => {
      const q = topicId ? `?topic_id=${topicId}` : "";
      return apiClient.request<QuizItem[]>(`/quizzes${q}`);
    },
    get: (id: number) => apiClient.request<QuizItem>(`/quizzes/${id}`),
    submit: (id: number, answers: { question_id: number; selected_answer: string }[]) =>
      apiClient.request<QuizAttemptResult>(`/quizzes/${id}/submit`, {
        method: "POST",
        body: JSON.stringify({ answers }),
      }),
    getHistory: () => apiClient.request<any[]>("/quizzes/history/all"),
  },

  // Flashcards
  flashcards: {
    generate: (payload: { topic_id: number; count?: number }) =>
      apiClient.request<{ deck_title: string; count: number; cards: FlashcardItem[] }>("/flashcards/generate", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    list: (params?: { topic_id?: number; due_only?: boolean; search?: string }) => {
      const q = new URLSearchParams();
      if (params?.topic_id) q.set("topic_id", params.topic_id.toString());
      if (params?.due_only) q.set("due_only", "true");
      if (params?.search) q.set("search", params.search);
      return apiClient.request<FlashcardItem[]>(`/flashcards?${q.toString()}`);
    },
    create: (payload: { topic_id: number; front: string; back: string; explanation?: string; difficulty?: string }) =>
      apiClient.request<FlashcardItem>("/flashcards", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    update: (id: number, payload: Partial<FlashcardItem>) =>
      apiClient.request<FlashcardItem>(`/flashcards/${id}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      }),
    delete: (id: number) => apiClient.request<void>(`/flashcards/${id}`, { method: "DELETE" }),
    review: (payload: { flashcard_id: number; rating: number; review_duration_ms?: number }) =>
      apiClient.request<any>("/flashcards/review", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    getExportPdfUrl: (topicId?: number) =>
      `${API_BASE}/flashcards/export/pdf${topicId ? `?topic_id=${topicId}` : ""}`,
  },

  // Question Papers
  questionPapers: {
    generate: (payload: { subject_id: number; duration_minutes?: number; total_marks?: number; exam_type?: string }) =>
      apiClient.request<QuestionPaperItem>("/question-papers/generate", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    list: (subjectId?: number) => {
      const q = subjectId ? `?subject_id=${subjectId}` : "";
      return apiClient.request<QuestionPaperItem[]>(`/question-papers${q}`);
    },
    get: (id: number) => apiClient.request<QuestionPaperItem>(`/question-papers/${id}`),
    evaluate: (id: number, answers: Record<string, string>) =>
      apiClient.request<any>(`/question-papers/${id}/evaluate`, {
        method: "POST",
        body: JSON.stringify({ answers }),
      }),
    getExportPdfUrl: (id: number) => `${API_BASE}/question-papers/${id}/export/pdf`,
  },

  // Roadmap
  roadmap: {
    generate: (subjectId: number) =>
      apiClient.request<RoadmapItem>("/roadmap/generate", {
        method: "POST",
        body: JSON.stringify({ subject_id: subjectId }),
      }),
    getBySubject: (subjectId: number) =>
      apiClient.request<RoadmapItem>(`/roadmap/subject/${subjectId}`),
    toggleTask: (subjectId: number, taskId: string, completed: boolean) =>
      apiClient.request<{ status: string; task_id: string; completed: boolean }>(
        `/roadmap/subject/${subjectId}/toggle-task`,
        {
          method: "POST",
          body: JSON.stringify({ task_id: taskId, completed }),
        }
      ),
  },

  // AI Tutor
  tutor: {
    listConversations: (topicId?: number) => {
      const q = topicId ? `?topic_id=${topicId}` : "";
      return apiClient.request<TutorConversationItem[]>(`/tutor/conversations${q}`);
    },
    getConversation: (id: number) =>
      apiClient.request<{ id: number; topic_id: number; title: string; messages: TutorMessageItem[] }>(
        `/tutor/conversations/${id}`
      ),
    checkUnderstanding: (payload: { topic_id?: number; concept?: string }) =>
      apiClient.request<{
        question_text: string;
        options: string[] | null;
        correct_answer: string;
        explanation: string;
        citation?: string;
      }>("/tutor/check-understanding", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    streamChat: async (
      payload: { topic_id?: number; message: string; mode?: string; conversation_id?: number },
      onToken: (token: string) => void,
      onConvId?: (id: number) => void
    ) => {
      const token = apiClient.getToken();
      const response = await fetch(`${API_BASE}/tutor/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let msg = `Chat failed (${response.status})`;
        try {
          const err = await response.json();
          if (err?.error?.message) msg = err.error.message;
          else if (err?.detail) msg = err.detail;
        } catch {}
        throw new Error(msg);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          if (buffer.trim()) {
            const remaining = buffer.split("\n\n");
            for (const line of remaining) {
              if (line.startsWith("data: ")) {
                try {
                  const data = JSON.parse(line.substring(6));
                  if (data.type === "token") onToken(data.text);
                  else if (data.type === "conv_id" && onConvId) onConvId(data.conversation_id);
                  else if (data.type === "error") throw new Error(data.error);
                } catch (err: any) {
                  if (err?.message && !err.message.includes("JSON")) throw err;
                }
              }
            }
          }
          break;
        }
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            let data: any = null;
            try {
              data = JSON.parse(line.substring(6));
            } catch {
              continue;
            }
            if (data.type === "token") {
              onToken(data.text);
            } else if (data.type === "conv_id" && onConvId) {
              onConvId(data.conversation_id);
            } else if (data.type === "error") {
              throw new Error(data.error || "Streaming error encountered");
            }
          }
        }
      }
    },
  },
};

