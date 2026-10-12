import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Subject, Topic, MaterialItem } from "@/types";
import {
  BookOpen,
  Plus,
  Upload,
  FileText,
  HelpCircle,
  Layers,
  GraduationCap,
  Trash2,
  CheckCircle,
  Clock,
  Sparkles,
  Search,
} from "lucide-react";
import { useToast } from "@/components/ui/Toast";

interface MyLearningPageProps {
  onNavigate: (tab: any, params?: any) => void;
}

export const MyLearningPage: React.FC<MyLearningPageProps> = ({ onNavigate }) => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);
  const [uploadTopicId, setUploadTopicId] = useState<number | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  // Load subjects
  const { data: subjectsData, isLoading: isLoadingSubjects } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => api.subjects.list({ page_size: 50 }),
  });

  const subjects = subjectsData?.items || [];
  const currentSubject = subjects.find((s) => s.id === selectedSubjectId) || subjects[0];

  // Load topics for selected subject
  const { data: topicsData, isLoading: isLoadingTopics } = useQuery({
    queryKey: ["topics", currentSubject?.id],
    queryFn: () => (currentSubject ? api.topics.listForSubject(currentSubject.id) : null),
    enabled: !!currentSubject,
  });

  const topics = topicsData?.items || [];

  // Load materials for topic if selected
  const { data: materialsData, refetch: refetchMaterials } = useQuery({
    queryKey: ["materials", selectedTopicId],
    queryFn: () => (selectedTopicId ? api.materials.listForTopic(selectedTopicId) : []),
    enabled: !!selectedTopicId,
  });

  // Material upload handler
  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !uploadTopicId) return;

    const ext = uploadFile.name.split(".").pop()?.toLowerCase();
    if (!["pdf", "txt", "md"].includes(ext || "")) {
      showToast("Please upload a .pdf, .txt, or .md file", "error");
      return;
    }

    const formData = new FormData();
    formData.append("topic_id", uploadTopicId.toString());
    formData.append("file", uploadFile);

    setIsUploading(true);
    try {
      await api.materials.upload(formData);
      showToast("Material uploaded & processed for RAG grounding!", "success");
      setUploadFile(null);
      setUploadTopicId(null);
      if (selectedTopicId) refetchMaterials();
    } catch (err: any) {
      showToast(err?.error?.message || "Failed to upload file", "error");
    } finally {
      setIsUploading(false);
    }
  };

  const getDifficultyBadge = (diff: string) => {
    switch (diff) {
      case "easy":
        return <span className="px-2 py-0.5 text-[11px] rounded-full bg-emerald-50 text-emerald-700 font-medium border border-emerald-200">Easy</span>;
      case "hard":
        return <span className="px-2 py-0.5 text-[11px] rounded-full bg-rose-50 text-rose-700 font-medium border border-rose-200">Hard</span>;
      default:
        return <span className="px-2 py-0.5 text-[11px] rounded-full bg-amber-50 text-amber-700 font-medium border border-amber-200">Medium</span>;
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-[#2F5D46] tracking-wider uppercase">
            Curriculum & Knowledge Base
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1F2A24] tracking-tight mt-1 font-serif">
            My Learning
          </h1>
          <p className="text-sm text-[#607166] mt-1">
            Manage your courses, study materials, and launch instant revision workflows.
          </p>
        </div>

        <button
          onClick={() => onNavigate("learning")}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#2F5D46] text-white text-sm font-medium hover:bg-[#254A37] transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>Edit Syllabus</span>
        </button>
      </div>

      {/* Subject Navigation Tabs */}
      {subjects.length > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-[#E3E8E2]">
          {subjects.map((s) => {
            const isSelected = (currentSubject?.id === s.id);
            return (
              <button
                key={s.id}
                onClick={() => {
                  setSelectedSubjectId(s.id);
                  setSelectedTopicId(null);
                }}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
                  isSelected
                    ? "bg-[#2F5D46] text-white shadow-sm"
                    : "bg-white text-[#607166] hover:bg-[#ECEFE8] hover:text-[#1F2A24] border border-[#E3E8E2]"
                }`}
              >
                <div
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: isSelected ? "#fff" : s.color }}
                />
                <span>{s.name}</span>
                {s.exam_date && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${isSelected ? "bg-white/20 text-white" : "bg-[#F4F6F1] text-[#607166]"}`}>
                    Exam {new Date(s.exam_date).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Topics List & Quick Actions (2 columns) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-[#1F2A24]">
              {currentSubject?.name || "Subject"} Topics ({topics.length})
            </h2>
            <button
              onClick={() => onNavigate("quizzes")}
              className="text-xs text-[#2F5D46] font-medium hover:underline flex items-center gap-1"
            >
              <span>View full exam practice</span>
            </button>
          </div>

          {topics.length === 0 ? (
            <div className="p-8 bg-white rounded-2xl border border-[#E3E8E2] text-center">
              <BookOpen className="w-10 h-10 text-[#8C9B90] mx-auto mb-3" />
              <p className="text-sm font-medium text-[#1F2A24]">No topics in this subject yet</p>
              <p className="text-xs text-[#607166] mt-1">Configure your syllabus to start generating materials.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {topics.map((t) => {
                const masteryPct = Math.round((t.mastery_score || 0) * 100);
                const isSelected = selectedTopicId === t.id;
                return (
                  <div
                    key={t.id}
                    onClick={() => setSelectedTopicId(t.id)}
                    className={`p-4 bg-white rounded-2xl border transition-all cursor-pointer ${
                      isSelected
                        ? "border-[#2F5D46] ring-1 ring-[#2F5D46] shadow-sm"
                        : "border-[#E3E8E2] hover:border-[#CBD5CD]"
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-semibold text-[#1F2A24]">{t.name}</h3>
                          {getDifficultyBadge(t.difficulty)}
                        </div>
                        {t.description && (
                          <p className="text-xs text-[#607166] mt-1 line-clamp-1">{t.description}</p>
                        )}
                      </div>

                      {/* Mastery Pill */}
                      <div className="flex items-center gap-3 shrink-0">
                        <div className="text-right">
                          <span className="text-xs font-semibold text-[#1F2A24]">{masteryPct}%</span>
                          <span className="text-[10px] text-[#8C9B90] block">Mastery</span>
                        </div>
                        <div className="w-16 h-2 rounded-full bg-[#EBF2EC] overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-500 bg-[#2F5D46]"
                            style={{ width: `${masteryPct}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Quick Action Ribbon */}
                    <div className="mt-3 pt-3 border-t border-[#F4F6F1] flex flex-wrap items-center gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onNavigate("notes");
                        }}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#F4F6F1] hover:bg-[#EBF2EC] text-[#2F5D46] text-xs font-medium transition-colors"
                      >
                        <FileText className="w-3.5 h-3.5" />
                        <span>Notes</span>
                      </button>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onNavigate("quizzes");
                        }}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#F4F6F1] hover:bg-[#EBF2EC] text-[#2F5D46] text-xs font-medium transition-colors"
                      >
                        <HelpCircle className="w-3.5 h-3.5" />
                        <span>Quiz</span>
                      </button>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onNavigate("flashcards");
                        }}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#F4F6F1] hover:bg-[#EBF2EC] text-[#2F5D46] text-xs font-medium transition-colors"
                      >
                        <Layers className="w-3.5 h-3.5" />
                        <span>Cards</span>
                      </button>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setUploadTopicId(t.id);
                        }}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-medium transition-colors ml-auto"
                      >
                        <Upload className="w-3.5 h-3.5" />
                        <span>Upload PDF/TXT</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Column: Ingestion & Knowledge Materials */}
        <div className="space-y-4">
          <div className="p-5 bg-white rounded-2xl border border-[#E3E8E2] space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#2F5D46]" />
              <h2 className="text-sm font-semibold text-[#1F2A24]">
                RAG Knowledge Ingestion
              </h2>
            </div>
            <p className="text-xs text-[#607166] leading-relaxed">
              Upload course PDFs, lecture transcripts, or notes. StudyPilot extracts text via PyMuPDF, chunks it with overlap, and grounds all AI generations with citations.
            </p>

            {/* Direct Upload Form */}
            <form onSubmit={handleUploadSubmit} className="space-y-3 pt-2">
              <div>
                <label className="text-xs font-medium text-[#1F2A24] block mb-1">
                  Assign to Topic
                </label>
                <select
                  value={uploadTopicId || selectedTopicId || (topics[0]?.id || "")}
                  onChange={(e) => setUploadTopicId(Number(e.target.value))}
                  className="w-full text-xs px-3 py-2 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24] focus:outline-none focus:ring-1 focus:ring-[#2F5D46]"
                >
                  {topics.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="border-2 border-dashed border-[#D7DEC5] rounded-xl p-4 text-center hover:bg-[#F4F6F1] transition-colors cursor-pointer">
                <input
                  type="file"
                  id="material-file"
                  accept=".pdf,.txt,.md"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="hidden"
                />
                <label htmlFor="material-file" className="cursor-pointer">
                  <Upload className="w-6 h-6 text-[#2F5D46] mx-auto mb-1" />
                  <span className="text-xs font-medium text-[#1F2A24] block">
                    {uploadFile ? uploadFile.name : "Choose PDF, TXT or Markdown"}
                  </span>
                  <span className="text-[10px] text-[#8C9B90]">Up to 25MB</span>
                </label>
              </div>

              <button
                type="submit"
                disabled={!uploadFile || isUploading}
                className="w-full py-2 px-3 rounded-xl bg-[#2F5D46] text-white text-xs font-medium hover:bg-[#254A37] transition-colors disabled:opacity-50 flex items-center justify-center gap-1.5 shadow-sm"
              >
                {isUploading ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Extracting & Indexing...</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-3.5 h-3.5" />
                    <span>Upload & Ground Material</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* List of uploaded materials for topic */}
          {selectedTopicId && (
            <div className="p-5 bg-white rounded-2xl border border-[#E3E8E2] space-y-3">
              <h3 className="text-xs font-semibold text-[#1F2A24] uppercase tracking-wider">
                Grounded Documents
              </h3>

              {materialsData && materialsData.length > 0 ? (
                <div className="space-y-2">
                  {materialsData.map((m: MaterialItem) => (
                    <div
                      key={m.id}
                      className="flex items-center justify-between p-2.5 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-xs"
                    >
                      <div className="flex items-center gap-2 truncate">
                        <FileText className="w-4 h-4 text-[#2F5D46] shrink-0" />
                        <span className="font-medium text-[#1F2A24] truncate">{m.title}</span>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold shrink-0">
                        Indexed
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-[#607166]">No files uploaded for this topic yet.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
