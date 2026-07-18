import api from "./api";
import { ChatRequest, ChatResponse, SessionSummary } from "@/types/assistant";

export const assistantService = {
  async sendMessage(payload: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>("/assistant/chat", payload);
    return response.data;
  },

  async listSessions(): Promise<SessionSummary[]> {
    const response = await api.get<SessionSummary[]>("/assistant/sessions");
    return response.data;
  },

  async searchFAQ(venueId: string, query: string): Promise<any> {
    const response = await api.post("/assistant/faq/search", {
      venue_id: venueId,
      query,
      limit: 5,
    });
    return response.data;
  },
};
