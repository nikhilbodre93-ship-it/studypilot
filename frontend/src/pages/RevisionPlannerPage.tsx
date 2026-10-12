import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Card } from "@/components/ui/Card";
import { Eyebrow } from "@/components/ui/Eyebrow";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { Play, Sparkles, CheckCircle, ArrowRight } from "lucide-react";
import { NavItem } from "@/components/layout/Sidebar";

interface RevisionPlannerPageProps {
  onNavigate: (tab: NavItem) => void;
  onStartSession?: (topicId: number, subjectId: number, minutes: number) => void;
}

export const RevisionPlannerPage: React.FC<RevisionPlannerPageProps> = ({
  onNavigate,
  onStartSession,
}) => {
  const [studyWindowMinutes, setStudyWindowMinutes] = useState<number>(60);

  // Fetch Revision Queue for the given study window
  const { data: queueData, isLoading: isQueueLoading } = useQuery({
    queryKey: ["revision_queue", studyWindowMinutes],
    queryFn: () => api.revision.getQueue(studyWindowMinutes),
  });

  // Fetch summary to see how many completed today
  const { data: studySummary } = useQuery({
    queryKey: ["study_sessions_summary"],
    queryFn: () => api.studySessions.getSummary(),
  });

  const queue = queueData?.queue || [];
  const totalPlannedMinutes = queueData?.total_scheduled_minutes || 0;
  const sessionsCount = queueData?.sessions_count || 0;

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header (Matching Screenshot 2) */}
      <div>
        <Eyebrow>A plan based on your progress</Eyebrow>
        <h1 className="text-3xl font-bold tracking-tight text-[#1F2A24] mt-1">
          Revision planner
        </h1>
        <p className="text-xs text-[#607166] mt-1">
          A focused queue shaped by quiz results, card reviews, and your exam dates.
        </p>
      </div>

      {/* Top Stat Cards (Matching Screenshot 2) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Today's focus */}
        <Card className="p-5 flex flex-col justify-between">
          <Eyebrow className="text-[10px]">Today's focus</Eyebrow>
          <div className="my-2">
            <span className="text-3xl font-bold text-[#1F2A24]">{sessionsCount}</span>
          </div>
          <span className="text-[11px] text-[#8C9B90]">recommended topics</span>
        </Card>

        {/* Card 2: Time planned */}
        <Card className="p-5 flex flex-col justify-between">
          <Eyebrow className="text-[10px]">Time planned</Eyebrow>
          <div className="my-2">
            <span className="text-3xl font-bold text-[#1F2A24]">{totalPlannedMinutes}</span>
            <span className="text-sm font-normal text-[#607166] ml-1">min</span>
          </div>
          <span className="text-[11px] text-[#8C9B90]">within your available time</span>
        </Card>

        {/* Card 3: Completed today */}
        <Card className="p-5 flex flex-col justify-between">
          <Eyebrow className="text-[10px]">Completed today</Eyebrow>
          <div className="my-2">
            <span className="text-3xl font-bold text-[#1F2A24]">
              {studySummary?.total_sessions || 0}
            </span>
          </div>
          <span className="text-[11px] text-[#8C9B90]">sessions recorded</span>
        </Card>

        {/* Card 4: Your study window with slider */}
        <Card className="p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <Eyebrow className="text-[10px]">Your study window</Eyebrow>
            <span className="text-xs font-bold text-[#2F5D46]">{studyWindowMinutes} minutes</span>
          </div>
          <div className="my-3">
            <input
              type="range"
              min="15"
              max="180"
              step="15"
              value={studyWindowMinutes}
              onChange={(e) => setStudyWindowMinutes(Number(e.target.value))}
              className="w-full"
            />
          </div>
          <div className="flex justify-between text-[10px] text-[#8C9B90]">
            <span>15 min</span>
            <span>3 hours</span>
          </div>
        </Card>
      </div>

      {/* Main Card: Your Revision Queue (Matching Screenshot 2) */}
      <Card className="p-6 sm:p-7">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 pb-4 mb-4 border-b border-[#E3E8E2]">
          <div>
            <Eyebrow>Next best actions</Eyebrow>
            <h2 className="text-base font-bold text-[#1F2A24] mt-0.5">Your revision queue</h2>
          </div>
          <span className="text-[11px] text-[#8C9B90]">
            Prioritized from your learning history
          </span>
        </div>

        {isQueueLoading ? (
          <div className="space-y-4 py-3">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        ) : queue.length === 0 ? (
          /* Empty / Clear state */
          <div className="py-12 px-4 text-center max-w-md mx-auto space-y-3">
            <div className="w-10 h-10 rounded-full bg-[#EBF2EC] text-[#2F5D46] flex items-center justify-center mx-auto">
              <CheckCircle className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-[#1F2A24]">You're clear for today.</h3>
            <p className="text-xs text-[#607166] leading-relaxed">
              You've completed the topics that fit your study window. Adjust the time available slider above or add subjects in Plan setup.
            </p>
            <button
              onClick={() => onNavigate("learning")}
              className="mt-2 inline-flex items-center gap-1.5 px-4 py-2 bg-[#2F5D46] text-white rounded-xl text-xs font-semibold hover:bg-[#254B38] transition-colors"
            >
              <span>Manage subjects & topics</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          /* Queue Items List */
          <div className="space-y-3.5">
            {queue.map((item, idx) => (
              <div
                key={item.topic_id}
                className="p-4 rounded-xl border border-[#E3E8E2] bg-white hover:border-[#D7DEC5] transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                {/* Topic Info & Explainable Reason */}
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2.5">
                    <span className="text-xs font-bold text-[#1F2A24]">
                      {idx + 1}. {item.topic_name}
                    </span>
                    <Badge variant={item.session_type}>{item.session_type}</Badge>
                    <span className="text-[11px] text-[#607166]">
                      {item.subject_name}
                    </span>
                  </div>

                  {/* Human-Readable Rationale */}
                  <p className="text-xs text-[#607166] leading-relaxed flex items-center gap-1.5">
                    <Sparkles className="w-3 h-3 text-[#2F5D46] shrink-0" />
                    <span>{item.reason}</span>
                  </p>

                  <div className="flex items-center gap-3 text-[10px] text-[#8C9B90]">
                    <span>Priority rank: {item.priority_score.toFixed(2)}</span>
                    <span>Next projected review: {item.next_review_date}</span>
                  </div>
                </div>

                {/* Right: Duration & Action Buttons */}
                <div className="flex flex-wrap items-center gap-2 self-end sm:self-center shrink-0">
                  <span className="text-xs font-semibold text-[#1F2A24] mr-1">
                    {item.duration_minutes} min
                  </span>

                  {/* Contextual Action Buttons */}
                  {item.session_type === "quiz" && (
                    <button
                      onClick={() => onNavigate("quizzes")}
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-50 text-blue-800 border border-blue-200 hover:bg-blue-100 rounded-xl text-xs font-semibold transition-colors"
                    >
                      <span>Start Quiz</span>
                    </button>
                  )}

                  {item.session_type === "review" && (
                    <button
                      onClick={() => onNavigate("flashcards")}
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-amber-50 text-amber-800 border border-amber-200 hover:bg-amber-100 rounded-xl text-xs font-semibold transition-colors"
                    >
                      <span>Review Cards</span>
                    </button>
                  )}

                  {item.session_type === "learn" && (
                    <button
                      onClick={() => onNavigate("notes")}
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-emerald-50 text-emerald-800 border border-emerald-200 hover:bg-emerald-100 rounded-xl text-xs font-semibold transition-colors"
                    >
                      <span>Read Notes</span>
                    </button>
                  )}

                  <button
                    onClick={() => {
                      if (onStartSession) {
                        onStartSession(item.topic_id, item.subject_id, item.duration_minutes);
                      } else {
                        onNavigate("timer");
                      }
                    }}
                    className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#2F5D46] hover:bg-[#254B38] text-white rounded-xl text-xs font-semibold transition-colors shadow-sm"
                  >
                    <Play className="w-3 h-3 fill-current" />
                    <span>Timer</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Card Footer Rationale Note */}
        <div className="mt-6 pt-4 border-t border-[#E3E8E2] text-[11px] text-[#8C9B90] leading-relaxed">
          Priority combines mastery gaps, recent quiz accuracy, overdue reviews, due flashcards, and exam proximity. Mastery remains an estimate; completing a session records study time but does not change quiz performance.
        </div>
      </Card>

      {/* Bottom Deterministic Calculation Note (Matching Screenshot 2) */}
      <div className="flex items-center gap-2 text-[11px] text-[#607166]">
        <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] inline-block shrink-0"></span>
        <span>
          Recommendations are calculated deterministically from the learning history saved on this device. Quiz scores update mastery; this planner explains how it uses that data.
        </span>
      </div>
    </div>
  );
};
