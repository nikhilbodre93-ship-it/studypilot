import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { QuizItem, QuizAttemptResult, Subject, Topic } from "@/types";
import {
  HelpCircle,
  Sparkles,
  Timer,
  Mic,
  MicOff,
  CheckCircle,
  XCircle,
  ArrowRight,
  RotateCcw,
  Award,
  History,
} from "lucide-react";
import { useToast } from "@/components/ui/Toast";

interface QuizzesPageProps {
  onNavigate: (tab: any, params?: any) => void;
}

export const QuizzesPage: React.FC<QuizzesPageProps> = ({ onNavigate }) => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const [isBuilderOpen, setIsBuilderOpen] = useState(false);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);
  const [questionCount, setQuestionCount] = useState(5);
  const [difficulty, setDifficulty] = useState("medium");
  const [isExamMode, setIsExamMode] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(300); // 5 mins default
  const [activeQuiz, setActiveQuiz] = useState<QuizItem | null>(null);

  // Active quiz runner state
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState<QuizAttemptResult | null>(null);
  const [isListeningVoice, setIsListeningVoice] = useState(false);

  // Load subjects and topics
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

  // Load recent attempts
  const { data: attemptsHistory, refetch: refetchHistory } = useQuery({
    queryKey: ["quizzes", "history"],
    queryFn: () => api.quizzes.getHistory(),
  });

  // Countdown timer for Exam Mode
  useEffect(() => {
    let interval: any = null;
    if (activeQuiz && isExamMode && timerSeconds > 0 && !submissionResult) {
      interval = setInterval(() => {
        setTimerSeconds((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            handleSubmitQuiz();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [activeQuiz, isExamMode, timerSeconds, submissionResult]);

  // Voice speech-to-text handler using Web Speech API
  const handleToggleVoice = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      showToast("Web Speech API is not supported in this browser.", "error");
      return;
    }

    if (isListeningVoice) {
      setIsListeningVoice(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setIsListeningVoice(true);
        showToast("Listening... Speak your answer now.", "info");
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        const currentQ = activeQuiz?.questions?.[currentQuestionIndex];
        if (currentQ) {
          setAnswers((prev) => ({ ...prev, [currentQ.id]: transcript }));
        }
        setIsListeningVoice(false);
        showToast("Speech captured!", "success");
      };

      recognition.onerror = () => {
        setIsListeningVoice(false);
      };

      recognition.onend = () => {
        setIsListeningVoice(false);
      };

      recognition.start();
    } catch (e) {
      setIsListeningVoice(false);
    }
  };

  const handleGenerateQuiz = async (e: React.FormEvent) => {
    e.preventDefault();
    const topicIdToUse = selectedTopicId || topics[0]?.id;
    if (!topicIdToUse) {
      showToast("Please select a topic", "error");
      return;
    }

    setIsSubmitting(true);
    try {
      const quiz = await api.quizzes.generate({
        topic_id: topicIdToUse,
        count: questionCount,
        difficulty,
      });
      setActiveQuiz(quiz);
      setCurrentQuestionIndex(0);
      setAnswers({});
      setSubmissionResult(null);
      setIsBuilderOpen(false);
      if (isExamMode) setTimerSeconds(questionCount * 60);
      showToast("Quiz generated successfully!", "success");
    } catch (err: any) {
      showToast(err?.error?.message || "Failed to generate quiz", "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitQuiz = async () => {
    if (!activeQuiz || !activeQuiz.questions) return;
    setIsSubmitting(true);
    try {
      const formattedAnswers = activeQuiz.questions.map((q) => ({
        question_id: q.id,
        selected_answer: answers[q.id] || "",
      }));
      const res = await api.quizzes.submit(activeQuiz.id, formattedAnswers);
      setSubmissionResult(res);
      showToast(`Quiz completed! Score: ${res.score}/${res.max_score} (${res.percentage}%)`, "success");
      refetchHistory();
    } catch (err: any) {
      showToast(err?.error?.message || "Submission failed", "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentQuestion = activeQuiz?.questions?.[currentQuestionIndex];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-[#2F5D46] tracking-wider uppercase">
            Active Recall & Exam Simulation
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1F2A24] tracking-tight mt-1 font-serif">
            Practice Quizzes
          </h1>
          <p className="text-sm text-[#607166] mt-1">
            Generate grounded diagnostic quizzes that dynamically update Bayesian Knowledge Tracing topic mastery.
          </p>
        </div>

        <button
          onClick={() => {
            setIsBuilderOpen(true);
            setSubmissionResult(null);
            setActiveQuiz(null);
          }}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#2F5D46] text-white text-sm font-medium hover:bg-[#254A37] transition-colors shadow-sm"
        >
          <Sparkles className="w-4 h-4" />
          <span>New Practice Quiz</span>
        </button>
      </div>

      {/* Quiz Builder Modal / Drawer */}
      {isBuilderOpen && (
        <div className="p-6 bg-white rounded-2xl border border-[#2F5D46] shadow-md space-y-4 animate-fade-in">
          <div className="flex items-center justify-between border-b border-[#E3E8E2] pb-3">
            <h2 className="text-base font-semibold text-[#1F2A24] flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#2F5D46]" />
              <span>Build Practice Quiz</span>
            </h2>
            <button
              onClick={() => setIsBuilderOpen(false)}
              className="text-xs text-[#607166] hover:text-[#1F2A24]"
            >
              Cancel
            </button>
          </div>

          <form onSubmit={handleGenerateQuiz} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div>
                <label className="text-xs font-semibold text-[#1F2A24] block mb-1">
                  Subject
                </label>
                <select
                  value={activeSubjectId || ""}
                  onChange={(e) => {
                    setSelectedSubjectId(Number(e.target.value));
                    setSelectedTopicId(null);
                  }}
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
                <label className="text-xs font-semibold text-[#1F2A24] block mb-1">
                  Topic
                </label>
                <select
                  value={selectedTopicId || (topics[0]?.id || "")}
                  onChange={(e) => setSelectedTopicId(Number(e.target.value))}
                  className="w-full text-xs px-3 py-2 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24]"
                >
                  {topics.length === 0 ? (
                    <option value="">No topics found</option>
                  ) : (
                    topics.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name}
                      </option>
                    ))
                  )}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-[#1F2A24] block mb-1">
                  Questions
                </label>
                <select
                  value={questionCount}
                  onChange={(e) => setQuestionCount(Number(e.target.value))}
                  className="w-full text-xs px-3 py-2 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24]"
                >
                  <option value={3}>3 Questions (Quick)</option>
                  <option value={5}>5 Questions (Standard)</option>
                  <option value={10}>10 Questions (Comprehensive)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-[#1F2A24] block mb-1">
                  Format Mode
                </label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setIsExamMode(false)}
                    className={`flex-1 py-2 rounded-xl text-xs font-semibold border ${
                      !isExamMode
                        ? "bg-[#2F5D46] text-white border-[#2F5D46]"
                        : "bg-white text-[#607166] border-[#E3E8E2]"
                    }`}
                  >
                    Practice
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsExamMode(true)}
                    className={`flex-1 py-2 rounded-xl text-xs font-semibold border flex items-center justify-center gap-1 ${
                      isExamMode
                        ? "bg-amber-600 text-white border-amber-600"
                        : "bg-white text-[#607166] border-[#E3E8E2]"
                    }`}
                  >
                    <Timer className="w-3.5 h-3.5" />
                    <span>Exam</span>
                  </button>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="submit"
                disabled={isSubmitting}
                className="py-2.5 px-5 rounded-xl bg-[#2F5D46] text-white text-xs font-semibold hover:bg-[#254A37] transition-colors disabled:opacity-50 flex items-center gap-2 shadow-sm"
              >
                {isSubmitting ? "Generating Questions..." : "Generate Quiz"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Main Quiz Runner or Submission Results */}
      {submissionResult ? (
        /* Results View */
        <div className="bg-white rounded-2xl border border-[#E3E8E2] p-8 space-y-6 animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#E3E8E2]">
            <div>
              <span className="text-xs font-semibold text-[#2F5D46] uppercase">Assessment Complete</span>
              <h2 className="text-2xl font-bold text-[#1F2A24] font-serif mt-1">
                Your Quiz Results
              </h2>
              <p className="text-xs text-[#607166] mt-1">
                Bayesian Knowledge Tracing has updated your topic mastery score based on your responses.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-[#EBF2EC] text-center shrink-0">
              <span className="text-3xl font-extrabold text-[#2F5D46]">
                {submissionResult.percentage}%
              </span>
              <span className="text-xs text-[#607166] block font-medium">
                {submissionResult.score} / {submissionResult.max_score} Correct
              </span>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-[#1F2A24]">Detailed Answers & Explanations</h3>
            {submissionResult.results.map((res, i) => (
              <div
                key={res.question_id}
                className={`p-4 rounded-xl border ${
                  res.is_correct
                    ? "border-emerald-200 bg-emerald-50/40"
                    : "border-rose-200 bg-rose-50/40"
                }`}
              >
                <div className="flex items-start gap-3">
                  {res.is_correct ? (
                    <CheckCircle className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                  ) : (
                    <XCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
                  )}
                  <div className="space-y-1.5 flex-1">
                    <p className="text-xs font-semibold text-[#1F2A24]">
                      {i + 1}. {res.question_text}
                    </p>
                    <div className="text-xs text-[#607166]">
                      <span className="font-medium text-[#1F2A24]">Your Answer: </span>
                      {res.selected_answer || "(None)"}
                    </div>
                    {!res.is_correct && (
                      <div className="text-xs text-emerald-800">
                        <span className="font-medium">Correct Answer: </span>
                        {res.correct_answer}
                      </div>
                    )}
                    <p className="text-xs text-[#4b5563] pt-1 border-t border-black/5 italic">
                      💡 {res.explanation}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-[#E3E8E2]">
            <button
              onClick={() => onNavigate("learning")}
              className="px-4 py-2 rounded-xl border border-[#E3E8E2] text-xs font-medium text-[#607166] hover:bg-[#F4F6F1]"
            >
              View Topic Mastery
            </button>
            <button
              onClick={() => {
                setSubmissionResult(null);
                setActiveQuiz(null);
                setIsBuilderOpen(true);
              }}
              className="px-4 py-2 rounded-xl bg-[#2F5D46] text-white text-xs font-medium hover:bg-[#254A37]"
            >
              Take Another Quiz
            </button>
          </div>
        </div>
      ) : activeQuiz && currentQuestion ? (
        /* Active Quiz Player */
        <div className="bg-white rounded-2xl border border-[#E3E8E2] p-8 space-y-6">
          {/* Runner Header */}
          <div className="flex items-center justify-between pb-4 border-b border-[#E3E8E2]">
            <div>
              <span className="text-xs font-semibold text-[#2F5D46] uppercase">
                {activeQuiz.title}
              </span>
              <p className="text-xs text-[#607166] mt-0.5">
                Question {currentQuestionIndex + 1} of {activeQuiz.questions?.length}
              </p>
            </div>

            {isExamMode && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-50 text-amber-800 border border-amber-200 text-xs font-mono font-semibold">
                <Timer className="w-4 h-4 text-amber-600" />
                <span>
                  {Math.floor(timerSeconds / 60)}:{(timerSeconds % 60).toString().padStart(2, "0")}
                </span>
              </div>
            )}
          </div>

          {/* Question Text */}
          <div className="space-y-4">
            <h2 className="text-base sm:text-lg font-semibold text-[#1F2A24] leading-snug">
              {currentQuestion.question_text}
            </h2>

            {/* Multiple Choice Options */}
            {currentQuestion.question_type === "multiple_choice" && currentQuestion.options && (
              <div className="space-y-2.5">
                {currentQuestion.options.map((opt, i) => {
                  const isSelected = answers[currentQuestion.id] === opt;
                  return (
                    <button
                      key={i}
                      onClick={() => setAnswers((prev) => ({ ...prev, [currentQuestion.id]: opt }))}
                      className={`w-full p-3.5 rounded-xl text-xs font-medium text-left border transition-all flex items-center justify-between ${
                        isSelected
                          ? "bg-[#EBF2EC] border-[#2F5D46] text-[#2F5D46] font-semibold shadow-xs"
                          : "bg-white border-[#E3E8E2] text-[#1F2A24] hover:bg-[#F4F6F1]"
                      }`}
                    >
                      <span>{opt}</span>
                      <div
                        className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                          isSelected ? "border-[#2F5D46] bg-[#2F5D46]" : "border-[#8C9B90]"
                        }`}
                      >
                        {isSelected && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}

            {/* True / False Options */}
            {currentQuestion.question_type === "true_false" && (
              <div className="grid grid-cols-2 gap-4">
                {["True", "False"].map((opt) => {
                  const isSelected = answers[currentQuestion.id] === opt;
                  return (
                    <button
                      key={opt}
                      onClick={() => setAnswers((prev) => ({ ...prev, [currentQuestion.id]: opt }))}
                      className={`p-4 rounded-xl text-center text-sm font-semibold border transition-all ${
                        isSelected
                          ? "bg-[#2F5D46] text-white border-[#2F5D46] shadow-sm"
                          : "bg-white text-[#1F2A24] border-[#E3E8E2] hover:bg-[#F4F6F1]"
                      }`}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>
            )}

            {/* Short Answer Input with Speech Recognition */}
            {currentQuestion.question_type === "short_answer" && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-[#607166]">Your Response:</label>
                  <button
                    type="button"
                    onClick={handleToggleVoice}
                    className={`inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg border transition-colors ${
                      isListeningVoice
                        ? "bg-rose-100 text-rose-700 border-rose-300 animate-pulse"
                        : "bg-white text-[#2F5D46] border-[#E3E8E2] hover:bg-[#F4F6F1]"
                    }`}
                  >
                    {isListeningVoice ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
                    <span>{isListeningVoice ? "Stop Dictation" : "Dictate with Voice"}</span>
                  </button>
                </div>
                <textarea
                  value={answers[currentQuestion.id] || ""}
                  onChange={(e) => setAnswers((prev) => ({ ...prev, [currentQuestion.id]: e.target.value }))}
                  rows={3}
                  placeholder="Type your explanation or use voice dictation..."
                  className="w-full text-xs p-3 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24] focus:outline-none focus:ring-1 focus:ring-[#2F5D46]"
                />
              </div>
            )}
          </div>

          {/* Player Navigation Buttons */}
          <div className="flex items-center justify-between pt-4 border-t border-[#E3E8E2]">
            <button
              disabled={currentQuestionIndex === 0}
              onClick={() => setCurrentQuestionIndex((prev) => prev - 1)}
              className="px-4 py-2 rounded-xl border border-[#E3E8E2] text-xs font-medium text-[#607166] hover:bg-[#F4F6F1] disabled:opacity-40"
            >
              Previous
            </button>

            {currentQuestionIndex < (activeQuiz.questions?.length || 1) - 1 ? (
              <button
                onClick={() => setCurrentQuestionIndex((prev) => prev + 1)}
                className="px-4 py-2 rounded-xl bg-[#2F5D46] text-white text-xs font-medium hover:bg-[#254A37] flex items-center gap-1.5"
              >
                <span>Next Question</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            ) : (
              <button
                onClick={handleSubmitQuiz}
                disabled={isSubmitting}
                className="px-5 py-2.5 rounded-xl bg-[#2F5D46] text-white text-xs font-semibold hover:bg-[#254A37] shadow-sm disabled:opacity-50"
              >
                {isSubmitting ? "Evaluating..." : "Submit & Grade Quiz"}
              </button>
            )}
          </div>
        </div>
      ) : (
        /* Empty State / Previous Attempts History */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 p-8 bg-white rounded-2xl border border-[#E3E8E2] text-center space-y-4">
            <HelpCircle className="w-12 h-12 text-[#2F5D46] mx-auto opacity-70" />
            <div>
              <h2 className="text-base font-semibold text-[#1F2A24]">
                Ready to test your understanding?
              </h2>
              <p className="text-xs text-[#607166] mt-1 max-w-md mx-auto">
                Practice quizzes use active recall to diagnose gaps and adjust your personalized spaced repetition schedule.
              </p>
            </div>
            <button
              onClick={() => setIsBuilderOpen(true)}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2F5D46] text-white text-xs font-semibold hover:bg-[#254A37] transition-colors shadow-sm"
            >
              <Sparkles className="w-4 h-4" />
              <span>Configure Practice Quiz</span>
            </button>
          </div>

          {/* Recent Quiz Attempts Sidebar */}
          <div className="p-5 bg-white rounded-2xl border border-[#E3E8E2] space-y-3">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-[#2F5D46]" />
              <h3 className="text-xs font-semibold text-[#1F2A24] uppercase tracking-wider">
                Recent Attempts
              </h3>
            </div>

            {attemptsHistory && attemptsHistory.length > 0 ? (
              <div className="space-y-2">
                {attemptsHistory.slice(0, 5).map((att: any) => (
                  <div
                    key={att.id}
                    className="p-3 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-xs flex items-center justify-between"
                  >
                    <div>
                      <span className="font-semibold text-[#1F2A24] block line-clamp-1">
                        {att.quiz_title || "Quiz"}
                      </span>
                      <span className="text-[10px] text-[#8C9B90]">
                        {new Date(att.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <span className="font-bold text-[#2F5D46] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[11px]">
                      {att.percentage}%
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-[#8C9B90]">No attempts recorded yet.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
