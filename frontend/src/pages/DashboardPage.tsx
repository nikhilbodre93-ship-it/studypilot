import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Card } from "@/components/ui/Card";
import { Eyebrow } from "@/components/ui/Eyebrow";
import { Badge } from "@/components/ui/Badge";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Skeleton } from "@/components/ui/Skeleton";
import { useToast } from "@/components/ui/Toast";
import { Check, CheckSquare, Square, Calendar, ArrowRight, Sparkles } from "lucide-react";
import { NavItem } from "@/components/layout/Sidebar";

interface DashboardPageProps {
  onNavigate: (tab: NavItem) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Queries
  const { data: analytics, isLoading: isAnalyticsLoading } = useQuery({
    queryKey: ["analytics_summary"],
    queryFn: () => api.analytics.getSummary(),
  });

  const { data: schedule, isLoading: isScheduleLoading } = useQuery({
    queryKey: ["plan_schedule"],
    queryFn: () => api.plan.getSchedule(),
  });

  const { data: queueData } = useQuery({
    queryKey: ["revision_queue", 60],
    queryFn: () => api.revision.getQueue(60),
  });

  // Toggle session status mutation
  const toggleMutation = useMutation({
    mutationFn: async ({ id, newStatus }: { id: number; newStatus: "completed" | "pending" }) => {
      return api.plan.updateSessionStatus(id, newStatus);
    },
    onSuccess: (updatedSession) => {
      queryClient.invalidateQueries({ queryKey: ["plan_schedule"] });
      queryClient.invalidateQueries({ queryKey: ["analytics_summary"] });
      queryClient.invalidateQueries({ queryKey: ["revision_queue"] });
      toast(
        updatedSession.status === "completed"
          ? `Marked "${updatedSession.topic_name || "Session"}" as completed!`
          : "Session marked as pending",
        "success"
      );
    },
  });

  // Format next exam
  const nextExam = analytics?.upcoming_exams && analytics.upcoming_exams.length > 0
    ? analytics.upcoming_exams[0]
    : null;

  const nextExamText = nextExam
    ? `Next exam: ${nextExam.subject_name} on ${new Date(nextExam.exam_date).toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
      })}`
    : "No upcoming exams set";

  // Calculate plan progress
  const totalSessions = schedule?.length || 0;
  const completedSessions = schedule?.filter((s) => s.status === "completed").length || 0;
  const progressPct = totalSessions > 0 ? Math.round((completedSessions / totalSessions) * 100) : 0;

  // Today's sessions
  const todayStr = new Date().toISOString().split("T")[0];
  const todaySessions = schedule?.filter((s) => s.scheduled_date === todayStr) || [];
  const displaySessions = todaySessions.length > 0 ? todaySessions : (schedule?.slice(0, 5) || []);

  const topRecommendation = queueData?.queue && queueData.queue.length > 0 ? queueData.queue[0] : null;

