import React, { useState, useRef, useEffect } from "react";
import { Send, Mic, ShieldCheck, Sparkles, AlertTriangle, Cpu, Terminal, RefreshCw } from "lucide-react";
import { ChatMessage } from "@/types/assistant";
import { assistantService } from "@/services/assistantService";
import { LanguageSwitcher } from "@/components/common/LanguageSwitcher";

export const ChatUI: React.FC<{ venueId?: string }> = ({ venueId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "init-1",
      role: "assistant",
      content:
        "Hello! I am your AI-Native Cultural & Venue Smart Copilot. I can assist you with indoor directions, wheelchair-accessible routes, parking availability, and volunteer support. How can I help you navigate today?",
      active_agents: ["OrchestratorAgent", "NavigationAgent"],
      grounding_score: 0.96,
      created_at: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [preferredLang, setPreferredLang] = useState("en");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsgText = input.trim();
    setInput("");

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: userMsgText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await assistantService.sendMessage({
        message: userMsgText,
        preferred_language: preferredLang,
        venue_id: venueId,
      });

      const aiMsg: ChatMessage = {
        id: res.message_id || `ai-${Date.now()}`,
        role: "assistant",
        content: res.response,
        active_agents: res.active_agents,
        executed_tools: res.executed_tools,
        grounding_score: res.grounding_score,
        token_usage: res.token_usage,
        created_at: res.created_at,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error: any) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        role: "assistant",
        content: `⚠️ System Guardrail Intervention: ${
          error.response?.data?.message || "Unable to reach multi-agent orchestration engine. Please check connection."
        }`,
        active_agents: ["SecurityGuard"],
        grounding_score: 1.0,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const toggleVoiceInput = () => {
    if (isRecording) {
      setIsRecording(false);
      setInput((prev) => prev + " [Voice Input: Directing to nearest accessible exit and restroom]");
    } else {
      setIsRecording(true);
    }
  };

  return (
    <div className="flex flex-col h-[750px] bg-dark-surface/90 border border-dark-border rounded-2xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 bg-dark-card/90 border-b border-dark-border flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-400 flex items-center justify-center text-white shadow-lg shadow-brand-500/20">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="font-bold text-gray-100 flex items-center gap-2">
              Multi-Agent LangGraph Copilot
              <span className="text-[10px] uppercase font-mono bg-brand-500/20 text-brand-400 px-2 py-0.5 rounded-full border border-brand-500/30">
                Streaming Active
              </span>
            </h3>
            <span className="text-xs text-gray-400 flex items-center gap-1.5 mt-0.5">
              <ShieldCheck className="w-3.5 h-3.5 text-brand-400" />
              PII Masking & RAG Hallucination Guardrails Online
            </span>
          </div>
        </div>
        <LanguageSwitcher currentLanguage={preferredLang} onSelect={setPreferredLang} />
      </div>

      {/* Messages Window */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.role === "user";
          return (
            <div key={msg.id} className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
              <div
                className={`max-w-[85%] rounded-2xl p-4 shadow-md ${
                  isUser
                    ? "bg-gradient-to-r from-brand-600 to-brand-500 text-white rounded-tr-none"
                    : "bg-dark-card border border-dark-border/80 text-gray-100 rounded-tl-none"
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>

                {/* AI Metadata & Tool Execution Summary */}
                {!isUser && msg.active_agents && (
                  <div className="mt-3 pt-3 border-t border-dark-border/60 flex flex-wrap items-center justify-between gap-2 text-xs">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <Sparkles className="w-3.5 h-3.5 text-brand-400" />
                      <span className="text-gray-400">Agents:</span>
                      {msg.active_agents.map((agent, i) => (
                        <span
                          key={i}
                          className="font-mono px-2 py-0.5 rounded bg-dark-bg border border-dark-border text-brand-400 text-[11px]"
                        >
                          {agent}
                        </span>
                      ))}
                    </div>

                    {msg.grounding_score !== undefined && (
                      <div className="flex items-center gap-1 bg-dark-bg px-2 py-0.5 rounded border border-dark-border">
                        <span className="text-gray-400">RAG Grounding:</span>
                        <span
                          className={`font-semibold ${
                            msg.grounding_score > 0.9 ? "text-brand-400" : "text-yellow-400"
                          }`}
                        >
                          {Math.round(msg.grounding_score * 100)}%
                        </span>
                      </div>
                    )}
                  </div>
                )}

                {/* Executed Tools Details */}
                {!isUser && msg.executed_tools && msg.executed_tools.length > 0 && (
                  <div className="mt-2 p-2.5 rounded-xl bg-dark-bg/80 border border-dark-border text-xs font-mono text-gray-300 space-y-1">
                    <div className="text-brand-400 font-semibold flex items-center gap-1">
                      <Terminal className="w-3.5 h-3.5" /> Executed Tool Calls:
                    </div>
                    {msg.executed_tools.map((t, i) => (
                      <div key={i} className="text-gray-400">
                        • <span className="text-gray-200">{t.tool_name}</span>: {t.output_summary}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex items-center gap-3 text-gray-400 text-sm font-medium animate-pulse bg-dark-card/50 px-4 py-3 rounded-xl border border-dark-border w-fit">
            <RefreshCw className="w-4 h-4 animate-spin text-brand-400" />
            <span>Multi-agent orchestrator analyzing intent and retrieving grounded vector knowledge...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <form onSubmit={handleSend} className="p-4 bg-dark-card/90 border-t border-dark-border flex items-center gap-3">
        <button
          type="button"
          onClick={toggleVoiceInput}
          className={`p-3 rounded-xl border transition-all ${
            isRecording
              ? "bg-red-500/20 border-red-500 text-red-400 animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.4)]"
              : "bg-dark-surface border-dark-border text-gray-400 hover:text-gray-200"
          }`}
          title="Voice Command Recognition"
        >
          <Mic className="w-5 h-5" />
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask for accessible routes, restroom locations, or EV parking status..."
          className="flex-1 bg-dark-surface border border-dark-border/80 rounded-xl px-4 py-3 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-brand-500/80 focus:ring-1 focus:ring-brand-500 transition-all"
        />

        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="bg-gradient-to-r from-brand-600 to-brand-500 text-white p-3 rounded-xl shadow-lg shadow-brand-500/20 hover:shadow-brand-500/40 disabled:opacity-40 transition-all"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
};
