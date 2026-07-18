import React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hoverEffect?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = "",
  onClick,
  hoverEffect = true,
}) => {
  const baseClasses =
    "bg-dark-surface/80 backdrop-blur-md border border-dark-border/60 rounded-2xl p-6 transition-all duration-300";
  const hoverClasses = hoverEffect
    ? "hover:border-brand-500/50 hover:shadow-[0_0_25px_rgba(34,197,94,0.15)] cursor-pointer"
    : "";

  return (
    <div
      onClick={onClick}
      className={`${baseClasses} ${hoverClasses} ${className}`}
    >
      {children}
    </div>
  );
};
