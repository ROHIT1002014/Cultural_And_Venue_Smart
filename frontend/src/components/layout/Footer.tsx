import React from "react";
import { ShieldCheck, Heart } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="bg-dark-surface/90 border-t border-dark-border/60 py-6 px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-400">
      <div className="flex items-center gap-2 mb-2 sm:mb-0">
        <ShieldCheck className="w-4 h-4 text-brand-400" />
        <span>Enterprise-Grade AI Guardrails Active & OWASP Compliant</span>
      </div>
      <div className="flex items-center gap-1">
        <span>Architected with</span>
        <Heart className="w-3.5 h-3.5 text-red-400 fill-red-400" />
        <span>for High-Density Cultural Venues & Museums</span>
      </div>
      <div className="mt-2 sm:mt-0 font-mono text-gray-500">v1.0.0-PROD</div>
    </footer>
  );
};
