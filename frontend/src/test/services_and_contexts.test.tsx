import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

const { mockGet, mockPost, mockUseRequest, mockUseResponse } = vi.hoisted(() => {
  const reqCallbacks: any[] = [];
  const resCallbacks: any[] = [];
  return {
    mockGet: vi.fn(),
    mockPost: vi.fn(),
    mockUseRequest: vi.fn((success: any, error?: any) => {
      reqCallbacks.push({ success, error });
    }),
    mockUseResponse: vi.fn((success: any, error?: any) => {
      resCallbacks.push({ success, error });
    }),
    reqCallbacks,
    resCallbacks,
  };
});

vi.mock("axios", () => {
  const mockApi = (...args: any[]) => mockGet(...args);
  Object.assign(mockApi, {
    get: (...args: any[]) => mockGet(...args),
    post: (...args: any[]) => mockPost(...args),
    interceptors: {
      request: { use: (onFulfilled: any, onRejected?: any) => mockUseRequest(onFulfilled, onRejected) },
      response: { use: (onFulfilled: any, onRejected?: any) => mockUseResponse(onFulfilled, onRejected) },
    },
    defaults: { headers: { common: {} } },
  });
  return {
    default: {
      create: vi.fn(() => mockApi),
      post: (...args: any[]) => mockPost(...args),
      get: (...args: any[]) => mockGet(...args),
      ...mockApi,
    },
  };
});

// Contexts
import { AuthProvider, useAuth } from "@/context/AuthContext";
import { ThemeProvider, useTheme } from "@/context/ThemeContext";

// Services
import { assistantService } from "@/services/assistantService";
import { authService } from "@/services/authService";
import { parkingService } from "@/services/parkingService";
import { venueService } from "@/services/venueService";

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe("ThemeContext", () => {
  const ThemeConsumer = () => {
    const { theme, toggleTheme } = useTheme();
    return (
      <div>
        <span>Current: {theme}</span>
        <button onClick={toggleTheme}>Toggle</button>
      </div>
    );
  };

  it("provides default theme and toggles between dark and light", () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );
    expect(screen.getByText("Current: dark")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Toggle"));
    expect(screen.getByText("Current: light")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Toggle"));
    expect(screen.getByText("Current: dark")).toBeInTheDocument();
  });
});

describe("AuthContext & authService", () => {
  const AuthConsumer = () => {
    const { user, login, register, logout } = useAuth();
    return (
      <div>
        <span>{user ? `Logged in as ${user.full_name}` : "Status: Logged out"}</span>
        <button
          onClick={async () => {
            await login({ username: "test@example.com", password: "password" });
          }}
        >
          Do Login
        </button>
        <button
          onClick={async () => {
            await register({
              email: "new@example.com",
              password: "password",
              full_name: "New User",
              role: "USER",
            });
          }}
        >
          Do Register
        </button>
        <button onClick={logout}>Do Logout</button>
      </div>
    );
  };

  it("handles login, register, and logout flows", async () => {
    mockPost.mockImplementation((url: string) => {
      if (url.includes("/login")) {
        return Promise.resolve({
          data: {
            access_token: "tok-123",
            refresh_token: "ref-123",
            token_type: "bearer",
            user: { id: "u-1", email: "test@example.com", full_name: "Test User", role: "USER" },
          },
        });
      }
      if (url.includes("/register")) {
        return Promise.resolve({
          data: {
            access_token: "tok-456",
            refresh_token: "ref-456",
            token_type: "bearer",
            user: { id: "u-2", email: "new@example.com", full_name: "New User", role: "USER" },
          },
        });
      }
      if (url.includes("/logout")) {
        return Promise.resolve({ data: {} });
      }
      return Promise.reject(new Error("Unknown post: " + url));
    });

    mockGet.mockImplementation((url: string) => {
      if (url.includes("/me")) {
        return Promise.resolve({
          data: { id: "u-1", email: "test@example.com", full_name: "Test User", role: "USER" },
        });
      }
      return Promise.reject(new Error("Unknown get: " + url));
    });

    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>
    );

    fireEvent.click(screen.getByText("Do Login"));
    await waitFor(() => expect(screen.getByText("Logged in as Test User")).toBeInTheDocument());

    fireEvent.click(screen.getByText("Do Logout"));
    await waitFor(() => expect(screen.getByText("Status: Logged out")).toBeInTheDocument());

    fireEvent.click(screen.getByText("Do Register"));
    await waitFor(() => expect(screen.getByText("Logged in as New User")).toBeInTheDocument());
  });

  it("handles initAuth on mount when token exists", async () => {
    localStorage.setItem("access_token", "tok-123");
    mockGet.mockResolvedValueOnce({
      data: { id: "u-1", email: "test@example.com", full_name: "Init User", role: "USER" },
    });
    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>
    );
    await waitFor(() => expect(screen.getByText("Logged in as Init User")).toBeInTheDocument());
    localStorage.clear();
  });

  it("handles initAuth error and clears storage", async () => {
    localStorage.setItem("access_token", "invalid-tok");
    mockGet.mockRejectedValueOnce(new Error("Unauthorized"));
    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>
    );
    await waitFor(() => expect(screen.getByText("Status: Logged out")).toBeInTheDocument());
    localStorage.clear();
  });

  it("throws error when useAuth used outside provider", () => {
    const TestComp = () => {
      useAuth();
      return null;
    };
    expect(() => render(<TestComp />)).toThrow("useAuth must be used within an AuthProvider");
  });
});

