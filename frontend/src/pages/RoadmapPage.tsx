import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { RoadmapItem, Subject, RoadmapPhaseItem, RoadmapTaskItem } from "@/types";
import {
  MapPin,
  Sparkles,
  CheckCircle,
  Circle,
  Clock,
  RotateCcw,
  BookOpen,
  HelpCircle,
  Layers,
  Calendar,
} from "lucide-react";
import { useToast } from "@/components/ui/Toast";

interface RoadmapPageProps {
  onNavigate: (tab: any, params?: any) => void;
}

export const RoadmapPage: React.FC<RoadmapPageProps> = ({ onNavigate }) => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Load subjects
  const { data: subjectsData } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => api.subjects.list({ page_size: 50 }),
  });
  const subjects = subjectsData?.items || [];
  const currentSubjectId = selectedSubjectId || subjects[0]?.id;

  // Load active roadmap
  const { data: roadmapData, refetch: refetchRoadmap } = useQuery({
    queryKey: ["roadmap", currentSubjectId],
    queryFn: () => (currentSubjectId ? api.roadmap.getBySubject(currentSubjectId) : null),
    enabled: !!currentSubjectId,
  });

  const roadmap = roadmapData?.roadmap;

  const handleGenerateRoadmap = async () => {
    if (!currentSubjectId) return;
    setIsGenerating(true);
    try {
      await api.roadmap.generate(currentSubjectId);
      showToast("Personalized learning roadmap generated from your topic mastery profile!", "success");
      refetchRoadmap();
    } catch (err: any) {
      showToast(err?.error?.message || "Failed to generate roadmap", "error");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleToggleTask = async (taskId: string, currentVal: boolean) => {
    if (!currentSubjectId) return;
    try {
      await api.roadmap.toggleTask(currentSubjectId, taskId, !currentVal);
      refetchRoadmap();
    } catch (err) {
      showToast("Failed to toggle task", "error");
    }
  };

  const getTaskIcon = (type: string) => {
    switch (type) {
      case "quiz":
        return <HelpCircle className="w-3.5 h-3.5 text-blue-600" />;
      case "review":
        return <Layers className="w-3.5 h-3.5 text-amber-600" />;
      default:
        return <BookOpen className="w-3.5 h-3.5 text-emerald-600" />;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-[#2F5D46] tracking-wider uppercase">
            Syllabus Phasing & Mastery Milestones
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1F2A24] tracking-tight mt-1 font-serif">
            Learning Roadmap
          </h1>
          <p className="text-sm text-[#607166] mt-1">
            A milestone-based progression broken down into weekly phases and actionable study tasks.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {subjects.length > 0 && (
            <select
              value={currentSubjectId || ""}
              onChange={(e) => setSelectedSubjectId(Number(e.target.value))}
              className="text-xs px-3 py-2 rounded-xl bg-white border border-[#E3E8E2] text-[#1F2A24]"
            >
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          )}

          <button
            onClick={handleGenerateRoadmap}
            disabled={isGenerating || !currentSubjectId}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#2F5D46] text-white text-xs font-semibold hover:bg-[#254A37] transition-colors shadow-sm disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{roadmap ? "Regenerate from Progress" : "Generate Roadmap"}</span>
          </button>
        </div>
      </div>

      {/* Roadmap Content */}
      {roadmap && roadmap.phases ? (
        <div className="space-y-6">
          {/* Summary Banner */}
          <div className="p-5 bg-white rounded-2xl border border-[#E3E8E2] flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-[#2F5D46] uppercase">Strategic Trajectory</span>
              <h2 className="text-base font-bold text-[#1F2A24] mt-0.5 font-serif">{roadmap.title}</h2>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#EBF2EC] text-[#2F5D46] text-xs font-semibold">
              <Clock className="w-4 h-4" />
              <span>Est. {roadmap.total_estimated_hours} Hours Total</span>
            </div>
          </div>

          {/* Chronological Phase Timeline */}
          <div className="space-y-6">
            {roadmap.phases.map((phase: RoadmapPhaseItem) => {
              const completedTasksCount = phase.tasks.filter((t) => t.completed).length;
              const totalTasksCount = phase.tasks.length;
              const phasePct = Math.round((completedTasksCount / totalTasksCount) * 100) || 0;

              return (
                <div
                  key={phase.phase_number}
                  className="bg-white rounded-2xl border border-[#E3E8E2] p-6 space-y-4"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#E3E8E2]">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-[#EBF2EC] text-[#2F5D46]">
                          Phase {phase.phase_number}
                        </span>
                        <span className="text-xs text-[#8C9B90]">{phase.timeframe}</span>
                      </div>
                      <h3 className="text-base font-bold text-[#1F2A24] mt-1">{phase.name}</h3>
                      <p className="text-xs text-[#607166] mt-0.5">{phase.summary}</p>
                    </div>

                    <div className="text-right shrink-0">
                      <span className="text-xs font-semibold text-[#1F2A24]">
                        {completedTasksCount} / {totalTasksCount} Completed ({phasePct}%)
                      </span>
                      <div className="w-24 h-1.5 bg-[#EBF2EC] rounded-full overflow-hidden mt-1">
                        <div
                          className="h-full bg-[#2F5D46] rounded-full transition-all duration-300"
                          style={{ width: `${phasePct}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Tasks List */}
                  <div className="space-y-2">
                    {phase.tasks.map((task: RoadmapTaskItem) => (
                      <div
                        key={task.id}
                        onClick={() => handleToggleTask(task.id, task.completed)}
                        className={`p-3 rounded-xl border transition-all flex items-center justify-between cursor-pointer select-none ${
                          task.completed
                            ? "bg-[#F4F6F1]/60 border-[#E3E8E2] text-[#8C9B90]"
                            : "bg-white border-[#E3E8E2] hover:border-[#2F5D46] text-[#1F2A24]"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          {task.completed ? (
                            <CheckCircle className="w-5 h-5 text-emerald-600 shrink-0" />
                          ) : (
                            <Circle className="w-5 h-5 text-[#8C9B90] shrink-0" />
                          )}
                          <div>
                            <span className={`text-xs font-medium block ${task.completed ? "line-through text-[#8C9B90]" : "text-[#1F2A24]"}`}>
                              {task.title}
                            </span>
                            <span className="text-[10px] text-[#607166]">
                              Topic: {task.topic_name}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          <span className="text-[10px] px-2 py-0.5 rounded bg-[#F4F6F1] text-[#607166] flex items-center gap-1 font-medium capitalize">
                            {getTaskIcon(task.task_type)}
                            <span>{task.task_type}</span>
                          </span>
                          <span className="text-[10px] text-[#8C9B90]">
                            {task.estimated_minutes}m
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="p-12 bg-white rounded-2xl border border-[#E3E8E2] text-center space-y-3">
          <MapPin className="w-12 h-12 text-[#2F5D46] mx-auto opacity-70" />
          <h2 className="text-base font-semibold text-[#1F2A24]">No Roadmap Generated Yet</h2>
          <p className="text-xs text-[#607166] max-w-sm mx-auto">
            Click "Generate Roadmap" to analyze your current topic masteries and construct a phased study timeline.
          </p>
          <button
            onClick={handleGenerateRoadmap}
            disabled={isGenerating || !currentSubjectId}
            className="px-5 py-2.5 rounded-xl bg-[#2F5D46] text-white text-xs font-semibold hover:bg-[#254A37] transition-colors shadow-sm disabled:opacity-50"
          >
            {isGenerating ? "Building Phased Plan..." : "Generate Roadmap"}
          </button>
        </div>
      )}
    </div>
  );
};
