import React from "react";
import { Sparkles, Navigation, ShieldCheck, Cpu, ArrowRight, Layers, Car, Globe, Heart } from "lucide-react";

export const Home: React.FC<{ onNavigate: (path: string) => void }> = ({ onNavigate }) => {
  return (
    <div className="space-y-16 py-6">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-dark-surface via-dark-card to-dark-bg border border-dark-border p-8 md:p-14 shadow-2xl">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-400 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 animate-pulse" /> AI-Native Multi-Agent Operations Engine
          </div>

          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight text-gray-100">
            Smart Copilot for <br />
            <span className="bg-gradient-to-r from-brand-400 via-brand-500 to-emerald-400 bg-clip-text text-transparent">
              Cultural & Museum Venues
            </span>
          </h1>

          <p className="text-gray-300 text-base md:text-lg leading-relaxed">
            Experience step-free indoor wayfinding, real-time crowd density analytics, accessible EV parking reservations, and multilingual natural language assistance powered by a DDD-compliant multi-agent LangGraph system.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-4">
            <button
              onClick={() => onNavigate("copilot")}
              className="bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-bold px-6 py-3.5 rounded-2xl shadow-xl shadow-brand-500/25 flex items-center gap-2 transition-all hover:scale-[1.02]"
            >
              Launch AI Copilot & Map
              <ArrowRight className="w-5 h-5" />
            </button>

            <button
              onClick={() => onNavigate("navigation")}
              className="bg-dark-card/90 border border-dark-border hover:border-gray-500 text-gray-200 font-semibold px-6 py-3.5 rounded-2xl transition-all flex items-center gap-2"
            >
              Explore Interactive Map
            </button>
          </div>
        </div>
      </div>

      {/* Feature Highlight Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-dark-surface/80 border border-dark-border rounded-2xl p-6 shadow-xl space-y-4 hover:border-brand-500/50 transition-all">
          <div className="w-12 h-12 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center">
            <Cpu className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-gray-100">LangGraph Multi-Agent RAG</h3>
          <p className="text-sm text-gray-400 leading-relaxed">
            Orchestrator, Navigation, Parking, and Emergency sub-agents coordinate with hybrid vector search, PII detection, and strict hallucination guardrails.
          </p>
        </div>

        <div className="bg-dark-surface/80 border border-dark-border rounded-2xl p-6 shadow-xl space-y-4 hover:border-brand-500/50 transition-all">
          <div className="w-12 h-12 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center">
            <Navigation className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-gray-100">Step-Free Wayfinding</h3>
          <p className="text-sm text-gray-400 leading-relaxed">
            Certified wheelchair-accessible routing avoiding staircases and narrow galleries, dynamically selecting elevators and ramps in real time.
          </p>
        </div>

        <div className="bg-dark-surface/80 border border-dark-border rounded-2xl p-6 shadow-xl space-y-4 hover:border-brand-500/50 transition-all">
          <div className="w-12 h-12 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-gray-100">Enterprise Security & RBAC</h3>
          <p className="text-sm text-gray-400 leading-relaxed">
            Hardened with JWT token rotation, Redis blacklisting, PromptGuard jailbreak defense, SlowAPI rate limits, and OWASP-compliant secret entropy.
          </p>
        </div>
      </div>
    </div>
  );
};
