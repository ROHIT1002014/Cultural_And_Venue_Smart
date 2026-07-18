import api from "./api";
import { LoginPayload, RegisterPayload, TokenResponse, User } from "@/types/auth";

export const authService = {
  async login(payload: LoginPayload): Promise<TokenResponse> {
    const formData = new URLSearchParams();
    formData.append("username", payload.username);
    formData.append("password", payload.password);

    const response = await api.post<TokenResponse>("/auth/login", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return response.data;
  },

  async register(payload: RegisterPayload): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>("/auth/register", payload);
    return response.data;
  },

  async getProfile(): Promise<User> {
    const response = await api.get<User>("/auth/me");
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await api.post("/auth/logout");
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
    }
  },
};
