import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ToastProvider } from "../components/ui/Toast";
import { MyLearningPage } from "../pages/MyLearningPage";
import { NotesPage } from "../pages/NotesPage";
import { QuizzesPage } from "../pages/QuizzesPage";
import { FlashcardsPage } from "../pages/FlashcardsPage";
import { QuestionPapersPage } from "../pages/QuestionPapersPage";
import { RoadmapPage } from "../pages/RoadmapPage";
import { AITutorPage } from "../pages/AITutorPage";

// Mock api methods so tests render cleanly without network dependencies
vi.mock("../api/client", () => ({
  api: {
    subjects: {
      list: vi.fn().mockResolvedValue({
        items: [
          { id: 1, name: "Biology", color: "#2F5D46", exam_date: "2026-11-01" },
        ],
        total: 1,
      }),
    },
    topics: {
      listForSubject: vi.fn().mockResolvedValue({
        items: [
          { id: 1, name: "Cell Structure", difficulty: "medium", mastery_score: 0.45 },
        ],
        total: 1,
      }),
    },
    notes: {
      list: vi.fn().mockResolvedValue([
        {
          id: 1,
          title: "Cell Membrane Notes",
          content_markdown: "Detailed notes on fluid mosaic model.",
          is_ai_generated: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]),
      getExportUrl: vi.fn().mockReturnValue("/api/v1/notes/1/export"),
    },
    quizzes: {
      getHistory: vi.fn().mockResolvedValue([]),
    },
    flashcards: {
      list: vi.fn().mockResolvedValue([
        {
          id: 1,
          front: "What is ATP?",
          back: "Adenosine triphosphate, cellular energy currency.",
          interval_days: 1,
          ease_factor: 2.5,
          repetitions: 1,
        },
      ]),
      getExportPdfUrl: vi.fn().mockReturnValue("/api/v1/flashcards/export/pdf"),
    },
    questionPapers: {
      list: vi.fn().mockResolvedValue([]),
      getExportPdfUrl: vi.fn().mockReturnValue("/api/v1/question-papers/1/export/pdf"),
    },
    roadmap: {
      getBySubject: vi.fn().mockResolvedValue({ roadmap: null }),
    },
    tutor: {
      listConversations: vi.fn().mockResolvedValue([]),
    },
  },
}));

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>{component}</ToastProvider>
    </QueryClientProvider>
  );
};

describe("Phase 5 Frontend Pages Rendering", () => {
  const noop = () => {};

  it("renders MyLearningPage header and knowledge base section", () => {
    renderWithProviders(<MyLearningPage onNavigate={noop} />);
    expect(screen.getByRole("heading", { name: /My Learning/i })).toBeInTheDocument();
    expect(screen.getByText(/RAG Knowledge Ingestion/i)).toBeInTheDocument();
  });

  it("renders NotesPage with generator button", () => {
    renderWithProviders(<NotesPage onNavigate={noop} />);
    expect(screen.getByRole("heading", { name: /Study Notes/i })).toBeInTheDocument();
    expect(screen.getAllByText(/Generate New Note/i).length).toBeGreaterThan(0);
  });

  it("renders QuizzesPage with Practice and Exam options", () => {
    renderWithProviders(<QuizzesPage onNavigate={noop} />);
    expect(screen.getByRole("heading", { name: /Practice Quizzes/i })).toBeInTheDocument();
    expect(screen.getByText(/New Practice Quiz/i)).toBeInTheDocument();
  });

  it("renders FlashcardsPage with deck options", () => {
    renderWithProviders(<FlashcardsPage onNavigate={noop} />);
    expect(screen.getByRole("heading", { name: /Flashcards/i })).toBeInTheDocument();
    expect(screen.getAllByText(/Generate Deck/i).length).toBeGreaterThan(0);
  });

  it("renders QuestionPapersPage with mock exam generator", () => {
    renderWithProviders(<QuestionPapersPage onNavigate={noop} />);
    expect(screen.getAllByRole("heading", { name: /Question Papers/i }).length).toBeGreaterThan(0);
    expect(screen.getByText(/Generate Paper/i)).toBeInTheDocument();
  });

  it("renders RoadmapPage with Phasing header", () => {
    renderWithProviders(<RoadmapPage onNavigate={noop} />);
    expect(screen.getByRole("heading", { name: /Learning Roadmap/i })).toBeInTheDocument();
    expect(screen.getAllByText(/Generate Roadmap/i).length).toBeGreaterThan(0);
  });

  it("renders AITutorPage with Socratic AI companion interface", () => {
    renderWithProviders(<AITutorPage onNavigate={noop} />);
    expect(screen.getByRole("heading", { name: /AI Tutor/i })).toBeInTheDocument();
    expect(screen.getByText(/Check My Understanding/i)).toBeInTheDocument();
  });
});
