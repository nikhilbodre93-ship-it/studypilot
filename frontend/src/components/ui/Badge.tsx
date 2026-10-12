import React from "react";

export type BadgeVariant =
  | "learn"
  | "review"
  | "quiz"
  | "rapid_review"
  | "exam_paper"
  | "easy"
  | "medium"
  | "hard"
  | "default";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "default",
  className = "",
}) => {
  const variantStyles: Record<BadgeVariant, string> = {
    learn: "bg-[#EEF2FF] text-[#4F46E5] border border-[#E0E7FF]",
    review: "bg-[#EBF2EC] text-[#2F5D46] border border-[#D7DEC5]",
    quiz: "bg-[#EFF6FF] text-[#2563EB] border border-[#DBEAFE]",
    rapid_review: "bg-[#FEF3C7] text-[#D97706] border border-[#FDE68A]",
    exam_paper: "bg-[#FEE2E2] text-[#DC2626] border border-[#FECACA]",
    easy: "bg-[#ECFDF5] text-[#059669] border border-[#A7F3D0]",
    medium: "bg-[#FFFBEB] text-[#D97706] border border-[#FDE68A]",
    hard: "bg-[#FEF2F2] text-[#E11D48] border border-[#FECDD3]",
    default: "bg-[#F4F6F1] text-[#607166] border border-[#E3E8E2]",
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium tracking-tight ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};
