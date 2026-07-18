export interface ExecutedTool {
  agent_name: string;
  tool_name: string;
  arguments: Record<string, any>;
  output_summary: string;
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  active_agents?: string[];
  executed_tools?: ExecutedTool[];
  grounding_score?: number;
  token_usage?: TokenUsage;
  created_at?: string;
}

export interface ChatRequest {
  session_id?: string;
  message: string;
  preferred_language?: string;
  venue_id?: string;
}

export interface ChatResponse {
  session_id: string;
  message_id: string;
  response: string;
  active_agents: string[];
  executed_tools: ExecutedTool[];
  grounding_score: number;
  token_usage: TokenUsage;
  created_at: string;
}

export interface SessionSummary {
  id: string;
  user_id: string;
  title: string;
  last_active_at: string;
  created_at: string;
}
