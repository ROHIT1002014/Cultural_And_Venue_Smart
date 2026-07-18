import React from "react";
import { useAuth } from "@/context/AuthContext";
import { useTheme } from "@/context/ThemeContext";
import { Sparkles, Sun, Moon, LogOut, ShieldAlert } from "lucide-react";

export const Navbar: React.FC<{ onNavigate: (path: string) => void }> = ({ onNavigate }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="sticky top-0 z-40 bg-dark-surface/80 backdrop-blur-md border-b border-dark-border/60 px-6 py-3.5 flex items-center justify-between">
      <div
        onClick={() => onNavigate("/")}
        className="flex items-center gap-3 cursor-pointer group"
      >
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-400 flex items-center justify-center text-white shadow-lg shadow-brand-500/30 group-hover:scale-105 transition-transform">
          <Sparkles className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-gray-200 to-brand-400 bg-clip-text text-transparent">
            Cultural<span className="text-brand-400">Copilot</span>
          </span>
          <span className="block text-xs text-gray-400 font-medium">Smart AI Operations</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={toggleTheme}
          className="p-2.5 rounded-xl bg-dark-card border border-dark-border text-gray-300 hover:text-brand-400 transition-colors"
          title="Toggle Theme"
        >
          {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        {user ? (
          <div className="flex items-center gap-3 bg-dark-card border border-dark-border/80 px-4 py-1.5 rounded-xl">
            <div className="text-right hidden sm:block">
              <span className="block text-sm font-semibold text-gray-200">{user.full_name}</span>
              <span className="block text-xs text-brand-400 font-mono tracking-wider">{user.role}</span>
            </div>
            {user.role === "ADMIN" && (
              <button
                onClick={() => onNavigate("/admin")}
                className="p-2 bg-brand-500/20 text-brand-400 rounded-lg hover:bg-brand-500/30 transition-colors"
                title="Admin Dashboard"
              >
                <ShieldAlert className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={logout}
              className="p-2 text-gray-400 hover:text-red-400 transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigate("/login")}
              className="text-sm font-medium text-gray-300 hover:text-white px-3 py-1.5"
            >
              Sign In
            </button>
            <button
              onClick={() => onNavigate("/register")}
              className="bg-gradient-to-r from-brand-600 to-brand-500 text-white font-semibold text-sm px-4 py-2 rounded-xl shadow-lg shadow-brand-500/20 hover:shadow-brand-500/40 transition-all"
            >
              Get Started
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};
