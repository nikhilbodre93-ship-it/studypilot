import React from "react";
import { Card } from "./Card";
import { Eyebrow } from "./Eyebrow";
import { Sparkles, ArrowRight } from "lucide-react";

interface EmptyStateProps {
  phase: number;
  title: string;
  eyebrow?: string;
  description: string;
  previewFeatures: string[];
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  phase,
  title,
  eyebrow = "COMING SOON",
  description,
  previewFeatures,
  actionLabel,
  onAction,
}) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Eyebrow>{eyebrow}</Eyebrow>
        <h1 className="text-3xl font-bold tracking-tight text-[#1F2A24] mt-1">{title}</h1>
        <p className="text-sm text-[#607166] mt-1 max-w-xl">{description}</p>
      </div>

      {/* Main Preview Card */}
      <Card className="p-8 border-dashed border-[#D7DEC5] bg-white/70">
        <div className="max-w-lg">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#EBF2EC] text-[#2F5D46] text-xs font-semibold mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Scheduled for Phase {phase}</span>
          </div>

          <h3 className="text-lg font-semibold text-[#1F2A24] mb-2">
            This module is arriving in Phase {phase}
          </h3>
          <p className="text-sm text-[#607166] leading-relaxed mb-6">
            StudyPilot builds revision intelligence step by step. This capability will be activated in the next development milestone.
          </p>

          <div className="space-y-2.5 mb-6">
            <span className="text-[11px] font-semibold tracking-wider text-[#607166] uppercase block">
              Planned capabilities:
            </span>
            {previewFeatures.map((feat, idx) => (
              <div key={idx} className="flex items-center gap-2 text-xs text-[#1F2A24]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#2F5D46]" />
                <span>{feat}</span>
              </div>
            ))}
          </div>

          {actionLabel && onAction && (
            <button
              onClick={onAction}
              className="inline-flex items-center gap-2 px-4 py-2 bg-[#2F5D46] hover:bg-[#254B38] text-white rounded-xl text-xs font-semibold transition-colors shadow-sm"
            >
              <span>{actionLabel}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </Card>
    </div>
  );
};