  return (
    <div className="space-y-7 max-w-6xl">
      {/* Page Header (Matching Screenshot 5) */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-[#1F2A24]">Dashboard</h1>
          <p className="text-xs text-[#607166] mt-1">{nextExamText}</p>
        </div>

        <button
          onClick={() => onNavigate("learning")}
          className="self-start sm:self-auto px-4 py-2 rounded-xl border border-[#D7DEC5] bg-white hover:bg-[#F4F6F1] text-xs font-semibold text-[#1F2A24] transition-colors shadow-sm"
        >
          Edit plan
        </button>
      </div>

      {/* Top Stat Cards (Matching Screenshot 5) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Card 1: Plan progress */}
        <Card className="flex flex-col justify-between">
          <div>
            <span className="text-xs text-[#607166] block mb-1">Plan progress</span>
            <div className="flex items-baseline gap-2 mb-3">
              <span className="text-3xl font-bold text-[#1F2A24]">{progressPct}%</span>
            </div>
            <ProgressBar value={progressPct} color="#818CF8" />
          </div>
          <span className="text-[11px] text-[#8C9B90] mt-3 block">
            {completedSessions} of {totalSessions} sessions done
          </span>
        </Card>

        {/* Card 2: Focus time logged */}
        <Card className="flex flex-col justify-between">
          <div>
            <span className="text-xs text-[#607166] block mb-1">Focus time logged</span>
            <div className="flex items-baseline gap-2 mb-3">
              <span className="text-3xl font-bold text-[#1F2A24]">
                {((analytics?.total_study_minutes || 0) / 60).toFixed(1)}h
              </span>
            </div>
          </div>
          <span className="text-[11px] text-[#8C9B90] block">
            {analytics?.total_study_sessions || 0} sessions
          </span>
        </Card>

        {/* Card 3: Subjects tracked */}
        <Card className="flex flex-col justify-between">
          <div>
            <span className="text-xs text-[#607166] block mb-1">Subjects tracked</span>
            <div className="flex items-baseline gap-2 mb-3">
              <span className="text-3xl font-bold text-[#1F2A24]">
                {analytics?.total_subjects || 0}
              </span>
            </div>
          </div>
          <span className="text-[11px] text-[#8C9B90] block">
            {analytics?.total_topics || 0} topics total
          </span>
        </Card>
      </div>

      {/* Today's Sessions Card (Matching Screenshot 5) */}
      <Card>
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-base font-bold text-[#1F2A24]">Today's sessions</h2>
          {displaySessions.length > 0 && (
            <span className="text-xs text-[#607166]">
              {displaySessions.filter((s) => s.status === "completed").length} / {displaySessions.length} done
            </span>
          )}
        </div>

        {isScheduleLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-14 w-full" />
            <Skeleton className="h-14 w-full" />
            <Skeleton className="h-14 w-full" />
          </div>
        ) : displaySessions.length === 0 ? (
          <div className="text-center py-8 px-4 border border-dashed border-[#D7DEC5] rounded-xl bg-[#F4F6F1]/50">
            <p className="text-xs text-[#607166] mb-3">
              No sessions scheduled for today yet. Set up subjects or generate your revision plan!
            </p>
            <button
              onClick={() => onNavigate("learning")}
              className="inline-flex items-center gap-2 px-4 py-2 bg-[#2F5D46] text-white rounded-xl text-xs font-semibold hover:bg-[#254B38] transition-colors"
            >
              <span>Setup study subjects & plan</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <div className="space-y-2.5">
            {displaySessions.map((session) => {
              const isDone = session.status === "completed";
              return (
                <div
                  key={session.id}
                  className={`flex items-center justify-between p-3.5 rounded-xl border transition-all ${
                    isDone
                      ? "bg-[#F9FAF8] border-[#E3E8E2] opacity-75"
                      : "bg-white border-[#E3E8E2] hover:border-[#D7DEC5]"
                  }`}
                >
                  {/* Left: Checkbox & Info */}
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() =>
                        toggleMutation.mutate({
                          id: session.id,
                          newStatus: isDone ? "pending" : "completed",
                        })
                      }
                      className="text-[#2F5D46] hover:scale-105 transition-transform"
                    >
                      {isDone ? (
                        <CheckSquare className="w-5 h-5 text-[#2F5D46]" />
                      ) : (
                        <Square className="w-5 h-5 text-[#8C9B90] hover:text-[#2F5D46]" />
                      )}
                    </button>

                    <div>
                      <span
                        className={`text-xs font-semibold block ${
                          isDone ? "line-through text-[#8C9B90]" : "text-[#1F2A24]"
                        }`}
                      >
                        {session.topic_name || "Study session"}
                      </span>
                      <span className="text-[11px] text-[#607166]">
                        {session.subject_name || "General"}
                      </span>
                    </div>
                  </div>

                  {/* Right: Badges */}
                  <div className="flex items-center gap-2.5">
                    <Badge variant={session.session_type as any}>
                      {session.session_type}
                    </Badge>
                    <span className="text-xs text-[#607166] min-w-[50px] text-right font-medium">
                      {session.duration_minutes} min
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* "Why this next?" Explainability Card */}
      {topRecommendation && (
        <Card className="bg-[#FAFBF9] border-[#D7DEC5]">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-[#2F5D46]" />
            <Eyebrow>Adaptive Recommendation Reason</Eyebrow>
          </div>
          <h3 className="text-sm font-bold text-[#1F2A24] mb-1">
            Why focus on "{topRecommendation.topic_name}" next?
          </h3>
          <p className="text-xs text-[#607166] leading-relaxed mb-3">
            {topRecommendation.reason}
          </p>
          <div className="flex items-center gap-4 text-[11px] text-[#8C9B90]">
            <span>Priority score: {topRecommendation.priority_score.toFixed(2)}</span>
            <span>Recommended session: {topRecommendation.session_type}</span>
            <span>Allocated time: {topRecommendation.duration_minutes} min</span>
          </div>
        </Card>
      )}

      {/* Full Schedule Section */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold text-[#1F2A24]">Full schedule</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {schedule && schedule.length > 0 ? (
            schedule.slice(0, 8).map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-3 rounded-xl bg-white border border-[#E3E8E2] text-xs"
              >
                <div>
                  <div className="font-semibold text-[#1F2A24]">{item.topic_name}</div>
                  <div className="text-[11px] text-[#607166]">
                    {item.subject_name} · {item.scheduled_date}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={item.session_type as any}>{item.session_type}</Badge>
                  <span className="text-[11px] text-[#8C9B90]">{item.duration_minutes}m</span>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-2 text-xs text-[#8C9B90] py-4 text-center">
              No future sessions planned yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
