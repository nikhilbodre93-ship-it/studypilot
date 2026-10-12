import React from "react";

export const Eyebrow: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = "",
}) => {
  return (
    <span
      className={`text-[11px] font-semibold tracking-wider text-[#607166] uppercase select-none ${className}`}
    >
      {children}
    </span>
  );
};
