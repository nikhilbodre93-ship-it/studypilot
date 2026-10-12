import React from "react";

export const Skeleton: React.FC<{ className?: string }> = ({ className = "" }) => {
  return (
    <div
      className={`animate-pulse bg-[#E5EAE3] rounded-lg ${className}`}
    />
  );
};
