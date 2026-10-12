import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Card } from "@/components/ui/Card";
import { Eyebrow } from "@/components/ui/Eyebrow";
import { Badge } from "@/components/ui/Badge";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Skeleton } from "@/components/ui/Skeleton";
import { TrendingUp, Clock, CheckCircle2, AlertCircle } from "lucide-react";

export const ProgressPage: React.FC = () => {
  const [chartDays, setChartDays] = useState<number>(14);

  // Queries
  const { data: summary, isLoading: isSummaryLoading } = useQuery({
    queryKey: ["analytics_summary"],
    queryFn: () => api.analytics.getSummary(),
  });

  const { data: masteryData, isLoading: isMasteryLoading } = useQuery({
    queryKey: ["analytics_mastery"],
    queryFn: () => api.analytics.getMastery(),
  });

  const { data: chartData, isLoading: isChartLoading } = useQuery({
    queryKey: ["analytics_study_time", chartDays],
    queryFn: () => api.analytics.getStudyTimeByDay(chartDays),
  });

  const subjects = masteryData?.subjects || [];
  const dailyPoints = chartData?.days || [];
  const maxMinutes = Math.max(60, ...dailyPoints.map((d) => d.study_minutes));

  return (
    <div className="space-y-7 max-w-6xl">
      {/* Page Title */}
      <div>
        <Eyebrow>Knowledge Retention & Analytics</Eyebrow>
        <h1 className="text-3xl font-bold tracking-tight text-[#1F2A24] mt-1">
          Progress
        </h1>
        <p className="text-xs text-[#607166] mt-1">
          Bayesian mastery tracking, retention health, and study consistency.
        </p>
      </div>

      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Overall Mastery */}
        <Card className="p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <Eyebrow className="text-[10px]">Overall Mastery</Eyebrow>
            <TrendingUp className="w-4 h-4 text-[#2F5D46]" />
          </div>
          <div className="my-2">
            <span className="text-3xl font-bold text-[#1F2A24]">
              {summary?.overall_mastery_pct || 0}%
            </span>
          </div>
          <span className="text-[11px] text-[#8C9B90]">BKT probabilistic estimate</span>
        </Card>

        {/* Card 2: Total Study Time */}
        <Card className="p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <Eyebrow className="text-[10px]">Study Time</Eyebrow>
            <Clock className="w-4 h-4 text-[#818CF8]" />
          </div>
          <div className="my-2">
            <span className="text-3xl font-bold text-[#1F2A24]">
              {(((summary?.total_study_minutes || 0) / 60)).toFixed(1)}h
            </span>
          </div>
          <span className="text-[11px] text-[#8C9B90]">
            across {summary?.total_study_sessions || 0} sessions
          </span>
        </Card>

        {/* Card 3: Mastered Topics */}
        <Card className="p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <Eyebrow className="text-[10px]">Mastered Topics</Eyebrow>
            <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
          </div>
          <div className="my-2">
            <span className="text-3xl font-bold text-[#1F2A24]">
              {summary?.mastered_topics_count || 0}
            </span>
            <span className="text-xs text-[#607166] ml-1">
              / {summary?.total_topics || 0}
            </span>
          </div>
          <span className="text-[11px] text-[#8C9B90]">mastery ≥ 80%</span>
        </Card>

        {/* Card 4: Overdue Flashcards */}
        <Card className="p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <Eyebrow className="text-[10px]">Cards Due</Eyebrow>
            <AlertCircle className="w-4 h-4 text-[#F59E0B]" />
          </div>
          <div className="my-2">
            <span className="text-3xl font-bold text-[#1F2A24]">
              {summary?.cards_overdue_count || 0}
            </span>
          </div>
          <span className="text-[11px] text-[#8C9B90]">SM-2 spaced repetitions</span>
        </Card>
      </div>

      {/* Study Time By Day Chart */}
      <Card className="p-6 sm:p-7">
        <div className="flex items-center justify-between mb-6">
          <div>
            <Eyebrow>Consistency</Eyebrow>
            <h2 className="text-base font-bold text-[#1F2A24] mt-0.5">Study time by day</h2>
          </div>

          <div className="flex items-center gap-2">
            {[7, 14, 30].map((d) => (
              <button
                key={d}
                onClick={() => setChartDays(d)}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors ${
                  chartDays === d
                    ? "bg-[#2F5D46] text-white"
                    : "bg-[#F4F6F1] text-[#607166] hover:text-[#1F2A24]"
                }`}
              >
                {d}d
              </button>
            ))}
          </div>
        </div>

        {/* Clean Responsive Bar Chart */}
        {isChartLoading ? (
          <Skeleton className="h-44 w-full" />
        ) : (
          <div className="space-y-2">
            <div className="h-44 flex items-end justify-between gap-1.5 sm:gap-2 pt-6 px-1">
              {dailyPoints.map((pt, idx) => {
                const heightPct = Math.min(100, Math.round((pt.study_minutes / maxMinutes) * 100));
                const dayLabel = pt.date.slice(8); // DD

                return (
                  <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group">
                    {/* Tooltip on hover */}
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity text-[10px] bg-[#1F2A24] text-white px-1.5 py-0.5 rounded whitespace-nowrap pointer-events-none mb-1">
                      {pt.study_minutes}m ({pt.session_count}s)
                    </div>

                    <div
                      className={`w-full max-w-[28px] rounded-t-md transition-all duration-300 ${
                        pt.study_minutes > 0
                          ? "bg-[#818CF8] hover:bg-[#6366F1]"
                          : "bg-[#E5EAE3] h-1"
                      }`}
                      style={{ height: pt.study_minutes > 0 ? `${Math.max(8, heightPct)}%` : "4px" }}
                    />

                    <span className="text-[10px] text-[#8C9B90] mt-1">{dayLabel}</span>
                  </div>
                );
              })}
            </div>
            <div className="flex justify-between items-center text-[11px] text-[#8C9B90] pt-2 border-t border-[#E3E8E2]">
              <span>Total studied in period: {chartData?.total_period_minutes || 0} minutes</span>
              <span>Max day: {maxMinutes} minutes</span>
            </div>
          </div>
        )}
      </Card>

      {/* Topic Mastery Breakdown by Subject */}
      <Card className="p-6 sm:p-7">
        <Eyebrow>Topic Mastery Breakdown</Eyebrow>
        <h2 className="text-base font-bold text-[#1F2A24] mt-0.5 mb-6">Subject & Topic Mastery</h2>

        {isMasteryLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        ) : subjects.length === 0 ? (
          <p className="text-xs text-[#8C9B90] py-4 text-center">
            No subjects or topics tracked yet.
          </p>
        ) : (
          <div className="space-y-6">
            {subjects.map((subj) => (
              <div key={subj.subject_id} className="p-4 rounded-xl border border-[#E3E8E2] bg-[#FAFBF9] space-y-4">
                {/* Subject Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: subj.color || "#2F5D46" }}
                    />
                    <h3 className="text-sm font-bold text-[#1F2A24]">{subj.subject_name}</h3>
                  </div>
                  <span className="text-xs font-semibold text-[#2F5D46]">
                    Average {subj.average_mastery}%
                  </span>
                </div>

                {/* Topics List */}
                <div className="space-y-3 pt-1">
                  {subj.topics.map((t) => (
                    <div
                      key={t.topic_id}
                      className="p-3 bg-white rounded-xl border border-[#E3E8E2] space-y-2"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-[#1F2A24]">{t.topic_name}</span>
                          <Badge variant={t.difficulty as any}>{t.difficulty}</Badge>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-[11px] text-[#607166]">
                            Observed Acc: {Math.round(t.observed_accuracy * 100)}% ({t.observed_total} attempts)
                          </span>
                          <span className="font-bold text-[#1F2A24]">{t.score}%</span>
                        </div>
                      </div>

                      <ProgressBar
                        value={t.score}
                        color={t.score >= 80 ? "#10B981" : t.score >= 50 ? "#818CF8" : "#F59E0B"}
                      />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