describe("Services API Methods", () => {
  it("assistantService methods call appropriate endpoints", async () => {
    mockPost.mockResolvedValueOnce({ data: { message_id: "ai-1" } });
    const res = await assistantService.sendMessage({ message: "hello", venue_id: "v-1" });
    expect(res).toEqual({ message_id: "ai-1" });

    mockGet.mockResolvedValueOnce({ data: [{ session_id: "s-1" }] });
    const sessions = await assistantService.listSessions();
    expect(sessions).toEqual([{ session_id: "s-1" }]);

    mockPost.mockResolvedValueOnce({ data: [{ faq_id: "f-1" }] });
    const faqs = await assistantService.searchFAQ("v-1", "exit");
    expect(faqs).toEqual([{ faq_id: "f-1" }]);
  });

  it("venueService methods call appropriate endpoints", async () => {
    mockGet.mockResolvedValueOnce({ data: { id: "v-1" } });
    const venue = await venueService.getVenue("v-1");
    expect(venue).toEqual({ id: "v-1" });

    mockGet.mockResolvedValueOnce({ data: [{ id: "poi-1" }] });
    const pois = await venueService.listPOIs("v-1", "exit", true);
    expect(pois).toEqual([{ id: "poi-1" }]);

    mockPost.mockResolvedValueOnce({ data: { total_distance_meters: 10 } });
    const route = await venueService.calculateRoute({ venue_id: "v-1", origin_poi_id: "poi-1", destination_poi_id: "poi-2", require_accessible_route: true });
    expect(route).toEqual({ total_distance_meters: 10 });

    mockGet.mockResolvedValueOnce({ data: [{ venue_id: "v-1" }] });
    const crowd = await venueService.getCrowdDensity("v-1");
    expect(crowd).toEqual([{ venue_id: "v-1" }]);

    mockPost.mockResolvedValueOnce({ data: { success: true } });
    const alert = await venueService.triggerEmergencyAlert("v-1", "Fire", "HIGH");
    expect(alert).toEqual({ success: true });
  });

  it("parkingService methods call appropriate endpoints", async () => {
    mockGet.mockResolvedValueOnce({ data: [{ id: "lot-1" }] });
    const lots = await parkingService.listLots("v-1");
    expect(lots).toEqual([{ id: "lot-1" }]);

    mockPost.mockResolvedValueOnce({ data: { id: "res-1" } });
    const res = await parkingService.reserveSpot("lot-1", "PLATE-1", true, true);
    expect(res).toEqual({ id: "res-1" });
  });

  it("authService methods call endpoints directly", async () => {
    mockPost.mockResolvedValueOnce({ data: { access_token: "tok" } });
    await authService.login({ username: "a", password: "b" });

    mockPost.mockResolvedValueOnce({ data: { id: "u-1" } });
    await authService.register({ email: "a@b.com", password: "b", full_name: "A", role: "USER" });

    mockGet.mockResolvedValueOnce({ data: { id: "u-1" } });
    await authService.getProfile();

    mockPost.mockResolvedValueOnce({ data: {} });
    await authService.logout();
  });

  it("throws when useTheme is used outside provider", () => {
    const TestComp = () => {
      useTheme();
      return null;
    };
    expect(() => render(<TestComp />)).toThrow("useTheme must be used within a ThemeProvider");
  });
});
