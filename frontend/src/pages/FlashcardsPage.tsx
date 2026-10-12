import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { FlashcardItem, Topic, Subject } from "@/types";
import {
  Layers,
  Sparkles,
  Plus,
  RotateCw,
  Download,
  Search,
  CheckCircle,
  HelpCircle,
  Clock,
  Sparkle,
  Trash2,
} from "lucide-react";
import { useToast } from "@/components/ui/Toast";

interface FlashcardsPageProps {
  onNavigate: (tab: any, params?: any) => void;
}

export const FlashcardsPage: React.FC<FlashcardsPageProps> = ({ onNavigate }) => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const [search, setSearch] = useState("");
  const [selectedTopicFilter, setSelectedTopicFilter] = useState<number | null>(null);
  const [isReviewMode, setIsReviewMode] = useState(false);
  const [isFlipped, setIsFlipped] = useState(false);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);

  // Deck generation state
  const [isGenerating, setIsGenerating] = useState(false);
  const [isCreatorOpen, setIsCreatorOpen] = useState(false);
  const [createFront, setCreateFront] = useState("");
  const [createBack, setCreateBack] = useState("");
  const [createTopicId, setCreateTopicId] = useState<number | null>(null);

  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);

  // Load cards
  const { data: cards, refetch: refetchCards } = useQuery({
    queryKey: ["flashcards", selectedTopicFilter, search],
    queryFn: () =>
      api.flashcards.list({
        topic_id: selectedTopicFilter || undefined,
        search: search || undefined,
      }),
  });

  // Load subjects & topics
  const { data: subjectsData } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => api.subjects.list({ page_size: 50 }),
  });
  const subjects = subjectsData?.items || [];
  const activeSubjectId = selectedSubjectId || (subjects.length > 0 ? subjects[0].id : null);

  const { data: topicsData } = useQuery({
    queryKey: ["topics", activeSubjectId],
    queryFn: () => (activeSubjectId ? api.topics.listForSubject(activeSubjectId) : null),
    enabled: !!activeSubjectId,
  });
  const topics = topicsData?.items || [];

  const dueCards = cards?.filter((c) => !c.due_date || new Date(c.due_date) <= new Date()) || [];
  const reviewDeck = dueCards.length > 0 ? dueCards : cards || [];
  const currentReviewCard = reviewDeck[currentCardIndex];

  // SM-2 Review rating handler
  const handleRateCard = async (rating: number) => {
    if (!currentReviewCard) return;
    try {
      await api.flashcards.review({
        flashcard_id: currentReviewCard.id,
        rating,
      });
      setIsFlipped(false);
      if (currentCardIndex < reviewDeck.length - 1) {
        setCurrentCardIndex((prev) => prev + 1);
      } else {
        setIsReviewMode(false);
        setCurrentCardIndex(0);
        showToast("Session complete! SuperMemo SM-2 schedule updated.", "success");
        refetchCards();
      }
    } catch (err: any) {
      showToast("Failed to record review", "error");
    }
  };

  const handleGenerateDeck = async () => {
    const topicId = selectedTopicFilter || topics[0]?.id;
    if (!topicId) {
      showToast("Please select a topic first", "error");
      return;
    }
    setIsGenerating(true);
    try {
      const res = await api.flashcards.generate({ topic_id: topicId, count: 6 });
      showToast(`Generated ${res.count} cards for spaced repetition!`, "success");
      refetchCards();
    } catch (err: any) {
      showToast(err?.error?.message || "Failed to generate flashcards", "error");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCreateCustomCard = async (e: React.FormEvent) => {
    e.preventDefault();
    const topicId = createTopicId || topics[0]?.id;
    if (!topicId || !createFront.trim() || !createBack.trim()) return;

    try {
      await api.flashcards.create({
        topic_id: topicId,
        front: createFront,
        back: createBack,
      });
      showToast("Flashcard created!", "success");
      setCreateFront("");
      setCreateBack("");
      setIsCreatorOpen(false);
      refetchCards();
    } catch (err) {
      showToast("Failed to create flashcard", "error");
    }
  };

  const handleDeleteCard = async (id: number) => {
    try {
      await api.flashcards.delete(id);
      showToast("Card removed", "success");
      refetchCards();
    } catch (err) {
      showToast("Failed to delete card", "error");
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-[#2F5D46] tracking-wider uppercase">
            Spaced Repetition (SuperMemo SM-2)
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1F2A24] tracking-tight mt-1 font-serif">
            Flashcards
          </h1>
          <p className="text-sm text-[#607166] mt-1">
            Optimized memory retention with SuperMemo SM-2 intervals that adapt to your recall confidence.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <a
            href={api.flashcards.getExportPdfUrl(selectedTopicFilter || undefined)}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border border-[#E3E8E2] text-xs font-medium text-[#607166] hover:bg-[#F4F6F1] transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Printable Deck</span>
          </a>

          <button
            onClick={() => setIsCreatorOpen(!isCreatorOpen)}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border border-[#E3E8E2] text-xs font-medium text-[#1F2A24] hover:bg-[#F4F6F1] transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Write Card</span>
          </button>

          <button
            onClick={handleGenerateDeck}
            disabled={isGenerating}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#2F5D46] text-white text-xs font-semibold hover:bg-[#254A37] transition-colors shadow-sm disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isGenerating ? "Generating..." : "Generate Deck"}</span>
          </button>
        </div>
      </div>

      {/* Write Custom Card Modal */}
      {isCreatorOpen && (
        <div className="p-6 bg-white rounded-2xl border border-[#2F5D46] shadow-md space-y-4 animate-fade-in">
          <div className="flex items-center justify-between border-b border-[#E3E8E2] pb-3">
            <h2 className="text-sm font-semibold text-[#1F2A24]">Create Custom Flashcard</h2>
            <button onClick={() => setIsCreatorOpen(false)} className="text-xs text-[#607166]">
              Cancel
            </button>
          </div>
          <form onSubmit={handleCreateCustomCard} className="space-y-3">
            <div>
              <label className="text-xs font-medium text-[#1F2A24] block mb-1">Topic</label>
              <select
                value={createTopicId || (topics[0]?.id || "")}
                onChange={(e) => setCreateTopicId(Number(e.target.value))}
                className="w-full text-xs px-3 py-2 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24]"
              >
                {topics.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-[#1F2A24] block mb-1">Front (Prompt)</label>
              <input
                type="text"
                value={createFront}
                onChange={(e) => setCreateFront(e.target.value)}
                placeholder="e.g. What is the primary function of the Golgi apparatus?"
                className="w-full text-xs px-3 py-2 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24]"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-[#1F2A24] block mb-1">Back (Target Concept)</label>
              <textarea
                value={createBack}
                onChange={(e) => setCreateBack(e.target.value)}
                rows={2}
                placeholder="e.g. Modifying, sorting, and packaging proteins for secretion."
                className="w-full text-xs p-3 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24]"
              />
            </div>
            <div className="flex justify-end gap-2">
              <button
                type="submit"
                className="px-4 py-2 bg-[#2F5D46] text-white rounded-xl text-xs font-medium"
              >
                Save Flashcard
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Review Mode Interactive Flip Card Runner */}
      {isReviewMode && currentReviewCard ? (
        <div className="max-w-xl mx-auto bg-white rounded-2xl border border-[#E3E8E2] p-8 space-y-6 shadow-sm animate-fade-in">
          <div className="flex items-center justify-between text-xs text-[#607166]">
            <span>
              Card {currentCardIndex + 1} of {reviewDeck.length}
            </span>
            <button
              onClick={() => setIsReviewMode(false)}
              className="text-[#607166] hover:text-[#1F2A24]"
            >
              Exit Review
            </button>
          </div>

          {/* 3D Flip Card Container */}
          <div
            onClick={() => setIsFlipped(!isFlipped)}
            className="min-h-[220px] p-6 rounded-2xl border-2 border-[#2F5D46]/20 bg-[#F4F6F1] flex flex-col items-center justify-center text-center cursor-pointer select-none transition-all hover:border-[#2F5D46]/40 shadow-inner"
          >
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#2F5D46] mb-3">
              {isFlipped ? "Answer" : "Question (Click to flip)"}
            </span>

            <p className="text-base sm:text-lg font-semibold text-[#1F2A24] leading-relaxed">
              {isFlipped ? currentReviewCard.back : currentReviewCard.front}
            </p>

            {isFlipped && currentReviewCard.explanation && (
              <p className="text-xs text-[#607166] mt-3 italic">
                {currentReviewCard.explanation}
              </p>
            )}
          </div>

          {/* SM-2 Rating Buttons */}
          {isFlipped ? (
            <div className="space-y-2">
              <span className="text-[11px] font-medium text-[#607166] block text-center">
                How well did you recall this concept?
              </span>
              <div className="grid grid-cols-4 gap-2">
                <button
                  onClick={() => handleRateCard(1)}
                  className="py-2.5 rounded-xl border border-rose-300 bg-rose-50 hover:bg-rose-100 text-rose-800 text-xs font-semibold transition-colors text-center"
                >
                  Again (1)
                  <span className="block text-[9px] font-normal text-rose-600">1 day</span>
                </button>
                <button
                  onClick={() => handleRateCard(2)}
                  className="py-2.5 rounded-xl border border-amber-300 bg-amber-50 hover:bg-amber-100 text-amber-800 text-xs font-semibold transition-colors text-center"
                >
                  Hard (2)
                  <span className="block text-[9px] font-normal text-amber-600">3 days</span>
                </button>
                <button
                  onClick={() => handleRateCard(3)}
                  className="py-2.5 rounded-xl border border-blue-300 bg-blue-50 hover:bg-blue-100 text-blue-800 text-xs font-semibold transition-colors text-center"
                >
                  Good (3)
                  <span className="block text-[9px] font-normal text-blue-600">6 days</span>
                </button>
                <button
                  onClick={() => handleRateCard(4)}
                  className="py-2.5 rounded-xl border border-emerald-300 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-semibold transition-colors text-center"
                >
                  Easy (4)
                  <span className="block text-[9px] font-normal text-emerald-600">14 days</span>
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setIsFlipped(true)}
              className="w-full py-3 rounded-xl bg-[#2F5D46] text-white text-xs font-semibold hover:bg-[#254A37] transition-colors"
            >
              Show Answer
            </button>
          )}
        </div>
      ) : (
        /* Deck Library View */
        <div className="space-y-6">
          {/* Deck Action Card */}
          <div className="p-6 bg-white rounded-2xl border border-[#E3E8E2] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="text-xs font-semibold text-[#2F5D46] uppercase">Today's Queue</span>
              <h2 className="text-lg font-bold text-[#1F2A24] mt-0.5 font-serif">
                {dueCards.length} Cards Due for Spaced Review
              </h2>
              <p className="text-xs text-[#607166] mt-1">
                Reviews scheduled to solidify neural memory traces before the forgetting curve steepens.
              </p>
            </div>

            <button
              onClick={() => {
                setIsReviewMode(true);
                setCurrentCardIndex(0);
                setIsFlipped(false);
              }}
              disabled={(cards?.length || 0) === 0}
              className="px-5 py-2.5 rounded-xl bg-[#2F5D46] text-white text-xs font-semibold hover:bg-[#254A37] disabled:opacity-50 transition-colors shadow-sm shrink-0"
            >
              Start Review Session
            </button>
          </div>

          {/* Cards Grid */}
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <h3 className="text-sm font-semibold text-[#1F2A24]">
                All Deck Cards ({cards?.length || 0})
              </h3>
              <div className="relative w-64">
                <Search className="w-3.5 h-3.5 text-[#8C9B90] absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Filter cards..."
                  className="w-full text-xs pl-8 pr-3 py-1.5 rounded-xl bg-white border border-[#E3E8E2] text-[#1F2A24] focus:outline-none focus:ring-1 focus:ring-[#2F5D46]"
                />
              </div>
            </div>

            {cards && cards.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {cards.map((c) => (
                  <div
                    key={c.id}
                    className="p-4 bg-white rounded-2xl border border-[#E3E8E2] flex flex-col justify-between space-y-3 hover:border-[#CBD5CD] transition-all"
                  >
                    <div>
                      <span className="text-[10px] font-semibold text-[#2F5D46] uppercase block mb-1">
                        {c.topic_name || "Topic"}
                      </span>
                      <p className="text-xs font-semibold text-[#1F2A24] leading-snug">
                        {c.front}
                      </p>
                      <hr className="my-2 border-[#F4F6F1]" />
                      <p className="text-xs text-[#4b5563] line-clamp-3">
                        {c.back}
                      </p>
                    </div>

                    <div className="pt-2 border-t border-[#F4F6F1] flex items-center justify-between text-[10px] text-[#8C9B90]">
                      <span>Interval: {c.interval_days}d</span>
                      <button
                        onClick={() => handleDeleteCard(c.id)}
                        className="text-[#8C9B90] hover:text-rose-600 transition-colors"
                        title="Delete card"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-12 text-center text-xs text-[#8C9B90] bg-white rounded-2xl border border-[#E3E8E2]">
                No flashcards in deck. Click "Generate Deck" or "Write Card" to begin.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
