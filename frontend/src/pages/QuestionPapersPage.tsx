import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { QuestionPaperItem, Subject } from "@/types";
import {
  GraduationCap,
  Sparkles,
  Download,
  Timer,
  CheckCircle,
  Clock,
  ArrowRight,
  FileCheck,
} from "lucide-react";
import { useToast } from "@/components/ui/Toast";

interface QuestionPapersPageProps {
  onNavigate: (tab: any, params?: any) => void;
}

export const QuestionPapersPage: React.FC<QuestionPapersPageProps> = ({ onNavigate }) => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [durationMinutes, setDurationMinutes] = useState(60);
  const [totalMarks, setTotalMarks] = useState(100);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isAttempting, setIsAttempting] = useState(false);
  const [activePaper, setActivePaper] = useState<QuestionPaperItem | null>(null);

  // Attempt runner state
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [timerSeconds, setTimerSeconds] = useState(3600);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState<any | null>(null);

  // Load subjects
  const { data: subjectsData } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => api.subjects.list({ page_size: 50 }),
  });
  const subjects = subjectsData?.items || [];

  // Load existing papers
  const { data: papers, refetch: refetchPapers } = useQuery({
    queryKey: ["question-papers", selectedSubjectId],
    queryFn: () => api.questionPapers.list(selectedSubjectId || undefined),
  });

  // Countdown timer during attempt
  useEffect(() => {
    let interval: any = null;
    if (isAttempting && timerSeconds > 0 && !evaluationResult) {
      interval = setInterval(() => {
        setTimerSeconds((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            handleEvaluatePaper();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isAttempting, timerSeconds, evaluationResult]);

  const handleGeneratePaper = async (e: React.FormEvent) => {
    e.preventDefault();
    const subjId = selectedSubjectId || subjects[0]?.id;
    if (!subjId) {
      showToast("Please select a subject", "error");
      return;
    }

    setIsGenerating(true);
    try {
      const paper = await api.questionPapers.generate({
        subject_id: subjId,
        duration_minutes: durationMinutes,
        total_marks: totalMarks,
      });
      showToast("Exam paper generated with Section A, B, C breakdown!", "success");
      setActivePaper(paper);
      setTimerSeconds(paper.duration_minutes * 60);
      setAnswers({});
      setEvaluationResult(null);
      refetchPapers();
    } catch (err: any) {
      showToast(err?.error?.message || "Failed to generate question paper", "error");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleEvaluatePaper = async () => {
    if (!activePaper) return;
    setIsEvaluating(true);
    try {
      const res = await api.questionPapers.evaluate(activePaper.id, answers);
      setEvaluationResult(res);
      showToast(`Evaluation completed! Awarded: ${res.total_marks_awarded} / ${res.total_max_marks} marks`, "success");
    } catch (err: any) {
      showToast(err?.error?.message || "Failed to evaluate exam paper", "error");
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-[#2F5D46] tracking-wider uppercase">
            Rigorous Mock Examination
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1F2A24] tracking-tight mt-1 font-serif">
            Question Papers
          </h1>
          <p className="text-sm text-[#607166] mt-1">
            Standard examination papers with Sections A/B/C, marking criteria, and automated rubric evaluation.
          </p>
        </div>

        {activePaper && !isAttempting && !evaluationResult && (
          <div className="flex items-center gap-2">
            <a
              href={api.questionPapers.getExportPdfUrl(activePaper.id)}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border border-[#E3E8E2] text-xs font-medium text-[#607166] hover:bg-[#F4F6F1]"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download PDF Paper</span>
            </a>
            <button
              onClick={() => {
                setIsAttempting(true);
                setTimerSeconds(activePaper.duration_minutes * 60);
              }}
              className="px-4 py-2 rounded-xl bg-[#2F5D46] text-white text-xs font-semibold hover:bg-[#254A37]"
            >
              Start Timed Attempt
            </button>
          </div>
        )}
      </div>

      {/* Generator Configuration Card */}
      {!activePaper && (
        <div className="p-6 bg-white rounded-2xl border border-[#E3E8E2] space-y-4">
          <h2 className="text-sm font-semibold text-[#1F2A24] flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#2F5D46]" />
            <span>Generate Authentic Mock Exam Paper</span>
          </h2>

          <form onSubmit={handleGeneratePaper} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
            <div>
              <label className="text-xs font-medium text-[#1F2A24] block mb-1">Subject</label>
              <select
                value={selectedSubjectId || (subjects[0]?.id || "")}
                onChange={(e) => setSelectedSubjectId(Number(e.target.value))}
                className="w-full text-xs px-3 py-2 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24]"
              >
                {subjects.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs font-medium text-[#1F2A24] block mb-1">Duration</label>
              <select
                value={durationMinutes}
                onChange={(e) => setDurationMinutes(Number(e.target.value))}
                className="w-full text-xs px-3 py-2 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24]"
              >
                <option value={30}>30 Minutes</option>
                <option value={60}>60 Minutes (Standard)</option>
                <option value={90}>90 Minutes</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-medium text-[#1F2A24] block mb-1">Total Marks</label>
              <select
                value={totalMarks}
                onChange={(e) => setTotalMarks(Number(e.target.value))}
                className="w-full text-xs px-3 py-2 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24]"
              >
                <option value={50}>50 Marks</option>
                <option value={100}>100 Marks</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={isGenerating}
              className="py-2.5 px-4 rounded-xl bg-[#2F5D46] text-white text-xs font-semibold hover:bg-[#254A37] disabled:opacity-50 transition-colors shadow-sm"
            >
              {isGenerating ? "Synthesizing Exam Paper..." : "Generate Paper"}
            </button>
          </form>
        </div>
      )}

      {/* Active Paper Evaluation Results */}
      {evaluationResult && (
        <div className="bg-white rounded-2xl border border-[#E3E8E2] p-8 space-y-6 animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E3E8E2]">
            <div>
              <span className="text-xs font-semibold text-[#2F5D46] uppercase">Evaluation Report</span>
              <h2 className="text-xl font-bold text-[#1F2A24] font-serif mt-1">
                Examination Assessment
              </h2>
              <p className="text-xs text-[#607166] mt-1">{evaluationResult.summary_feedback}</p>
            </div>
            <div className="p-4 rounded-xl bg-[#EBF2EC] text-center shrink-0">
              <span className="text-3xl font-extrabold text-[#2F5D46]">
                {evaluationResult.percentage}%
              </span>
              <span className="text-xs text-[#607166] block font-medium">
                {evaluationResult.total_marks_awarded} / {evaluationResult.total_max_marks} Marks
              </span>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-[#1F2A24]">Question Breakdown & Rubric Feedback</h3>
            {evaluationResult.question_evaluations?.map((ev: any) => (
              <div key={ev.question_id} className="p-4 rounded-xl border border-[#E3E8E2] bg-[#F4F6F1] space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#1F2A24]">{ev.question_id}</span>
                  <span className="text-xs font-semibold text-[#2F5D46] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                    {ev.marks_awarded} / {ev.max_marks} Marks
                  </span>
                </div>
                <p className="text-xs text-[#1F2A24]">{ev.feedback}</p>
                {ev.key_missed_concepts && ev.key_missed_concepts.length > 0 && (
                  <div className="text-[11px] text-amber-700">
                    Missed keywords: {ev.key_missed_concepts.join(", ")}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="flex justify-end pt-4 border-t border-[#E3E8E2]">
            <button
              onClick={() => {
                setActivePaper(null);
                setEvaluationResult(null);
                setIsAttempting(false);
              }}
              className="px-4 py-2 bg-[#2F5D46] text-white rounded-xl text-xs font-medium"
            >
              Done & Return to Exam Papers
            </button>
          </div>
        </div>
      )}

      {/* Active Paper View or Timed Attempt Mode */}
      {activePaper && !evaluationResult && (
        <div className="bg-white rounded-2xl border border-[#E3E8E2] p-8 space-y-6 shadow-sm">
          {/* Exam Header */}
          <div className="text-center pb-6 border-b-2 border-double border-[#2F5D46] space-y-1">
            <h2 className="text-2xl font-bold text-[#1F2A24] font-serif">{activePaper.title}</h2>
            <p className="text-xs text-[#607166]">
              Maximum Marks: {activePaper.total_marks} &nbsp;|&nbsp; Duration: {activePaper.duration_minutes} Minutes
            </p>

            {isAttempting && (
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-xs font-mono font-bold mt-2">
                <Timer className="w-4 h-4 text-amber-600" />
                <span>
                  Time Remaining: {Math.floor(timerSeconds / 60)}:{(timerSeconds % 60).toString().padStart(2, "0")}
                </span>
              </div>
            )}
          </div>

          {/* Sections and Questions */}
          <div className="space-y-8">
            {activePaper.content?.sections?.map((sec) => (
              <div key={sec.section_code} className="space-y-4">
                <div className="pb-2 border-b border-[#2F5D46]">
                  <h3 className="text-base font-bold text-[#2F5D46]">{sec.name}</h3>
                  <p className="text-xs text-[#607166] italic">{sec.description} (Total: {sec.total_marks} Marks)</p>
                </div>

                <div className="space-y-6">
                  {sec.questions.map((q) => (
                    <div key={q.id} className="space-y-2 p-4 rounded-xl bg-[#F4F6F1]/50 border border-[#E3E8E2]">
                      <div className="flex items-start justify-between gap-4">
                        <p className="text-xs font-semibold text-[#1F2A24] leading-relaxed">
                          <strong>{q.id}.</strong> {q.question_text}
                        </p>
                        <span className="text-xs font-bold text-[#2F5D46] shrink-0">
                          [{q.marks} Marks]
                        </span>
                      </div>

                      {q.options && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                          {q.options.map((opt, oi) => (
                            <div key={oi} className="text-xs p-2 rounded-lg bg-white border border-[#E3E8E2]">
                              {String.fromCharCode(65 + oi)}. {opt}
                            </div>
                          ))}
                        </div>
                      )}

                      {isAttempting && (
                        <div className="pt-2">
                          <label className="text-[11px] font-medium text-[#607166] block mb-1">Your Answer:</label>
                          <textarea
                            value={answers[q.id] || ""}
                            onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
                            rows={q.marks > 4 ? 3 : 1}
                            placeholder="Type student response here..."
                            className="w-full text-xs p-2.5 rounded-lg bg-white border border-[#E3E8E2] text-[#1F2A24] focus:outline-none focus:ring-1 focus:ring-[#2F5D46]"
                          />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Submission in Attempt Mode */}
          {isAttempting && (
            <div className="flex justify-end pt-6 border-t border-[#E3E8E2]">
              <button
                onClick={handleEvaluatePaper}
                disabled={isEvaluating}
                className="px-6 py-3 rounded-xl bg-[#2F5D46] text-white text-xs font-semibold hover:bg-[#254A37] shadow-sm disabled:opacity-50"
              >
                {isEvaluating ? "Grading Paper with AI..." : "Submit Paper for AI Evaluation"}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Papers Library Grid */}
      {!activePaper && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-[#1F2A24]">Saved Question Papers ({papers?.length || 0})</h3>
          {papers && papers.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {papers.map((p) => (
                <div
                  key={p.id}
                  onClick={() => {
                    setActivePaper(p);
                    setEvaluationResult(null);
                    setIsAttempting(false);
                  }}
                  className="p-5 bg-white rounded-2xl border border-[#E3E8E2] hover:border-[#2F5D46] transition-all cursor-pointer space-y-3"
                >
                  <span className="text-[10px] font-semibold text-[#2F5D46] uppercase block">
                    {p.subject_name || "Subject"}
                  </span>
                  <h4 className="text-sm font-semibold text-[#1F2A24] line-clamp-1">{p.title}</h4>
                  <div className="flex items-center justify-between text-xs text-[#607166] pt-2 border-t border-[#F4F6F1]">
                    <span>{p.total_marks} Marks</span>
                    <span>{p.duration_minutes} Mins</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[#8C9B90]">No saved papers yet. Configure one above.</p>
          )}
        </div>
      )}
    </div>
  );
};
