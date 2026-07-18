import React from "react";

export const LoadingScreen: React.FC<{ message?: string }> = ({ message = "Initializing Smart Copilot Engine..." }) => {
  return (
    <div className="min-h-screen bg-dark-bg flex flex-col items-center justify-center p-6 text-gray-100">
      <div className="relative flex items-center justify-center mb-6">
        <div className="w-20 h-20 border-4 border-brand-500/20 rounded-full animate-ping absolute" />
        <div className="w-16 h-16 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
      <p className="text-lg font-semibold tracking-wide text-brand-400 animate-pulse">{message}</p>
    </div>
  );
};
