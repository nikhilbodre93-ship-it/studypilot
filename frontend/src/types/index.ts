export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface Subject {
  id: number;
  user_id: number;
  name: string;
  description?: string | null;
  exam_date?: string | null;
  color: string;
  topic_count: number;
  created_at: string;
  updated_at: string;
}

export interface Topic {
  id: number;
  subject_id: number;
  name: string;
  description?: string | null;
  difficulty: "easy" | "medium" | "hard";
  order_index: number;
  mastery_score?: number | null;
  created_at: string;
  updated_at: string;
}

export interface ScheduledSessionItem {
  topic_id: number;
  topic_name: string;
  subject_id: number;
  subject_name: string;
  duration_minutes: number;
  session_type: "learn" | "review" | "quiz" | "rapid_review" | "exam_paper";
  reason: string;
  priority_score: number;
  scheduled_order: number;
  next_review_date: string;
}

export interface RevisionQueueResponse {
  available_minutes: number;
  total_scheduled_minutes: number;
  sessions_count: number;
  is_exam_mode_active: boolean;
  queue: ScheduledSessionItem[];
}

export interface PlanSession {
  id: number;
  user_id: number;
  subject_id?: number | null;
  topic_id: number;
  scheduled_date: string;
  scheduled_order: number;
  duration_minutes: number;
  session_type: string;
  status: "pending" | "completed" | "skipped";
  reason?: string | null;
  created_at: string;
  subject_name?: string | null;
  topic_name?: string | null;
}

export interface TopicPriorityBreakdown {
  topic_id: number;
  topic_name: string;
  subject_id: number;
  subject_name: string;
  priority_score: number;
  base_score: number;
  exam_proximity_multiplier: number;
  is_exam_mode: boolean;
  days_until_exam?: number | null;
  components: {
    mastery: number;
    quiz_error: number;
    overdue_cards: number;
    difficulty: number;
    forgetting: number;
  };
  raw_metrics: {
    score: number;
    attempts: number;
    observed_accuracy: number;
    overdue_cards_count: number;
    days_since_last_study?: number | null;
    difficulty: string;
    days_until_exam?: number | null;
  };
  reason: string;
}

export interface StudySession {
  id: number;
  user_id: number;
  subject_id?: number | null;
  topic_id?: number | null;
  duration_minutes: number;
  session_type: "pomodoro" | "review" | "quiz" | "free";
  notes?: string | null;
  completed_at?: string | null;
  created_at: string;
  subject_name?: string | null;
  topic_name?: string | null;
}

export interface StudySessionSummary {
  total_sessions: number;
  total_minutes: number;
  total_hours: number;
  by_type: Record<string, number>;
}

export interface UpcomingExam {
  subject_id: number;
  subject_name: string;
  exam_date: string;
  days_remaining: number;
  is_exam_mode: boolean;
  color: string;
}

export interface AnalyticsSummary {
  overall_mastery_pct: number;
  total_subjects: number;
  total_topics: number;
  mastered_topics_count: number;
  in_progress_topics_count: number;
  total_study_minutes: number;
  total_study_sessions: number;
  cards_overdue_count: number;
  upcoming_exams: UpcomingExam[];
}

export interface TopicMasteryItem {
  topic_id: number;
  topic_name: string;
  difficulty: string;
  score: number;
  p_mastery: number;
  observed_accuracy: number;
  observed_total: number;
  last_reviewed_at?: string | null;
}

export interface SubjectMasteryItem {
  subject_id: number;
  subject_name: string;
  color: string;
  average_mastery: number;
  exam_date?: string | null;
  topics: TopicMasteryItem[];
}

export interface DayStudyTimeItem {
  date: string;
  study_minutes: number;
  session_count: number;
}

export interface MaterialItem {
  id: number;
  topic_id: number;
  title: string;
  file_name: string;
  file_type: string;
  file_size: number;
  status: "completed" | "processing" | "failed";
  created_at: string;
}

export interface NoteItem {
  id: number;
  topic_id: number;
  topic_name?: string;
  subject_name?: string;
  title: string;
  content_markdown: string;
  is_ai_generated: boolean;
  created_at: string;
  updated_at: string;
}

export interface QuizQuestionItem {
  id: number;
  question_text: string;
  question_type: "multiple_choice" | "true_false" | "short_answer";
  options?: string[] | null;
  order_index: number;
}

export interface QuizItem {
  id: number;
  topic_id: number;
  topic_name?: string;
  subject_name?: string;
  title: string;
  total_questions: number;
  created_at: string;
  questions?: QuizQuestionItem[];
}

export interface QuizAttemptResult {
  attempt_id: number;
  score: number;
  max_score: number;
  percentage: number;
  completed_at: string;
  results: {
    question_id: number;
    question_text: string;
    selected_answer: string;
    correct_answer: string;
    is_correct: boolean;
    explanation: string;
  }[];
}

export interface FlashcardItem {
  id: number;
  topic_id: number;
  topic_name?: string;
  subject_name?: string;
  front: string;
  back: string;
  explanation?: string | null;
  difficulty: string;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
  due_date?: string | null;
  last_reviewed_at?: string | null;
}

export interface QuestionPaperItem {
  id: number;
  subject_id: number;
  subject_name?: string;
  title: string;
  exam_type: string;
  duration_minutes: number;
  total_marks: number;
  created_at: string;
  content?: {
    instructions: string[];
    sections: {
      name: string;
      description: string;
      section_code: string;
      total_marks: number;
      questions: {
        id: string;
        question_text: string;
        marks: number;
        options?: string[];
        model_answer?: string;
        rubric?: string;
      }[];
    }[];
  };
}

export interface RoadmapTaskItem {
  id: string;
  title: string;
  topic_name: string;
  task_type: "learn" | "review" | "quiz" | "practice";
  estimated_minutes: number;
  completed: boolean;
}

export interface RoadmapPhaseItem {
  phase_number: number;
  name: string;
  timeframe: string;
  summary: string;
  tasks: RoadmapTaskItem[];
}

export interface RoadmapItem {
  id: number;
  subject_id: number;
  title: string;
  roadmap?: {
    title: string;
    subject_name: string;
    total_estimated_hours: number;
    phases: RoadmapPhaseItem[];
  };
}

export interface TutorConversationItem {
  id: number;
  topic_id: number;
  topic_name: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface TutorMessageItem {
  id: number;
  sender: "user" | "assistant";
  content: string;
  created_at: string;
}
