import React, { useState, useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Card } from "@/components/ui/Card";
import { useToast } from "@/components/ui/Toast";
import { Play, Pause, Square, RotateCcw } from "lucide-react";

interface FocusTimerPageProps {
  initialSubjectId?: number | null;
  initialTopicId?: number | null;
  initialMinutes?: number;
}

export const FocusTimerPage: React.FC<FocusTimerPageProps> = ({
  initialSubjectId = null,
  initialTopicId = null,
  initialMinutes = 25,
}) => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [targetMinutes, setTargetMinutes] = useState<number>(initialMinutes);
  const [secondsRemaining, setSecondsRemaining] = useState<number>(initialMinutes * 60);
  const [isActive, setIsActive] = useState<boolean>(false);
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0);

  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(initialSubjectId);
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(initialTopicId);

  // Queries
  const { data: subjectsData } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => api.subjects.list({ page_size: 50 }),
  });

  const { data: recentSessionsData } = useQuery({
    queryKey: ["study_sessions"],
    queryFn: () => api.studySessions.list({ page_size: 10 }),
  });

  // Set default subject if none selected
  useEffect(() => {
    if (!selectedSubjectId && subjectsData?.items && subjectsData.items.length > 0) {
      setSelectedSubjectId(subjectsData.items[0].id);
    }
  }, [subjectsData, selectedSubjectId]);

  // Log session mutation
  const logMutation = useMutation({
    mutationFn: (actualMinutes: number) => {
      return api.studySessions.create({
        subject_id: selectedSubjectId,
        topic_id: selectedTopicId,
        duration_minutes: Math.max(1, actualMinutes),
        session_type: "pomodoro",
        notes: `Focus timer session (${targetMinutes}m target)`,
      });
    },
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ["study_sessions"] });
      queryClient.invalidateQueries({ queryKey: ["study_sessions_summary"] });
      queryClient.invalidateQueries({ queryKey: ["analytics_summary"] });
      toast(`Logged ${session.duration_minutes} minutes study session!`, "success");
    },
  });

  // Timer interval effect
  useEffect(() => {
    let interval: any = null;
    if (isActive && secondsRemaining > 0) {
      interval = setInterval(() => {
        setSecondsRemaining((prev) => prev - 1);
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    } else if (isActive && secondsRemaining === 0) {
      // Completed full session
      setIsActive(false);
      const actualMinutes = Math.round(elapsedSeconds / 60) || targetMinutes;
      logMutation.mutate(actualMinutes);
      toast("Focus session complete! Excellent work.", "success");
    }

    return () => clearInterval(interval);
  }, [isActive, secondsRemaining, elapsedSeconds, targetMinutes]);

  // Change preset duration
  const handleSelectPreset = (mins: number) => {
    if (isActive) {
      if (!confirm("Timer is running. Reset to switch duration?")) return;
      handleStopAndLog();
    }
    setTargetMinutes(mins);
    setSecondsRemaining(mins * 60);
    setElapsedSeconds(0);
    setIsActive(false);
  };

  // Toggle Start / Pause
  const handleToggle = () => {
    setIsActive(!isActive);
  };

  // Early stop & log actual minutes
  const handleStopAndLog = () => {
    const actualMinutes = Math.round(elapsedSeconds / 60);
    setIsActive(false);

    if (actualMinutes >= 1) {
      logMutation.mutate(actualMinutes);
    } else {
      toast("Session was under 1 minute; not logged.", "info");
    }

    // Reset timer
    setSecondsRemaining(targetMinutes * 60);
    setElapsedSeconds(0);
  };

  const handleReset = () => {
    setIsActive(false);
    setSecondsRemaining(targetMinutes * 60);
    setElapsedSeconds(0);
  };

  // Format MM:SS
  const mins = Math.floor(secondsRemaining / 60);
  const secs = secondsRemaining % 60;
  const timeFormatted = `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;

  const subjects = subjectsData?.items || [];
  const recentSessions = recentSessionsData?.items || [];

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Page Title (Matching Screenshot 3) */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-[#1F2A24]">Focus timer</h1>
        <p className="text-xs text-[#607166] mt-1">
          Pomodoro-style sessions. Stopping early still logs the minutes you actually studied.
        </p>
      </div>

      {/* Main Timer Card (Matching Screenshot 3) */}
      <Card className="py-14 px-6 sm:px-12 flex flex-col items-center justify-center text-center">
        {/* Huge Timer Digits */}
        <div className="text-6xl sm:text-7xl font-bold tracking-tight text-[#1F2A24] font-mono select-none mb-10">
          {timeFormatted}
        </div>

        {/* Duration Presets & Subject Picker */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-8">
          {[25, 45, 60].map((mins) => {
            const isSelected = targetMinutes === mins;
            return (
              <button
                key={mins}
                type="button"
                onClick={() => handleSelectPreset(mins)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  isSelected
                    ? "border border-[#818CF8] bg-white text-[#1F2A24] shadow-sm"
                    : "border border-[#E3E8E2] bg-white text-[#607166] hover:bg-[#F4F6F1]"
                }`}
              >
                {mins} min
              </button>
            );
          })}

          {/* Subject Dropdown */}
          <select
            value={selectedSubjectId || ""}
            onChange={(e) => setSelectedSubjectId(Number(e.target.value) || null)}
            className="px-4 py-2 rounded-xl border border-[#E3E8E2] text-xs font-semibold text-[#1F2A24] bg-white focus:outline-none focus:ring-2 focus:ring-[#2F5D46]/20"
          >
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
            {subjects.length === 0 && <option value="">General</option>}
          </select>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleToggle}
            className="inline-flex items-center gap-2 px-6 py-2.5 bg-[#2F5D46] hover:bg-[#254B38] text-white rounded-xl text-xs font-semibold transition-all shadow-sm"
          >
            {isActive ? (
              <>
                <Pause className="w-3.5 h-3.5 fill-current" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Start</span>
              </>
            )}
          </button>

          {elapsedSeconds > 0 && (
            <button
              type="button"
              onClick={handleStopAndLog}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 border border-[#DC2626] text-[#DC2626] hover:bg-[#FEF2F2] rounded-xl text-xs font-semibold transition-colors"
              title="Stop early and log studied minutes"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>Stop & Log ({Math.max(1, Math.round(elapsedSeconds / 60))}m)</span>
            </button>
          )}

          {!isActive && elapsedSeconds > 0 && (
            <button
              type="button"
              onClick={handleReset}
              className="p-2.5 border border-[#E3E8E2] text-[#607166] hover:bg-[#F4F6F1] rounded-xl transition-colors"
              title="Reset timer without logging"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </Card>

      {/* Recent Sessions Card (Matching Screenshot 3) */}
      <Card className="p-6">
        <h2 className="text-xs font-semibold text-[#607166] mb-4">Recent sessions</h2>
        {recentSessions.length === 0 ? (
          <p className="text-xs text-[#8C9B90] py-4">
            No study sessions recorded yet. Start your first focus timer session above!
          </p>
        ) : (
          <div className="space-y-3">
            {recentSessions.map((session) => (
              <div
                key={session.id}
                className="flex items-center justify-between py-2 border-b border-[#F4F6F1] last:border-none text-xs"
              >
                <span className="font-medium text-[#1F2A24]">
                  {session.subject_name || "General"}
                </span>
                <span className="text-[#8C9B90]">
                  {session.duration_minutes} min · {session.created_at.split("T")[0]}
                </span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
