import React from "react";
import { MessageSquare, Map, Car, ShieldAlert, Home } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export const Sidebar: React.FC<{ activeTab: string; onSelectTab: (tab: string) => void }> = ({
  activeTab,
  onSelectTab,
}) => {
  const { user } = useAuth();

  const items = [
    { id: "home", label: "Overview", icon: <Home className="w-5 h-5" /> },
    { id: "copilot", label: "AI Copilot & Map", icon: <MessageSquare className="w-5 h-5" /> },
    { id: "navigation", label: "Interactive Map", icon: <Map className="w-5 h-5" /> },
    { id: "parking", label: "Parking Logistics", icon: <Car className="w-5 h-5" /> },
  ];

  if (user?.role === "ADMIN" || user?.role === "VOLUNTEER") {
    items.push({ id: "admin", label: "Admin Operations", icon: <ShieldAlert className="w-5 h-5" /> });
  }

  return (
    <aside className="w-64 bg-dark-surface/60 backdrop-blur-md border-r border-dark-border/60 p-4 flex flex-col gap-2 min-h-[calc(100vh-65px)]">
      <div className="text-xs font-bold text-gray-500 uppercase tracking-wider px-3 py-2">
        Platform Navigation
      </div>
      {items.map((item) => {
        const isActive = activeTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => onSelectTab(item.id)}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 text-sm ${
              isActive
                ? "bg-gradient-to-r from-brand-600/30 to-transparent text-brand-400 border-l-4 border-brand-500 shadow-sm"
                : "text-gray-400 hover:text-gray-200 hover:bg-dark-card/50"
            }`}
          >
            <span className={isActive ? "text-brand-400" : "text-gray-500"}>{item.icon}</span>
            {item.label}
          </aside>
        );
      })}
    </aside>
  );
};
