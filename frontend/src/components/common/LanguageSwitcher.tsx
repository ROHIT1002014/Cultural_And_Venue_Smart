import React from "react";
import { Globe } from "lucide-react";

interface LanguageSwitcherProps {
  currentLanguage: string;
  onSelect: (langCode: string) => void;
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ currentLanguage, onSelect }) => {
  const languages = [
    { code: "en", name: "English" },
    { code: "es", name: "Español" },
    { code: "fr", name: "Français" },
    { code: "de", name: "Deutsch" },
    { code: "ja", name: "日本語" },
    { code: "hi", name: "हिन्दी" },
  ];

  return (
    <div className="relative flex items-center gap-2 bg-dark-card border border-dark-border px-3 py-1.5 rounded-xl text-sm font-medium text-gray-300">
      <Globe className="w-4 h-4 text-brand-400" />
      <select
        value={currentLanguage}
        onChange={(e) => onSelect(e.target.value)}
        className="bg-transparent text-gray-200 outline-none cursor-pointer"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code} className="bg-dark-surface text-gray-100">
            {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
};
