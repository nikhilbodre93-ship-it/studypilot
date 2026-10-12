import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Card } from "@/components/ui/Card";
import { useToast } from "@/components/ui/Toast";
import { Plus, X, Sparkles, Trash2, Calendar, BookOpen } from "lucide-react";
import { NavItem } from "@/components/layout/Sidebar";

interface PlanSetupPageProps {
  onNavigate: (tab: NavItem) => void;
}

interface LocalTopic {
  id?: number;
  name: string;
  difficulty: "easy" | "medium" | "hard";
}

interface LocalSubject {
  id?: number;
  name: string;
  exam_date: string;
  topics: LocalTopic[];
}

export const PlanSetupPage: React.FC<PlanSetupPageProps> = ({ onNavigate }) => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [subjectsList, setSubjectsList] = useState<LocalSubject[]>([
    {
      name: "",
      exam_date: "",
      topics: [{ name: "", difficulty: "medium" }],
    },
  ]);

  // Fetch existing subjects and topics
  const { data: serverSubjects, isLoading } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => api.subjects.list({ page_size: 50 }),
  });

  useEffect(() => {
    if (serverSubjects?.items && serverSubjects.items.length > 0) {
      // Load topics for each subject
      Promise.all(
        serverSubjects.items.map(async (subj) => {
          const topicsData = await api.topics.listForSubject(subj.id);
          return {
            id: subj.id,
            name: subj.name,
            exam_date: subj.exam_date || "",
            topics: topicsData.items.map((t) => ({
              id: t.id,
              name: t.name,
              difficulty: t.difficulty,
            })),
          };
        })
      ).then((loaded) => {
        if (loaded.length > 0) {
          setSubjectsList(loaded);
        }
      });
    }
  }, [serverSubjects]);

  // Load sample data
  const handleLoadSampleData = () => {
    const today = new Date();
    const addDays = (d: number) => {
      const target = new Date(today);
      target.setDate(target.getDate() + d);
      return target.toISOString().split("T")[0];
    };

    setSubjectsList([
      {
        name: "Biology",
        exam_date: addDays(45),
        topics: [
          { name: "Cell structure", difficulty: "medium" },
          { name: "Genetics & inheritance", difficulty: "hard" },
        ],
      },
      {
        name: "Math",
        exam_date: addDays(30),
        topics: [
          { name: "Calculus: integration", difficulty: "hard" },
          { name: "Statistics", difficulty: "medium" },
        ],
      },
      {
        name: "Computer Engineering",
        exam_date: addDays(60),
        topics: [
          { name: "Data structures", difficulty: "medium" },
          { name: "Computer architecture", difficulty: "hard" },
          { name: "Operating systems", difficulty: "hard" },
        ],
      },
    ]);
    toast("Loaded standard syllabus sample data! Click 'Generate my plan' to schedule.", "info");
  };

  const handleAddSubject = () => {
    setSubjectsList((prev) => [
      ...prev,
      {
        name: "",
        exam_date: "",
        topics: [{ name: "", difficulty: "medium" }],
      },
    ]);
  };

  const handleRemoveSubject = (idx: number) => {
    setSubjectsList((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleAddTopic = (subjectIdx: number) => {
    setSubjectsList((prev) => {
      const copy = [...prev];
      copy[subjectIdx].topics.push({ name: "", difficulty: "medium" });
      return copy;
    });
  };

  const handleRemoveTopic = (subjectIdx: number, topicIdx: number) => {
    setSubjectsList((prev) => {
      const copy = [...prev];
      copy[subjectIdx].topics = copy[subjectIdx].topics.filter((_, i) => i !== topicIdx);
      return copy;
    });
  };

  // Generate Plan Mutation
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSaveAndGenerate = async () => {
    // Validate
    const validSubjects = subjectsList.filter((s) => s.name.trim().length > 0);
    if (validSubjects.length === 0) {
      toast("Please add at least one subject with topics", "error");
      return;
    }

    setIsGenerating(true);
    try {
      // 1. Sync subjects & topics with backend
      for (const subj of validSubjects) {
        let subjectId = subj.id;
        if (!subjectId) {
          const createdSubj = await api.subjects.create({
            name: subj.name.trim(),
            exam_date: subj.exam_date || undefined,
          });
          subjectId = createdSubj.id;
        } else {
          await api.subjects.update(subjectId, {
            name: subj.name.trim(),
            exam_date: subj.exam_date || undefined,
          });
        }

        // Add topics that don't have IDs
        for (const t of subj.topics) {
          if (t.name.trim().length > 0 && !t.id) {
            await api.topics.create(subjectId, {
              name: t.name.trim(),
              difficulty: t.difficulty,
            });
          }
        }
      }

      // 2. Trigger Plan Generator
      const planRes = await api.plan.generate({
        daily_minutes: 60,
        days_horizon: 14,
      });

      queryClient.invalidateQueries({ queryKey: ["subjects"] });
      queryClient.invalidateQueries({ queryKey: ["plan_schedule"] });
      queryClient.invalidateQueries({ queryKey: ["revision_queue"] });
      queryClient.invalidateQueries({ queryKey: ["analytics_summary"] });

      toast(`Revision plan generated! ${planRes.total_sessions_created} sessions scheduled.`, "success");
      onNavigate("planner");
    } catch (err: any) {
      toast(err?.error?.message || "Failed to generate plan", "error");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Page Title (Matching Screenshot 6) */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-[#1F2A24]">Plan setup</h1>
        <p className="text-xs text-[#607166] mt-1">
          Add your subjects, exam dates and topics. Rate each topic's difficulty honestly — the AI uses it to weight your schedule.
        </p>
      </div>

      {/* Subject Cards List */}
      <div className="space-y-6">
        {subjectsList.map((subject, sIdx) => (
          <Card key={sIdx} className="p-6 space-y-4">
            {/* Subject Header Row */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-3">
              <input
                type="text"
                placeholder={`Subject ${sIdx + 1} name (e.g. Computer Engineering)`}
                value={subject.name}
                onChange={(e) => {
                  const val = e.target.value;
                  setSubjectsList((prev) => {
                    const copy = [...prev];
                    copy[sIdx].name = val;
                    return copy;
                  });
                }}
                className="flex-1 px-3.5 py-2.5 rounded-xl border border-[#E3E8E2] text-xs font-medium text-[#1F2A24] placeholder:text-[#8C9B90] focus:outline-none focus:ring-2 focus:ring-[#2F5D46]/20 focus:border-[#2F5D46]"
              />

              <div className="flex items-center gap-2">
                <span className="text-xs text-[#607166] whitespace-nowrap">Exam date</span>
                <input
                  type="date"
                  value={subject.exam_date}
                  onChange={(e) => {
                    const val = e.target.value;
                    setSubjectsList((prev) => {
                      const copy = [...prev];
                      copy[sIdx].exam_date = val;
                      return copy;
                    });
                  }}
                  className="px-3 py-2 rounded-xl border border-[#E3E8E2] text-xs text-[#1F2A24] focus:outline-none focus:ring-2 focus:ring-[#2F5D46]/20 focus:border-[#2F5D46]"
                />
              </div>

              {subjectsList.length > 1 && (
                <button
                  type="button"
                  onClick={() => handleRemoveSubject(sIdx)}
                  className="px-3 py-2 rounded-xl border border-[#FCA5A5] text-[#DC2626] hover:bg-[#FEF2F2] text-xs font-medium transition-colors"
                >
                  Remove
                </button>
              )}
            </div>

            {/* Topics rows for this subject */}
            <div className="space-y-2.5 pt-1">
              {subject.topics.map((topic, tIdx) => (
                <div key={tIdx} className="flex items-center gap-2">
                  <input
                    type="text"
                    placeholder={`Topic ${tIdx + 1} (e.g. Computer architecture)`}
                    value={topic.name}
                    onChange={(e) => {
                      const val = e.target.value;
                      setSubjectsList((prev) => {
                        const copy = [...prev];
                        copy[sIdx].topics[tIdx].name = val;
                        return copy;
                      });
                    }}
                    className="flex-1 px-3.5 py-2 rounded-xl border border-[#E3E8E2] text-xs text-[#1F2A24] placeholder:text-[#8C9B90] focus:outline-none focus:ring-2 focus:ring-[#2F5D46]/20 focus:border-[#2F5D46]"
                  />

                  <select
                    value={topic.difficulty}
                    onChange={(e) => {
                      const diff = e.target.value as "easy" | "medium" | "hard";
                      setSubjectsList((prev) => {
                        const copy = [...prev];
                        copy[sIdx].topics[tIdx].difficulty = diff;
                        return copy;
                      });
                    }}
                    className="px-3 py-2 rounded-xl border border-[#E3E8E2] text-xs text-[#1F2A24] bg-white focus:outline-none focus:ring-2 focus:ring-[#2F5D46]/20 focus:border-[#2F5D46]"
                  >
                    <option value="easy">easy</option>
                    <option value="medium">medium</option>
                    <option value="hard">hard</option>
                  </select>

                  {subject.topics.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveTopic(sIdx, tIdx)}
                      className="p-2 text-[#8C9B90] hover:text-[#DC2626] rounded-lg transition-colors"
                      title="Remove topic"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            {/* Add Topic Button */}
            <button
              type="button"
              onClick={() => handleAddTopic(sIdx)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#E3E8E2] bg-white hover:bg-[#F4F6F1] text-xs font-medium text-[#1F2A24] transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add topic</span>
            </button>
          </Card>
        ))}
      </div>

      {/* Bottom Action Bar (Matching Screenshot 6) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleAddSubject}
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-[#D7DEC5] bg-white hover:bg-[#F4F6F1] text-xs font-semibold text-[#1F2A24] transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Add subject</span>
          </button>

          <button
            type="button"
            onClick={handleLoadSampleData}
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-[#D7DEC5] bg-white hover:bg-[#F4F6F1] text-xs font-semibold text-[#1F2A24] transition-colors shadow-sm"
          >
            <BookOpen className="w-4 h-4 text-[#2F5D46]" />
            <span>Load sample data</span>
          </button>
        </div>

        <button
          type="button"
          disabled={isGenerating}
          onClick={handleSaveAndGenerate}
          className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-[#2F5D46] hover:bg-[#254B38] text-white text-xs font-semibold transition-all shadow-sm disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4 text-[#FDE68A]" />
          <span>{isGenerating ? "Generating plan..." : "Generate my plan"}</span>
        </button>
      </div>
    </div>
  );
};
