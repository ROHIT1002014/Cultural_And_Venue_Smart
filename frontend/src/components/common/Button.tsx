import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger";
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  isLoading = false,
  icon,
  className = "",
  disabled,
  ...props
}) => {
  const baseClasses =
    "px-5 py-2.5 rounded-xl font-semibold transition-all duration-200 flex items-center justify-center gap-2.5 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary:
      "bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-lg shadow-brand-500/20 hover:from-brand-500 hover:to-brand-400 hover:shadow-brand-500/40",
    secondary:
      "bg-dark-card border border-dark-border text-gray-200 hover:border-gray-500 hover:bg-dark-card/80",
    danger:
      "bg-gradient-to-r from-red-600 to-red-500 text-white shadow-lg shadow-red-500/20 hover:from-red-500 hover:to-red-400",
  };

  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      ) : (
        icon
      )}
      {children}
    </button>
  );
};
