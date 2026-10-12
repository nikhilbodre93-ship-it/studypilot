import React from "react";
import { EmptyState } from "@/components/ui/EmptyState";
import { NavItem } from "@/components/layout/Sidebar";

interface ComingSoonProps {
  tab: NavItem;
  onNavigate: (tab: NavItem) => void;
}

export const ComingSoonPage: React.FC<ComingSoonProps> = ({ tab, onNavigate }) => {
  switch (tab) {
    case "roadmap":
      return (
        <EmptyState
          phase={4}
          title="Learning roadmap"
          eyebrow="ADAPTIVE CURRICULUM"
          description="Visual topic dependency graphs that adapt as you conquer prerequisite concepts."
          previewFeatures={[
            "Visual knowledge dependency graph",
            "Prerequisite topic lock/unlock logic",
            "Target exam milestone checkpoints",
          ]}
          actionLabel="View Revision planner"
          onAction={() => onNavigate("planner")}
        />
      );

    case "notes":
      return (
        <EmptyState
          phase={4}
          title="Study notes"
          eyebrow="YOUR KNOWLEDGE, ORGANIZED"
          description="Capture an idea, build a useful summary, and keep your best notes close."
          previewFeatures={[
            "Note builder from topic or study material",
            "Structured Markdown editor with formula support",
            "Automatic key-concept extraction and cheat sheets",
          ]}
          actionLabel="View Dashboard"
          onAction={() => onNavigate("dashboard")}
        />
      );

    case "quizzes":
      return (
        <EmptyState
          phase={4}
          title="Practice quizzes"
          eyebrow="RETRIEVAL PRACTICE"
          description="Practice a topic, hear questions aloud, or answer by voice."
          previewFeatures={[
            "Automated multiple-choice and conceptual questions",
            "Exam mode vs Practice mode toggle",
            "Direct BKT mastery updating on every answer submitted",
          ]}
          actionLabel="View Focus timer"
          onAction={() => onNavigate("timer")}
        />
      );

    case "flashcards":
      return (
        <EmptyState
          phase={4}
          title="Flashcards"
          eyebrow="RETRIEVAL PRACTICE"
          description="A small review, at the right time, makes a topic easier to remember."
          previewFeatures={[
            "Automatic flashcard deck generator from uploaded notes",
            "SM-2 spaced repetition review queue",
            "Rating 1-5 with interval and ease factor progression",
          ]}
          actionLabel="View Progress"
          onAction={() => onNavigate("progress")}
        />
      );

    case "tutor":
      return (
        <EmptyState
          phase={5}
          title="AI tutor"
          eyebrow="STEP-BY-STEP GUIDANCE"
          description="Ask questions, explore complex proofs, and get step-by-step explanations."
          previewFeatures={[
            "Step-by-step Socratic reasoning explanations",
            "Citations and references to your uploaded study material",
            "Multi-provider LLM support (Anthropic, OpenAI, Ollama)",
          ]}
          actionLabel="View Revision planner"
          onAction={() => onNavigate("planner")}
        />
      );

    default:
      return null;
  }
};
