import React from "react";

interface ProgressBarProps {
  value: number; // 0 to 100
  color?: string;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  color = "#818CF8",
  className = "",
}) => {
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <div
      className={`w-full bg-[#E5EAE3] h-2 rounded-full overflow-hidden ${className}`}
    >
      <div
        className="h-full rounded-full transition-all duration-500 ease-out"
        style={{
          width: `${clamped}%`,
          backgroundColor: color,
        }}
      />
    </div>
  );
};
