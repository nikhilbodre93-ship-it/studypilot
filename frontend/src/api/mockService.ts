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
  QuizItem,
  QuizAttemptResult,
  FlashcardItem,
  NoteItem,
  QuestionPaperItem,
  RoadmapItem,
  TutorConversationItem,
  TutorMessageItem,
} from "@/types";

// LocalStorage Keys
const STORAGE_KEYS = {
  USER: "studypilot_mock_user",
  SUBJECTS: "studypilot_mock_subjects",
  TOPICS: "studypilot_mock_topics",
  SESSIONS: "studypilot_mock_sessions",
  PLAN: "studypilot_mock_plan",
  CARDS: "studypilot_mock_cards",
  QUIZZES: "studypilot_mock_quizzes",
  NOTES: "studypilot_mock_notes",
  TUTOR: "studypilot_mock_tutor",
};

// Initial Seed Data
const DEFAULT_USER: User = {
  id: 1,
  email: "demo@studypilot.io",
  full_name: "Alex Chen",
  is_active: true,
  created_at: new Date().toISOString(),
};

const DEFAULT_SUBJECTS: Subject[] = [
  {
    id: 1,
    user_id: 1,
    name: "Biology",
    description: "Cellular biology, genetic processes, and inheritance systems.",
    exam_date: new Date(Date.now() + 45 * 86400000).toISOString().split("T")[0],
    color: "#2F5D46",
    topic_count: 2,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 2,
    user_id: 1,
    name: "Mathematics",
    description: "Higher mathematics focusing on integral calculus and applied probability.",
    exam_date: new Date(Date.now() + 30 * 86400000).toISOString().split("T")[0],
    color: "#3B82F6",
    topic_count: 2,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 3,
    user_id: 1,
    name: "Computer Engineering",
    description: "Core computer science fundamentals: hardware-software interface and algorithms.",
    exam_date: new Date(Date.now() + 60 * 86400000).toISOString().split("T")[0],
    color: "#6366F1",
    topic_count: 3,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

const DEFAULT_TOPICS: Topic[] = [
  {
    id: 1,
    subject_id: 1,
    name: "Cell structure",
    description: "Prokaryotic vs eukaryotic cells, organelle functions, and membrane dynamics.",
    difficulty: "medium",
    order_index: 0,
    mastery_score: 0.72,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 2,
    subject_id: 1,
    name: "Genetics & inheritance",
    description: "Mendelian genetics, DNA replication, gene expression, and pedigree charts.",
    difficulty: "hard",
    order_index: 1,
    mastery_score: 0.45,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 3,
    subject_id: 2,
    name: "Calculus: integration",
    description: "Definite/indefinite integrals, substitution, integration by parts, and area under curves.",
    difficulty: "hard",
    order_index: 0,
    mastery_score: 0.38,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 4,
    subject_id: 2,
    name: "Statistics & Probability",
    description: "Probability distributions, hypothesis testing, confidence intervals, and regression.",
    difficulty: "medium",
    order_index: 1,
    mastery_score: 0.65,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 5,
    subject_id: 3,
    name: "Data structures",
    description: "Arrays, linked lists, trees, graphs, heaps, hash tables, and asymptotic complexity.",
    difficulty: "medium",
    order_index: 0,
    mastery_score: 0.84,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 6,
    subject_id: 3,
    name: "Computer architecture",
    description: "Instruction set architecture (ISA), pipelining, cache memory hierarchy, and ALU design.",
    difficulty: "hard",
    order_index: 1,
    mastery_score: 0.52,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 7,
    subject_id: 3,
    name: "Operating systems",
    description: "Process management, virtual memory, concurrency, deadlocks, and filesystem structures.",
    difficulty: "hard",
    order_index: 2,
    mastery_score: 0.41,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

const DEFAULT_FLASHCARDS: FlashcardItem[] = [
  {
    id: 1,
    topic_id: 1,
    topic_name: "Cell structure",
    subject_name: "Biology",
    front: "What is the primary function of the mitochondrion?",
    back: "It produces ATP through cellular respiration, often called the powerhouse of the cell.",
    explanation: "Inner cristae contain ATP synthase complexes driven by a proton gradient.",
    difficulty: "easy",
    ease_factor: 2.5,
    interval_days: 3,
    repetitions: 2,
    due_date: new Date().toISOString(),
  },
  {
    id: 2,
    topic_id: 2,
    topic_name: "Genetics & inheritance",
    subject_name: "Biology",
    front: "State Mendel's Law of Independent Assortment.",
    back: "Alleles of two (or more) different genes get sorted into gametes independently of one another.",
    explanation: "Applies to genes located on different chromosomes or far apart on the same chromosome.",
    difficulty: "hard",
    ease_factor: 2.1,
    interval_days: 1,
    repetitions: 1,
    due_date: new Date().toISOString(),
  },
  {
    id: 3,
    topic_id: 3,
    topic_name: "Calculus: integration",
    subject_name: "Mathematics",
    front: "What is the formula for integration by parts?",
    back: "∫ u dv = u·v - ∫ v du",
    explanation: "Derived directly from the product rule of differentiation: d(uv) = u dv + v du.",
    difficulty: "hard",
    ease_factor: 2.3,
    interval_days: 2,
    repetitions: 1,
    due_date: new Date().toISOString(),
  },
  {
    id: 4,
    topic_id: 5,
    topic_name: "Data structures",
    subject_name: "Computer Engineering",
    front: "What is the average time complexity of searching in a Balanced Binary Search Tree (AVL / Red-Black)?",
    back: "O(log n)",
    explanation: "Tree height is strictly bounded to O(log n) through rebalancing rotations.",
    difficulty: "medium",
    ease_factor: 2.6,
    interval_days: 5,
    repetitions: 3,
    due_date: new Date().toISOString(),
  },
];

const DEFAULT_QUIZZES: QuizItem[] = [
  {
    id: 1,
    topic_id: 1,
    topic_name: "Cell structure",
    subject_name: "Biology",
    title: "Cell Organelles & Membrane Dynamics Quiz",
    total_questions: 3,
    created_at: new Date().toISOString(),
    questions: [
      {
        id: 101,
        question_text: "Which organelle is responsible for post-translational modification and protein sorting?",
        question_type: "multiple_choice",
        options: ["Golgi apparatus", "Ribosome", "Lysosome", "Centrosome"],
        order_index: 0,
      },
      {
        id: 102,
        question_text: "Phospholipid bilayers have hydrophilic heads and hydrophobic tails.",
        question_type: "true_false",
        options: ["True", "False"],
        order_index: 1,
      },
      {
        id: 103,
        question_text: "Which cytoskeletal component facilitates muscle contraction in conjunction with myosin?",
        question_type: "multiple_choice",
        options: ["Actin microfilaments", "Microtubules", "Intermediate filaments", "Keratin"],
        order_index: 2,
      },
    ],
  },
  {
    id: 2,
    topic_id: 5,
    topic_name: "Data structures",
    subject_name: "Computer Engineering",
    title: "Trees & Complexity Diagnostic",
    total_questions: 2,
    created_at: new Date().toISOString(),
    questions: [
      {
        id: 201,
        question_text: "What is the worst-case lookup time in an unbalanced Binary Search Tree?",
        question_type: "multiple_choice",
        options: ["O(n)", "O(log n)", "O(1)", "O(n log n)"],
        order_index: 0,
      },
      {
        id: 202,
        question_text: "A heap allows finding the maximum or minimum element in O(1) constant time.",
        question_type: "true_false",
        options: ["True", "False"],
        order_index: 1,
      },
    ],
  },
];

function loadItem<T>(key: string, defaultValue: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : defaultValue;
  } catch {
    return defaultValue;
  }
}

function saveItem<T>(key: string, value: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore
  }
}

export function handleMockRequest<T>(endpoint: string, options: RequestInit = {}): T {
  const method = (options.method || "GET").toUpperCase();
  const url = new URL(`http://localhost${endpoint}`);
  const path = url.pathname;
  let body: any = {};
  if (options.body && typeof options.body === "string") {
    try {
      body = JSON.parse(options.body);
    } catch {
      // ignore
    }
  }

  // --- AUTH ---
  if (path === "/auth/login" || path === "/auth/register") {
    const user = loadItem<User>(STORAGE_KEYS.USER, DEFAULT_USER);
    if (body.full_name) user.full_name = body.full_name;
    if (body.email) user.email = body.email;
    saveItem(STORAGE_KEYS.USER, user);
    const authRes: AuthResponse = {
      access_token: "mock-jwt-token-active",
      token_type: "bearer",
      expires_in: 86400,
    };
    return authRes as T;
  }

  if (path === "/auth/me") {
    const user = loadItem<User>(STORAGE_KEYS.USER, DEFAULT_USER);
    return user as T;
  }

  if (path === "/auth/logout") {
    return { message: "Successfully logged out", success: true } as T;
  }

  // --- SUBJECTS ---
  if (path === "/subjects" && method === "GET") {
    const subjects = loadItem<Subject[]>(STORAGE_KEYS.SUBJECTS, DEFAULT_SUBJECTS);
    return {
      items: subjects,
      total: subjects.length,
      page: 1,
      page_size: 50,
      pages: 1,
    } as T;
  }

  if (path === "/subjects" && method === "POST") {
    const subjects = loadItem<Subject[]>(STORAGE_KEYS.SUBJECTS, DEFAULT_SUBJECTS);
    const newSub: Subject = {
      id: Date.now(),
      user_id: 1,
      name: body.name || "New Subject",
      description: body.description || "",
      exam_date: body.exam_date || null,
      color: body.color || "#2F5D46",
      topic_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    subjects.unshift(newSub);
    saveItem(STORAGE_KEYS.SUBJECTS, subjects);
    return newSub as T;
  }

  if (path.startsWith("/subjects/") && path.endsWith("/topics") && method === "GET") {
    const parts = path.split("/");
    const subId = parseInt(parts[2], 10);
    const topics = loadItem<Topic[]>(STORAGE_KEYS.TOPICS, DEFAULT_TOPICS).filter((t) => t.subject_id === subId);
    return { items: topics, total: topics.length } as T;
  }

  if (path.startsWith("/subjects/") && path.endsWith("/topics") && method === "POST") {
    const parts = path.split("/");
    const subId = parseInt(parts[2], 10);
    const topics = loadItem<Topic[]>(STORAGE_KEYS.TOPICS, DEFAULT_TOPICS);
    const newTopic: Topic = {
      id: Date.now(),
      subject_id: subId,
      name: body.name,
      description: body.description || "",
      difficulty: body.difficulty || "medium",
      order_index: topics.length,
      mastery_score: 0.3,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    topics.push(newTopic);
    saveItem(STORAGE_KEYS.TOPICS, topics);
    return newTopic as T;
  }

  // --- REVISION QUEUE ---
  if (path === "/revision/queue") {
    const res: RevisionQueueResponse = {
      available_minutes: 60,
      total_scheduled_minutes: 65,
      sessions_count: 3,
      is_exam_mode_active: false,
      queue: [
        {
          topic_id: 3,
          topic_name: "Calculus: integration",
          subject_id: 2,
          subject_name: "Mathematics",
          duration_minutes: 25,
          session_type: "review",
          reason: "High forgetting risk (decay: 0.62) & upcoming exam in 30 days",
          priority_score: 88.4,
          scheduled_order: 1,
          next_review_date: new Date().toISOString(),
        },
        {
          topic_id: 2,
          topic_name: "Genetics & inheritance",
          subject_id: 1,
          subject_name: "Biology",
          duration_minutes: 25,
          session_type: "learn",
          reason: "Low mastery threshold (45%) requiring focused reinforcement",
          priority_score: 79.2,
          scheduled_order: 2,
          next_review_date: new Date().toISOString(),
        },
        {
          topic_id: 7,
          topic_name: "Operating systems",
          subject_id: 3,
          subject_name: "Computer Engineering",
          duration_minutes: 15,
          session_type: "rapid_review",
          reason: "Spaced repetition flashcards due for review",
          priority_score: 68.0,
          scheduled_order: 3,
          next_review_date: new Date().toISOString(),
        },
      ],
    };
    return res as T;
  }

  if (path.startsWith("/revision/explain/")) {
    const parts = path.split("/");
    const topicId = parseInt(parts[3], 10);
    const topic = loadItem<Topic[]>(STORAGE_KEYS.TOPICS, DEFAULT_TOPICS).find((t) => t.id === topicId);
    const breakdown: TopicPriorityBreakdown = {
      topic_id: topicId,
      topic_name: topic?.name || "Topic",
      subject_id: topic?.subject_id || 1,
      subject_name: "Subject",
      priority_score: 84.5,
      base_score: 65.0,
      exam_proximity_multiplier: 1.3,
      is_exam_mode: false,
      days_until_exam: 30,
      components: {
        mastery: 28.5,
        quiz_error: 16.0,
        overdue_cards: 12.0,
        difficulty: 8.0,
        forgetting: 18.0,
      },
      raw_metrics: {
        score: topic?.mastery_score ? topic.mastery_score * 100 : 45,
        attempts: 12,
        observed_accuracy: 0.68,
        overdue_cards_count: 3,
        days_since_last_study: 4,
        difficulty: topic?.difficulty || "hard",
        days_until_exam: 30,
      },
      reason: "High forgetting risk combined with low mastery score.",
    };
    return breakdown as T;
  }

  // --- PLAN ---
  if (path === "/plan/schedule") {
    const plan = loadItem<PlanSession[]>(STORAGE_KEYS.PLAN, [
      {
        id: 1,
        user_id: 1,
        subject_id: 2,
        topic_id: 3,
        scheduled_date: new Date().toISOString().split("T")[0],
        scheduled_order: 1,
        duration_minutes: 25,
        session_type: "review",
        status: "pending",
        reason: "Exam in 30 days; high priority",
        created_at: new Date().toISOString(),
        subject_name: "Mathematics",
        topic_name: "Calculus: integration",
      },
      {
        id: 2,
        user_id: 1,
        subject_id: 1,
        topic_id: 2,
        scheduled_date: new Date().toISOString().split("T")[0],
        scheduled_order: 2,
        duration_minutes: 25,
        session_type: "learn",
        status: "pending",
        reason: "Genetics concept reinforcement",
        created_at: new Date().toISOString(),
        subject_name: "Biology",
        topic_name: "Genetics & inheritance",
      },
      {
        id: 3,
        user_id: 1,
        subject_id: 3,
        topic_id: 5,
        scheduled_date: new Date().toISOString().split("T")[0],
        scheduled_order: 3,
        duration_minutes: 20,
        session_type: "quiz",
        status: "pending",
        reason: "Tree structures diagnostic check",
        created_at: new Date().toISOString(),
        subject_name: "Computer Engineering",
        topic_name: "Data structures",
      },
    ]);
    return plan as T;
  }

  if (path === "/plan/generate") {
    return {
      message: "Plan generated successfully",
      total_sessions_created: 14,
      start_date: new Date().toISOString().split("T")[0],
      end_date: new Date(Date.now() + 7 * 86400000).toISOString().split("T")[0],
    } as T;
  }

  if (path.startsWith("/plan/sessions/") && method === "PATCH") {
    const parts = path.split("/");
    const id = parseInt(parts[3], 10);
    const plan = loadItem<PlanSession[]>(STORAGE_KEYS.PLAN, []);
    const item = plan.find((p) => p.id === id);
    if (item && body.status) {
      item.status = body.status;
      saveItem(STORAGE_KEYS.PLAN, plan);
      return item as T;
    }
    return { id, status: body.status || "completed" } as T;
  }

  // --- ANALYTICS ---
  if (path === "/analytics/summary") {
    const res: AnalyticsSummary = {
      overall_mastery_pct: 68,
      total_subjects: 3,
      total_topics: 7,
      mastered_topics_count: 2,
      in_progress_topics_count: 5,
      total_study_minutes: 420,
      total_study_sessions: 16,
      cards_overdue_count: 4,
      upcoming_exams: [
        {
          subject_id: 2,
          subject_name: "Mathematics",
          exam_date: new Date(Date.now() + 30 * 86400000).toISOString().split("T")[0],
          days_remaining: 30,
          is_exam_mode: false,
          color: "#3B82F6",
        },
        {
          subject_id: 1,
          subject_name: "Biology",
          exam_date: new Date(Date.now() + 45 * 86400000).toISOString().split("T")[0],
          days_remaining: 45,
          is_exam_mode: false,
          color: "#2F5D46",
        },
      ],
    };
    return res as T;
  }

  if (path === "/analytics/subjects") {
    const subjects = loadItem<Subject[]>(STORAGE_KEYS.SUBJECTS, DEFAULT_SUBJECTS);
    const res: SubjectMasteryItem[] = subjects.map((s) => ({
      subject_id: s.id,
      subject_name: s.name,
      color: s.color,
      average_mastery: 0.65,
      exam_date: s.exam_date,
      topics: [
        {
          topic_id: 1,
          topic_name: "Fundamentals",
          difficulty: "medium",
          score: 75,
          p_mastery: 0.75,
          observed_accuracy: 0.82,
          observed_total: 15,
        },
      ],
    }));
    return res as T;
  }

  if (path === "/analytics/time-series") {
    const days: DayStudyTimeItem[] = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(Date.now() - i * 86400000).toISOString().split("T")[0];
      days.push({
        date: d,
        study_minutes: [35, 50, 45, 60, 25, 70, 45][6 - i] || 40,
        session_count: [1, 2, 2, 3, 1, 3, 2][6 - i] || 2,
      });
    }
    return days as T;
  }

  // --- STUDY SESSIONS ---
  if (path === "/study-sessions" && method === "GET") {
    return loadItem<StudySession[]>(STORAGE_KEYS.SESSIONS, [
      {
        id: 1,
        user_id: 1,
        subject_id: 2,
        topic_id: 3,
        duration_minutes: 25,
        session_type: "pomodoro",
        notes: "Integration by parts solved 5 questions.",
        created_at: new Date().toISOString(),
        subject_name: "Mathematics",
        topic_name: "Calculus: integration",
      },
    ]) as T;
  }

  if (path === "/study-sessions" && method === "POST") {
    const sessions = loadItem<StudySession[]>(STORAGE_KEYS.SESSIONS, []);
    const newSession: StudySession = {
      id: Date.now(),
      user_id: 1,
      subject_id: body.subject_id,
      topic_id: body.topic_id,
      duration_minutes: body.duration_minutes || 25,
      session_type: body.session_type || "pomodoro",
      notes: body.notes || "",
      created_at: new Date().toISOString(),
    };
    sessions.unshift(newSession);
    saveItem(STORAGE_KEYS.SESSIONS, sessions);
    return newSession as T;
  }

  if (path === "/study-sessions/summary") {
    const res: StudySessionSummary = {
      total_sessions: 16,
      total_minutes: 420,
      total_hours: 7.0,
      by_type: { pomodoro: 10, review: 4, quiz: 2 },
    };
    return res as T;
  }

  // --- FLASHCARDS ---
  if (path.startsWith("/flashcards")) {
    const cards = loadItem<FlashcardItem[]>(STORAGE_KEYS.CARDS, DEFAULT_FLASHCARDS);
    if (path.includes("/review") && method === "POST") {
      return { message: "Review recorded successfully", ease_factor: 2.5, interval_days: 3 } as T;
    }
    return { items: cards, total: cards.length } as T;
  }

  // --- QUIZZES ---
  if (path.startsWith("/quizzes")) {
    const quizzes = loadItem<QuizItem[]>(STORAGE_KEYS.QUIZZES, DEFAULT_QUIZZES);
    if (path.includes("/submit")) {
      const result: QuizAttemptResult = {
        attempt_id: Date.now(),
        score: 3,
        max_score: 3,
        percentage: 100,
        completed_at: new Date().toISOString(),
        results: [
          {
            question_id: 101,
            question_text: "Which organelle is responsible for protein sorting?",
            selected_answer: "Golgi apparatus",
            correct_answer: "Golgi apparatus",
            is_correct: true,
            explanation: "The Golgi apparatus modifies and routes synthesized proteins.",
          },
        ],
      };
      return result as T;
    }
    if (path.includes("/topic/")) {
      return quizzes as T;
    }
    return { items: quizzes, total: quizzes.length } as T;
  }

  // --- NOTES ---
  if (path.startsWith("/notes")) {
    const notes = loadItem<NoteItem[]>(STORAGE_KEYS.NOTES, [
      {
        id: 1,
        topic_id: 1,
        topic_name: "Cell structure",
        subject_name: "Biology",
        title: "Membrane Transport Key Summary",
        content_markdown: "### Passive vs Active Transport\n- **Passive:** Diffusion along concentration gradient (no ATP).\n- **Active:** Requires ATP (e.g. Sodium-Potassium pump).",
        is_ai_generated: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ]);
    return { items: notes, total: notes.length } as T;
  }

  // --- TUTOR ---
  if (path.startsWith("/tutor")) {
    if (path.includes("/messages") && method === "POST") {
      const query = body.content || "your question";
      return {
        id: Date.now(),
        conversation_id: 1,
        sender: "assistant",
        content: `Great question! Regarding "${query.slice(0, 50)}...", here is a key breakdown:\n\n1. **Core Concept**: Focus on the fundamental definitions and mechanics first.\n2. **Common Trap**: Watch out for edge cases and variable substitutions.\n3. **Exam Strategy**: Always verify units and state your intermediate formula.\n\nWould you like a quick practice question to test your understanding?`,
        created_at: new Date().toISOString(),
      } as T;
    }
    return [
      {
        id: 1,
        title: "Study Guidance & Concept Review",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ] as T;
  }

  // Fallback generic response
  return { items: [], total: 0, message: "OK", success: true } as T;
}
