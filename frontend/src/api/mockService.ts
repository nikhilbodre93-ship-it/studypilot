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
  TUTOR_CONVS: "studypilot_mock_tutor_convs",
  TUTOR_MSGS: "studypilot_mock_tutor_msgs",
  PAPERS: "studypilot_mock_papers",
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
    topic_id: 7,
    topic_name: "Operating systems",
    subject_name: "Computer Engineering",
    front: "What is an Operating System (OS)?",
    back: "An OS is system software that manages computer hardware, software resources, and provides common services for computer programs (e.g. process management, memory allocation, filesystem).",
    explanation: "Acts as an intermediary between the user/applications and the physical computer hardware.",
    difficulty: "easy",
    ease_factor: 2.5,
    interval_days: 3,
    repetitions: 2,
    due_date: new Date().toISOString(),
  },
  {
    id: 2,
    topic_id: 7,
    topic_name: "Operating systems",
    subject_name: "Computer Engineering",
    front: "What are the four essential conditions for Deadlock?",
    back: "1. Mutual Exclusion\n2. Hold and Wait\n3. No Preemption\n4. Circular Wait (Coffman Conditions).",
    explanation: "If any one of these four conditions is prevented or broken, deadlock cannot occur.",
    difficulty: "hard",
    ease_factor: 2.1,
    interval_days: 1,
    repetitions: 1,
    due_date: new Date().toISOString(),
  },
  {
    id: 3,
    topic_id: 1,
    topic_name: "Cell structure",
    subject_name: "Biology",
    front: "What is the primary function of the mitochondrion?",
    back: "It produces ATP through cellular respiration, often referred to as the powerhouse of the cell.",
    explanation: "Inner cristae contain ATP synthase complexes driven by a proton concentration gradient.",
    difficulty: "easy",
    ease_factor: 2.5,
    interval_days: 4,
    repetitions: 3,
    due_date: new Date().toISOString(),
  },
  {
    id: 4,
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
    id: 5,
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

const DEFAULT_NOTES: NoteItem[] = [
  {
    id: 1,
    topic_id: 7,
    topic_name: "Operating systems",
    subject_name: "Computer Engineering",
    title: "Operating Systems — Comprehensive Revision Notes",
    content_markdown: `## Operating Systems Core Architecture

An **Operating System (OS)** is a program that manages a computer's hardware and acts as an intermediary between the user and computer hardware.

### 1. Key Responsibilities
- **Process Management:** CPU scheduling, process creation/termination, synchronization, and deadlock prevention.
- **Memory Management:** Tracking memory usage, allocation/deallocation, paging, segmentation, and virtual memory.
- **Storage Management:** File system organization, directory structures, and disk scheduling algorithms (SCAN, C-SCAN).
- **Protection & Security:** User authentication, access control lists, and memory isolation (User Mode vs Kernel Mode).

### 2. Process vs Thread
- A **process** is a program in execution with its own address space, file handles, and memory.
- A **thread** is a lightweight unit of CPU execution within a process that shares the code, data, and OS resources with peer threads.

### 3. Virtual Memory & Paging
Virtual memory separates user logical memory from physical memory. Paging maps logical addresses into physical frames via a **Page Table**.
- **Page Fault:** Occurs when an accessed page is not currently in physical RAM.
- **Page Replacement Algorithms:** FIFO, LRU (Least Recently Used), and Optimal (Belady's anomaly occurs in FIFO).`,
    is_ai_generated: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 2,
    topic_id: 1,
    topic_name: "Cell structure",
    subject_name: "Biology",
    title: "Cell Organelles & Membrane Dynamics",
    content_markdown: `## Cellular Biology Key Summary

### 1. Eukaryotic vs Prokaryotic Cells
- **Prokaryotes:** Lack a membrane-bound nucleus and membrane-bound organelles (e.g. Bacteria, Archaea). Circular DNA.
- **Eukaryotes:** Contain a true nucleus enclosed by a double membrane and complex organelles (Mitochondria, ER, Golgi).

### 2. Membrane Transport
- **Passive Transport:** Diffusion and facilitated diffusion (via channel/carrier proteins) along concentration gradient without ATP.
- **Active Transport:** Movement against concentration gradient requiring ATP (e.g. Na+/K+ ATPase pump).`,
    is_ai_generated: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

const DEFAULT_QUIZZES: QuizItem[] = [
  {
    id: 1,
    topic_id: 7,
    topic_name: "Operating systems",
    subject_name: "Computer Engineering",
    title: "Operating Systems Core Diagnostics",
    total_questions: 3,
    created_at: new Date().toISOString(),
    questions: [
      {
        id: 101,
        question_text: "Which of the following is NOT one of Coffman's four deadlock conditions?",
        question_type: "multiple_choice",
        options: ["Mutual Exclusion", "Circular Wait", "Preemption allowed", "Hold and Wait"],
        order_index: 0,
      },
      {
        id: 102,
        question_text: "Virtual memory allows the execution of processes that are not completely in physical memory.",
        question_type: "true_false",
        options: ["True", "False"],
        order_index: 1,
      },
      {
        id: 103,
        question_text: "What hardware component translates virtual page numbers into physical page frame numbers?",
        question_type: "multiple_choice",
        options: ["Memory Management Unit (MMU)", "ALU", "Cache Controller", "DMA Controller"],
        order_index: 2,
      },
    ],
  },
  {
    id: 2,
    topic_id: 1,
    topic_name: "Cell structure",
    subject_name: "Biology",
    title: "Cell Organelles & Membrane Dynamics",
    total_questions: 2,
    created_at: new Date().toISOString(),
    questions: [
      {
        id: 201,
        question_text: "Which organelle is responsible for post-translational modification and protein sorting?",
        question_type: "multiple_choice",
        options: ["Golgi apparatus", "Ribosome", "Lysosome", "Centrosome"],
        order_index: 0,
      },
      {
        id: 202,
        question_text: "Phospholipid bilayers have hydrophilic heads and hydrophobic fatty acid tails.",
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

/**
 * Intelligent client-side AI response generator for tutor chats
 */
export function generateAITutorResponse(userMessage: string, mode = "standard"): string {
  const query = userMessage.toLowerCase().trim();

  if (query.includes("os") || query.includes("operating system") || query.includes("osy")) {
    if (mode === "eli5") {
      return `### Operating System Explained Simply (ELI5) 💻

Think of your computer as a busy restaurant:
- **The Hardware (CPU, RAM, Hard Drive):** The kitchen, the chefs, and the storage pantry.
- **The Programs (Chrome, Spotify, Games):** The customers placing orders.
- **The Operating System (OS):** **The Head Manager!**

Without the manager, all customers would fight over the stoves and chefs at the same time. The OS decides who gets food first (**CPU scheduling**), where things are stored (**memory management**), and makes sure no customer crashes into another!`;
    }

    return `### Operating System (OS) Comprehensive Guide 🖥️

An **Operating System (OS)** is fundamental system software that manages computer hardware and software resources and provides common services for computer programs.

---

### 1. Key Functions of an Operating System
- **Process Management:** Allocates CPU time to competing processes, handles context switching, and prevents deadlocks.
- **Memory Management:** Manages RAM allocation, virtual memory paging, and memory isolation between processes.
- **File System Management:** Organizes files into hierarchical directories and handles read/write permissions.
- **Device & I/O Handling:** Uses device drivers and interrupts to communicate with disks, keyboards, and network adapters.
- **Security & Protection:** Distinguishes between User Mode and Kernel Mode (ring 0) to prevent rogue programs from crashing the system.

---

### 2. Famous Operating Systems
- **Desktop/Laptop:** Linux (Ubuntu, Debian, Fedora), Windows, macOS.
- **Mobile:** Android (Linux kernel), iOS (Darwin/Unix kernel).
- **Servers/Cloud:** Linux dominates >90% of global web servers and cloud containers.

---

💡 *Tip: Would you like to dive deeper into CPU Scheduling (Round Robin, FCFS) or Deadlock Prevention?*`;
  }

  if (query.includes("dbms") || query.includes("database")) {
    return `### Database Management Systems (DBMS) 🗄️

A **Database Management System (DBMS)** is software designed to store, retrieve, manage, and query structured and unstructured data reliably.

---

### 1. Why Use a DBMS over Files?
- **Data Integrity & Consistency:** Eliminates data redundancy and inconsistencies.
- **Concurrent Access:** Multiple users can read and write simultaneously without corrupting data.
- **Security:** Granular role-based permissions and encrypted storage.
- **ACID Transactions:** Ensures critical financial and user data never gets half-written during crashes.

---

### 2. The ACID Properties
- **Atomicity:** "All or nothing" — if one step fails, the entire transaction rolls back.
- **Consistency:** Transactions only bring the database from one valid state to another.
- **Isolation:** Concurrent transactions execute without interfering with one another.
- **Durability:** Once committed, data survives power outages and hardware failures.

---

### 3. SQL vs NoSQL
- **Relational (SQL):** PostgreSQL, MySQL, SQLite (strict tables, schemas, and foreign keys).
- **Non-Relational (NoSQL):** MongoDB (documents), Redis (in-memory key-value), Neo4j (graphs).`;
  }

  // General fallback educational answer
  return `### AI Study Coach Breakdown 🧠

Regarding **"${userMessage.trim()}"**:

---

### 1. Fundamental Concept
This is a core topic in your syllabus. The most effective way to understand it is to break it down into:
- **Definition & Purpose:** What exact problem does this solve?
- **Mechanics:** How does the underlying system operate step-by-step?
- **Key Equations or Rules:** The mathematical or logical invariants governing it.

---

### 2. High-Yield Exam Strategy
- **Common Trap:** Conflating the theoretical model with implementation-specific details.
- **Key Marks:** Examiners always look for proper terminology, labeled diagrams, and step-by-step reasoning.

---

✨ *Would you like me to generate a 3-question mini quiz or create a set of revision flashcards for this topic?*`;
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

  // --- NOTES (Must return NoteItem[] array for list) ---
  if (path === "/notes" && method === "GET") {
    const notes = loadItem<NoteItem[]>(STORAGE_KEYS.NOTES, DEFAULT_NOTES);
    const search = url.searchParams.get("search")?.toLowerCase();
    const topicId = url.searchParams.get("topic_id");
    let filtered = notes;
    if (topicId) filtered = filtered.filter((n) => n.topic_id === parseInt(topicId, 10));
    if (search) filtered = filtered.filter((n) => n.title.toLowerCase().includes(search) || n.content_markdown.toLowerCase().includes(search));
    return filtered as T;
  }

  if (path === "/notes/generate" || (path === "/notes" && method === "POST")) {
    const notes = loadItem<NoteItem[]>(STORAGE_KEYS.NOTES, DEFAULT_NOTES);
    const topics = loadItem<Topic[]>(STORAGE_KEYS.TOPICS, DEFAULT_TOPICS);
    const selectedTopic = topics.find((t) => t.id === body.topic_id) || topics[0];
    const newNote: NoteItem = {
      id: Date.now(),
      topic_id: selectedTopic.id,
      topic_name: selectedTopic.name,
      subject_name: "Computer Engineering",
      title: `${selectedTopic.name} — AI Generated Study Notes`,
      content_markdown: `## ${selectedTopic.name} Comprehensive Study Notes\n\n### 1. Overview\n${selectedTopic.description || "Core theoretical foundations and applications in modern systems."}\n\n### 2. High-Yield Principles\n- **Principle A:** Always decompose the problem into fundamental invariants.\n- **Principle B:** Evaluate edge cases and boundary conditions.\n- **Principle C:** Practice active recall with self-testing.\n\n### 3. Exam Tips\nReview formulas, state assumptions clearly, and verify answers with dimension/units analysis.`,
      is_ai_generated: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    notes.unshift(newNote);
    saveItem(STORAGE_KEYS.NOTES, notes);
    return newNote as T;
  }

  if (path.startsWith("/notes/") && method === "DELETE") {
    const parts = path.split("/");
    const id = parseInt(parts[2], 10);
    let notes = loadItem<NoteItem[]>(STORAGE_KEYS.NOTES, DEFAULT_NOTES);
    notes = notes.filter((n) => n.id !== id);
    saveItem(STORAGE_KEYS.NOTES, notes);
    return { success: true } as T;
  }

  // --- FLASHCARDS (Must return FlashcardItem[] array for list) ---
  if (path === "/flashcards" && method === "GET") {
    const cards = loadItem<FlashcardItem[]>(STORAGE_KEYS.CARDS, DEFAULT_FLASHCARDS);
    const topicId = url.searchParams.get("topic_id");
    const search = url.searchParams.get("search")?.toLowerCase();
    let filtered = cards;
    if (topicId) filtered = filtered.filter((c) => c.topic_id === parseInt(topicId, 10));
    if (search) filtered = filtered.filter((c) => c.front.toLowerCase().includes(search) || c.back.toLowerCase().includes(search));
    return filtered as T;
  }

  if (path === "/flashcards/generate") {
    const cards = loadItem<FlashcardItem[]>(STORAGE_KEYS.CARDS, DEFAULT_FLASHCARDS);
    const topics = loadItem<Topic[]>(STORAGE_KEYS.TOPICS, DEFAULT_TOPICS);
    const topic = topics.find((t) => t.id === body.topic_id) || topics[0];

    const newCards: FlashcardItem[] = [
      {
        id: Date.now() + 1,
        topic_id: topic.id,
        topic_name: topic.name,
        subject_name: "Computer Engineering",
        front: `What is the core definition of ${topic.name}?`,
        back: `A fundamental area covering: ${topic.description || "essential concepts, algorithms, and models."}`,
        explanation: "Key conceptual question frequently appearing in standard exams.",
        difficulty: "medium",
        ease_factor: 2.5,
        interval_days: 1,
        repetitions: 0,
        due_date: new Date().toISOString(),
      },
      {
        id: Date.now() + 2,
        topic_id: topic.id,
        topic_name: topic.name,
        subject_name: "Computer Engineering",
        front: `What is a common pitfall or trap when analyzing ${topic.name}?`,
        back: "Overlooking edge cases and failing to verify base conditions.",
        explanation: "Critical for full-credit answers in midterm and final exams.",
        difficulty: "hard",
        ease_factor: 2.4,
        interval_days: 1,
        repetitions: 0,
        due_date: new Date().toISOString(),
      },
    ];

    const updated = [...newCards, ...cards];
    saveItem(STORAGE_KEYS.CARDS, updated);
    return { deck_title: `${topic.name} Flashcard Deck`, count: newCards.length, cards: newCards } as T;
  }

  if (path === "/flashcards" && method === "POST") {
    const cards = loadItem<FlashcardItem[]>(STORAGE_KEYS.CARDS, DEFAULT_FLASHCARDS);
    const topics = loadItem<Topic[]>(STORAGE_KEYS.TOPICS, DEFAULT_TOPICS);
    const topic = topics.find((t) => t.id === body.topic_id) || topics[0];
    const newCard: FlashcardItem = {
      id: Date.now(),
      topic_id: topic.id,
      topic_name: topic.name,
      subject_name: "Computer Engineering",
      front: body.front,
      back: body.back,
      explanation: body.explanation || "",
      difficulty: body.difficulty || "medium",
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
      due_date: new Date().toISOString(),
    };
    cards.unshift(newCard);
    saveItem(STORAGE_KEYS.CARDS, cards);
    return newCard as T;
  }

  if (path === "/flashcards/review" && method === "POST") {
    const cards = loadItem<FlashcardItem[]>(STORAGE_KEYS.CARDS, DEFAULT_FLASHCARDS);
    const card = cards.find((c) => c.id === body.flashcard_id);
    if (card) {
      card.repetitions = (card.repetitions || 0) + 1;
      card.interval_days = Math.max(1, Math.round((card.interval_days || 1) * (card.ease_factor || 2.5)));
      card.due_date = new Date(Date.now() + card.interval_days * 86400000).toISOString();
      card.last_reviewed_at = new Date().toISOString();
      saveItem(STORAGE_KEYS.CARDS, cards);
    }
    return { message: "Review recorded successfully", success: true } as T;
  }

  if (path.startsWith("/flashcards/") && method === "DELETE") {
    const parts = path.split("/");
    const id = parseInt(parts[2], 10);
    let cards = loadItem<FlashcardItem[]>(STORAGE_KEYS.CARDS, DEFAULT_FLASHCARDS);
    cards = cards.filter((c) => c.id !== id);
    saveItem(STORAGE_KEYS.CARDS, cards);
    return { success: true } as T;
  }

  // --- QUIZZES (Must return QuizItem[] array for list) ---
  if (path === "/quizzes" && method === "GET") {
    const quizzes = loadItem<QuizItem[]>(STORAGE_KEYS.QUIZZES, DEFAULT_QUIZZES);
    return quizzes as T;
  }

  if (path.startsWith("/quizzes/topic/")) {
    const parts = path.split("/");
    const topicId = parseInt(parts[3], 10);
    const quizzes = loadItem<QuizItem[]>(STORAGE_KEYS.QUIZZES, DEFAULT_QUIZZES).filter((q) => q.topic_id === topicId);
    return quizzes as T;
  }

  if (path === "/quizzes/generate") {
    const quizzes = loadItem<QuizItem[]>(STORAGE_KEYS.QUIZZES, DEFAULT_QUIZZES);
    const topics = loadItem<Topic[]>(STORAGE_KEYS.TOPICS, DEFAULT_TOPICS);
    const topic = topics.find((t) => t.id === body.topic_id) || topics[0];
    const newQuiz: QuizItem = {
      id: Date.now(),
      topic_id: topic.id,
      topic_name: topic.name,
      subject_name: "Computer Engineering",
      title: `${topic.name} Diagnostic Quiz`,
      total_questions: 3,
      created_at: new Date().toISOString(),
      questions: [
        {
          id: 501,
          question_text: `What is the principal advantage of ${topic.name}?`,
          question_type: "multiple_choice",
          options: ["High computational efficiency", "Reduced memory complexity", "Both of the above", "None of the above"],
          order_index: 0,
        },
        {
          id: 502,
          question_text: "Understanding boundary invariants helps prevent runtime exceptions.",
          question_type: "true_false",
          options: ["True", "False"],
          order_index: 1,
        },
      ],
    };
    quizzes.unshift(newQuiz);
    saveItem(STORAGE_KEYS.QUIZZES, quizzes);
    return newQuiz as T;
  }

  if (path.includes("/quizzes/") && path.endsWith("/submit")) {
    const result: QuizAttemptResult = {
      attempt_id: Date.now(),
      score: 3,
      max_score: 3,
      percentage: 100,
      completed_at: new Date().toISOString(),
      results: [
        {
          question_id: 101,
          question_text: "Which of the following is NOT one of Coffman's four deadlock conditions?",
          selected_answer: "Preemption allowed",
          correct_answer: "Preemption allowed",
          is_correct: true,
          explanation: "The condition is 'No Preemption', meaning resources cannot be forcibly seized.",
        },
      ],
    };
    return result as T;
  }

  // --- TUTOR CONVERSATIONS ---
  if (path === "/tutor/conversations" && method === "GET") {
    const convs = loadItem<TutorConversationItem[]>(STORAGE_KEYS.TUTOR_CONVS, [
      {
        id: 1,
        topic_id: 7,
        topic_name: "Operating systems",
        title: "Study Guidance & Concept Review",
        message_count: 2,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ]);
    return convs as T;
  }

  if (path.startsWith("/tutor/conversations/") && method === "GET") {
    const parts = path.split("/");
    const id = parseInt(parts[3], 10);
    return {
      id,
      topic_id: 7,
      title: "Operating Systems Guidance",
      messages: [
        {
          id: 1,
          conversation_id: id,
          sender: "assistant",
          content: "Hello! I am your AI Study Coach. Ask me any question about Operating Systems, DBMS, Mathematics, or Biology!",
          created_at: new Date().toISOString(),
        },
      ],
    } as T;
  }

  if (path === "/tutor/check-understanding") {
    return {
      question_text: "Which mechanism guarantees memory isolation between concurrent processes?",
      options: ["Paging and Page Tables", "ALU Pipeline", "Direct Memory Access (DMA)", "Bus arbitration"],
      correct_answer: "Paging and Page Tables",
      explanation: "Page tables map separate virtual address spaces into disjoint physical frames, preventing one process from reading another's memory.",
    } as T;
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
          topic_id: 7,
          topic_name: "Operating systems",
          subject_id: 3,
          subject_name: "Computer Engineering",
          duration_minutes: 25,
          session_type: "learn",
          reason: "Critical OS fundamentals & low mastery score (41%)",
          priority_score: 92.4,
          scheduled_order: 1,
          next_review_date: new Date().toISOString(),
        },
        {
          topic_id: 3,
          topic_name: "Calculus: integration",
          subject_id: 2,
          subject_name: "Mathematics",
          duration_minutes: 25,
          session_type: "review",
          reason: "High forgetting risk & upcoming exam in 30 days",
          priority_score: 84.1,
          scheduled_order: 2,
          next_review_date: new Date().toISOString(),
        },
        {
          topic_id: 2,
          topic_name: "Genetics & inheritance",
          subject_id: 1,
          subject_name: "Biology",
          duration_minutes: 15,
          session_type: "rapid_review",
          reason: "Spaced repetition flashcards due for review",
          priority_score: 76.0,
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
    const breakdown: TopicPriorityBreakdown = {
      topic_id: topicId,
      topic_name: "Topic Priority Analysis",
      subject_id: 1,
      subject_name: "Subject",
      priority_score: 88.5,
      base_score: 68.0,
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
        score: 42,
        attempts: 12,
        observed_accuracy: 0.65,
        overdue_cards_count: 2,
        days_since_last_study: 3,
        difficulty: "hard",
        days_until_exam: 30,
      },
      reason: "High memory decay rate combined with low mastery score.",
    };
    return breakdown as T;
  }

  // --- PLAN ---
  if (path === "/plan/schedule") {
    const plan = loadItem<PlanSession[]>(STORAGE_KEYS.PLAN, [
      {
        id: 1,
        user_id: 1,
        subject_id: 3,
        topic_id: 7,
        scheduled_date: new Date().toISOString().split("T")[0],
        scheduled_order: 1,
        duration_minutes: 25,
        session_type: "learn",
        status: "pending",
        reason: "Process scheduling & Deadlock prevention",
        created_at: new Date().toISOString(),
        subject_name: "Computer Engineering",
        topic_name: "Operating systems",
      },
      {
        id: 2,
        user_id: 1,
        subject_id: 2,
        topic_id: 3,
        scheduled_date: new Date().toISOString().split("T")[0],
        scheduled_order: 2,
        duration_minutes: 25,
        session_type: "review",
        status: "pending",
        reason: "Integration by parts problem sets",
        created_at: new Date().toISOString(),
        subject_name: "Mathematics",
        topic_name: "Calculus: integration",
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
      total_study_minutes: 450,
      total_study_sessions: 18,
      cards_overdue_count: 2,
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
        subject_id: 3,
        topic_id: 7,
        duration_minutes: 25,
        session_type: "pomodoro",
        notes: "Studied process scheduling and deadlock conditions.",
        created_at: new Date().toISOString(),
        subject_name: "Computer Engineering",
        topic_name: "Operating systems",
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
      total_sessions: 18,
      total_minutes: 450,
      total_hours: 7.5,
      by_type: { pomodoro: 12, review: 4, quiz: 2 },
    };
    return res as T;
  }

  // --- ROADMAP ---
  if (path.startsWith("/roadmap")) {
    return {
      id: 1,
      subject_id: 3,
      subject_name: "Computer Engineering",
      title: "Complete Computer Systems Mastery Roadmap",
      description: "Structured path from hardware foundations to advanced operating systems.",
      phases: [
        {
          phase_number: 1,
          name: "Foundations",
          tasks: [
            { id: "t1", title: "Data Structures & Big-O Complexity", completed: true },
            { id: "t2", title: "CPU Architecture & Pipelining", completed: true },
          ],
        },
        {
          phase_number: 2,
          name: "Operating Systems Core",
          tasks: [
            { id: "t3", title: "Process & Thread Scheduling", completed: false },
            { id: "t4", title: "Virtual Memory & Paging", completed: false },
            { id: "t5", title: "Deadlock Prevention Algorithms", completed: false },
          ],
        },
      ],
    } as T;
  }

  // --- QUESTION PAPERS ---
  if (path.startsWith("/question-papers")) {
    const papers: QuestionPaperItem[] = [
      {
        id: 1,
        subject_id: 3,
        subject_name: "Computer Engineering",
        title: "Midterm Mock Examination — Operating Systems",
        exam_type: "Midterm Exam",
        duration_minutes: 90,
        total_marks: 50,
        created_at: new Date().toISOString(),
        content: {
          instructions: ["Answer all questions.", "Time allowed: 90 minutes.", "Total marks: 50."],
          sections: [
            {
              name: "Section A: Conceptual Questions",
              description: "5 questions, 2 marks each",
              section_code: "A",
              total_marks: 10,
              questions: [
                {
                  id: "q1",
                  question_text: "Differentiate between a process and a thread.",
                  marks: 2,
                  model_answer: "A process has its own address space, whereas threads share memory within the same process.",
                },
                {
                  id: "q2",
                  question_text: "State the four Coffman conditions for deadlock.",
                  marks: 2,
                  model_answer: "Mutual exclusion, hold and wait, no preemption, and circular wait.",
                },
              ],
            },
          ],
        },
      },
    ];
    return papers as T;
  }

  return { items: [], total: 0, message: "OK", success: true } as T;
}
