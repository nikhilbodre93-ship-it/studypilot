import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { NoteItem, Topic, Subject } from "@/types";
import {
  FileText,
  Sparkles,
  Download,
  Search,
  Plus,
  Trash2,
  Share2,
  Layers,
  HelpCircle,
  Copy,
  BookOpen,
} from "lucide-react";
import { useToast } from "@/components/ui/Toast";

interface NotesPageProps {
  onNavigate: (tab: any, params?: any) => void;
}

export const NotesPage: React.FC<NotesPageProps> = ({ onNavigate }) => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const [search, setSearch] = useState("");
  const [selectedNoteId, setSelectedNoteId] = useState<number | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isBuilderOpen, setIsBuilderOpen] = useState(false);

  // Note builder form state
  const [builderSubjectId, setBuilderSubjectId] = useState<number | null>(null);
  const [targetTopicId, setTargetTopicId] = useState<number | null>(null);
  const [academicLevel, setAcademicLevel] = useState("Undergraduate / High School");
  const [customInstructions, setCustomInstructions] = useState("");

  // Load notes
  const { data: notes, isLoading: isLoadingNotes, refetch: refetchNotes } = useQuery({
    queryKey: ["notes", search],
    queryFn: () => api.notes.list({ search: search || undefined }),
  });

  // Load subjects & topics for builder dropdown
  const { data: subjectsData } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => api.subjects.list({ page_size: 50 }),
  });
  const subjects = subjectsData?.items || [];
  const activeSubjectId = builderSubjectId || (subjects.length > 0 ? subjects[0].id : null);

  const { data: topicsData } = useQuery({
    queryKey: ["topics", activeSubjectId],
    queryFn: () => (activeSubjectId ? api.topics.listForSubject(activeSubjectId) : null),
    enabled: !!activeSubjectId,
  });
  const topics = topicsData?.items || [];

  const activeNote = notes?.find((n) => n.id === selectedNoteId) || notes?.[0];

  const handleGenerateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    const topicIdToUse = targetTopicId || topics[0]?.id;
    if (!topicIdToUse) {
      showToast("Please select a topic first", "error");
      return;
    }

    setIsGenerating(true);
    try {
      const created = await api.notes.generate({
        topic_id: topicIdToUse,
        academic_level: academicLevel,
        custom_instructions: customInstructions || undefined,
      });
      showToast("Study note generated successfully!", "success");
      setIsBuilderOpen(false);
      refetchNotes();
      setSelectedNoteId(created.id);
    } catch (err: any) {
      showToast(err?.error?.message || "Failed to generate note", "error");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDeleteNote = async (id: number) => {
    if (!confirm("Are you sure you want to delete this note?")) return;
    try {
      await api.notes.delete(id);
      showToast("Note deleted", "success");
      refetchNotes();
      if (selectedNoteId === id) setSelectedNoteId(null);
    } catch (err) {
      showToast("Failed to delete note", "error");
    }
  };

  const handleCopyMarkdown = () => {
    if (activeNote) {
      navigator.clipboard.writeText(activeNote.content_markdown);
      showToast("Markdown copied to clipboard!", "success");
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-[#2F5D46] tracking-wider uppercase">
            AI Synthesis & Library
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1F2A24] tracking-tight mt-1 font-serif">
            Study Notes
          </h1>
          <p className="text-sm text-[#607166] mt-1">
            Grounded notes generated from your materials, formatted with high-yield takeaways and citations.
          </p>
        </div>

        <button
          onClick={() => setIsBuilderOpen(!isBuilderOpen)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#2F5D46] text-white text-sm font-medium hover:bg-[#254A37] transition-colors shadow-sm"
        >
          <Sparkles className="w-4 h-4" />
          <span>Generate New Note</span>
        </button>
      </div>

      {/* Note Builder Collapsible Panel */}
      {isBuilderOpen && (
        <div className="p-6 bg-white rounded-2xl border border-[#2F5D46] shadow-md space-y-4 animate-fade-in">
          <div className="flex items-center justify-between border-b border-[#E3E8E2] pb-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-[#2F5D46]" />
              <h2 className="text-base font-semibold text-[#1F2A24]">AI Note Builder</h2>
            </div>
            <button
              onClick={() => setIsBuilderOpen(false)}
              className="text-xs text-[#607166] hover:text-[#1F2A24]"
            >
              Cancel
            </button>
          </div>

          <form onSubmit={handleGenerateNote} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="text-xs font-semibold text-[#1F2A24] block mb-1">
                  Select Subject
                </label>
                <select
                  value={activeSubjectId || ""}
                  onChange={(e) => {
                    setBuilderSubjectId(Number(e.target.value));
                    setTargetTopicId(null);
                  }}
                  className="w-full text-xs px-3 py-2 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24] focus:outline-none focus:ring-1 focus:ring-[#2F5D46]"
                >
                  {subjects.length === 0 ? (
                    <option value="">No subjects created</option>
                  ) : (
                    subjects.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))
                  )}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-[#1F2A24] block mb-1">
                  Select Topic
                </label>
                <select
                  value={targetTopicId || (topics[0]?.id || "")}
                  onChange={(e) => setTargetTopicId(Number(e.target.value))}
                  className="w-full text-xs px-3 py-2 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24] focus:outline-none focus:ring-1 focus:ring-[#2F5D46]"
                >
                  {topics.length === 0 ? (
                    <option value="">No topics in this subject</option>
                  ) : (
                    topics.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name} ({t.difficulty})
                      </option>
                    ))
                  )}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-[#1F2A24] block mb-1">
                  Academic Depth
                </label>
                <select
                  value={academicLevel}
                  onChange={(e) => setAcademicLevel(e.target.value)}
                  className="w-full text-xs px-3 py-2 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24] focus:outline-none focus:ring-1 focus:ring-[#2F5D46]"
                >
                  <option value="High School / GCSE / A-Level">High School / A-Level</option>
                  <option value="Undergraduate / High School">Undergraduate</option>
                  <option value="Postgraduate / Advanced Research">Postgraduate / Exam Rigor</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-[#1F2A24] block mb-1">
                Custom Focus or Pasted Text (Optional)
              </label>
              <textarea
                value={customInstructions}
                onChange={(e) => setCustomInstructions(e.target.value)}
                rows={2}
                placeholder="e.g. Emphasize active transport mechanisms, ion channel kinetics, and clinical pharmacology applications."
                className="w-full text-xs p-3 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24] focus:outline-none focus:ring-1 focus:ring-[#2F5D46]"
              />
            </div>

            <div className="flex justify-end gap-2">
              <button
                type="submit"
                disabled={isGenerating}
                className="py-2.5 px-5 rounded-xl bg-[#2F5D46] text-white text-xs font-semibold hover:bg-[#254A37] transition-colors disabled:opacity-50 flex items-center gap-2 shadow-sm"
              >
                {isGenerating ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Synthesizing Grounded Notes...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Generate Structured Notes</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Main Layout: Notes List Sidebar & Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Notes Library List (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-2xl border border-[#E3E8E2] p-4 space-y-3">
          <div className="relative">
            <Search className="w-4 h-4 text-[#8C9B90] absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search notes..."
              className="w-full text-xs pl-9 pr-3 py-2 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24] placeholder-[#8C9B90] focus:outline-none focus:ring-1 focus:ring-[#2F5D46]"
            />
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {notes && notes.length > 0 ? (
              notes.map((note) => {
                const isSelected = activeNote?.id === note.id;
                return (
                  <div
                    key={note.id}
                    onClick={() => setSelectedNoteId(note.id)}
                    className={`p-3 rounded-xl border text-left cursor-pointer transition-all ${
                      isSelected
                        ? "bg-[#EBF2EC] border-[#2F5D46] shadow-xs"
                        : "bg-white border-[#E3E8E2] hover:bg-[#F4F6F1]"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-semibold text-[#1F2A24] line-clamp-1">
                        {note.title}
                      </span>
                      {note.is_ai_generated && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-medium shrink-0">
                          AI
                        </span>
                      )}
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-[#607166] mt-1">
                      <span>{note.topic_name || "Topic"}</span>
                      <span>{new Date(note.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="p-8 text-center text-xs text-[#8C9B90]">
                No notes found. Click "Generate New Note" above.
              </div>
            )}
          </div>
        </div>

        {/* Right: Markdown Reader & Quick Actions (8 cols) */}
        <div className="lg:col-span-8 bg-white rounded-2xl border border-[#E3E8E2] p-6 space-y-6">
          {activeNote ? (
            <>
              {/* Header and Action Bar */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E3E8E2]">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-semibold text-[#2F5D46] uppercase">
                      {activeNote.subject_name || "StudyPilot Note"}
                    </span>
                    <span className="text-xs text-[#8C9B90]">•</span>
                    <span className="text-xs text-[#607166]">{activeNote.topic_name}</span>
                  </div>
                  <h2 className="text-xl font-bold text-[#1F2A24] mt-0.5 font-serif">
                    {activeNote.title}
                  </h2>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={handleCopyMarkdown}
                    className="p-2 rounded-xl border border-[#E3E8E2] hover:bg-[#F4F6F1] text-[#607166] transition-colors"
                    title="Copy Markdown"
                  >
                    <Copy className="w-4 h-4" />
                  </button>

                  <a
                    href={api.notes.getExportUrl(activeNote.id, "md")}
                    download
                    className="p-2 rounded-xl border border-[#E3E8E2] hover:bg-[#F4F6F1] text-[#607166] transition-colors"
                    title="Export Markdown"
                  >
                    <Download className="w-4 h-4" />
                  </a>

                  <button
                    onClick={() => handleDeleteNote(activeNote.id)}
                    className="p-2 rounded-xl border border-rose-200 hover:bg-rose-50 text-rose-600 transition-colors"
                    title="Delete Note"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Note Markdown Content Body */}
              <div className="prose prose-sm max-w-none text-[#1F2A24] space-y-4 leading-relaxed font-sans">
                <div className="whitespace-pre-wrap font-sans text-sm text-[#1F2A24] leading-relaxed">
                  {activeNote.content_markdown}
                </div>
              </div>

              {/* Connected Workflows Ribbon */}
              <div className="pt-6 border-t border-[#E3E8E2] flex flex-wrap items-center justify-between gap-4 bg-[#F4F6F1] p-4 rounded-xl">
                <div>
                  <span className="text-xs font-semibold text-[#1F2A24] block">
                    Turn this note into active practice
                  </span>
                  <span className="text-[11px] text-[#607166]">
                    Reinforce your memory with spaced repetition or an exam quiz.
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onNavigate("flashcards")}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-[#E3E8E2] text-xs font-medium text-[#2F5D46] hover:bg-[#EBF2EC] transition-colors shadow-xs"
                  >
                    <Layers className="w-3.5 h-3.5" />
                    <span>Make Flashcards</span>
                  </button>

                  <button
                    onClick={() => onNavigate("quizzes")}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#2F5D46] text-white text-xs font-medium hover:bg-[#254A37] transition-colors shadow-xs"
                  >
                    <HelpCircle className="w-3.5 h-3.5" />
                    <span>Create Quiz</span>
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="p-12 text-center text-[#8C9B90] space-y-2">
              <BookOpen className="w-10 h-10 mx-auto text-[#8C9B90]" />
              <p className="text-sm font-medium text-[#1F2A24]">Select or generate a note</p>
              <p className="text-xs">Your structured revision notes will render here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
