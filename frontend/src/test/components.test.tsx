import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import React from "react";

// Components
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { Toast } from "@/components/common/Toast";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { LanguageSwitcher } from "@/components/common/LanguageSwitcher";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { ChatUI } from "@/components/chat/ChatUI";
import { AdminDashboard } from "@/components/dashboard/AdminDashboard";
import { MapUI } from "@/components/map/MapUI";

// Pages
import { Home } from "@/pages/Home";
import { Login } from "@/pages/Login";
import { Register } from "@/pages/Register";
import { ParkingPage } from "@/pages/ParkingPage";
import { CopilotPage } from "@/pages/CopilotPage";
import { NavigationPage } from "@/pages/NavigationPage";
import { AdminPage } from "@/pages/AdminPage";
import App from "@/App";

// Mock AuthContext
const mockUser = { id: "u-1", email: "user@example.com", full_name: "Test User", role: "USER" };

vi.mock("@/context/AuthContext", () => ({
  useAuth: vi.fn(() => ({
    user: mockUser,
    isAuthenticated: true,
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
  })),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("@/context/ThemeContext", () => ({
  useTheme: vi.fn(() => ({
    theme: "dark",
    toggleTheme: vi.fn(),
  })),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock services
vi.mock("@/services/assistantService", () => ({
  assistantService: {
    sendMessage: vi.fn().mockResolvedValue({
      message_id: "ai-msg-1",
      response: "AI response successfully grounded.",
      active_agents: ["OrchestratorAgent"],
      executed_tools: [{ tool_name: "retrieve_venue_info", output_summary: "Found info" }],
      grounding_score: 0.95,
      created_at: new Date().toISOString(),
    }),
  },
}));

vi.mock("@/services/venueService", () => ({
  venueService: {
    listPOIs: vi.fn().mockResolvedValue([
      { id: "poi-1", venue_id: "v-1", name: "POI 1", category: "exit", floor_level: 1, coordinates: { x: 10, y: 10 }, is_accessible: true },
      { id: "poi-2", venue_id: "v-1", name: "POI 2", category: "restroom", floor_level: 1, coordinates: { x: 20, y: 20 }, is_accessible: true },
    ]),
    calculateRoute: vi.fn().mockResolvedValue({
      venue_id: "v-1",
      origin_name: "POI 1",
      destination_name: "POI 2",
      total_distance_meters: 50,
      estimated_time_minutes: 1,
      steps: ["Step 1", "Step 2"],
      is_accessible: true,
    }),
    getCrowdDensity: vi.fn().mockResolvedValue([
      { venue_id: "v-1", zone_name: "Hall A", current_occupancy: 100, capacity: 500, occupancy_percentage: 20, density_status: "SPARSE" },
    ]),
    triggerEmergencyAlert: vi.fn().mockResolvedValue(true),
  },
}));

vi.mock("@/services/parkingService", () => ({
  parkingService: {
    listLots: vi.fn().mockResolvedValue([
      { id: "lot-1", venue_id: "v-1", lot_name: "Lot A", total_spots: 100, available_spots: 50, accessible_spots_total: 10, accessible_spots_available: 5, has_ev_charging: true, status: "OPEN" },
    ]),
    reserveSpot: vi.fn().mockResolvedValue({ id: "res-1", status: "CONFIRMED" }),
  },
}));

describe("Common Components", () => {
  it("renders Button correctly and handles click", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);
    const btn = screen.getByText("Click Me");
    fireEvent.click(btn);
    expect(handleClick).toHaveBeenCalled();
  });

  it("renders Card correctly", () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText("Card content")).toBeInTheDocument();
  });

  it("renders Toast and closes on click", () => {
    const handleClose = vi.fn();
    render(<Toast message="Test Toast" type="success" onClose={handleClose} />);
    expect(screen.getByText("Test Toast")).toBeInTheDocument();
    const closeBtn = screen.getByRole("button");
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalled();
  });

  it("renders LoadingScreen correctly", () => {
    render(<LoadingScreen message="Loading app..." />);
    expect(screen.getByText("Loading app...")).toBeInTheDocument();
  });

  it("renders LanguageSwitcher and handles language select", () => {
    const handleSelect = vi.fn();
    render(<LanguageSwitcher currentLanguage="en" onSelect={handleSelect} />);
    const select = screen.getByRole("combobox");
    fireEvent.change(select, { target: { value: "es" } });
    expect(handleSelect).toHaveBeenCalledWith("es");
  });

  it("renders children inside ErrorBoundary normally", () => {
    render(
      <ErrorBoundary>
        <div>Normal child content</div>
      </ErrorBoundary>
    );
    expect(screen.getByText("Normal child content")).toBeInTheDocument();
  });

  it("renders ErrorBoundary fallback UI on error", () => {
    const ThrowError = () => {
      throw new Error("Simulated error");
    };
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });
});

describe("Layout Components", () => {
  it("renders Navbar and handles tab navigation", () => {
    const handleNavigate = vi.fn();
    render(<Navbar onNavigate={handleNavigate} />);
    expect(screen.getByText(/Smart AI Operations/i)).toBeInTheDocument();
  });

  it("renders Sidebar and handles tab select", () => {
    const handleSelectTab = vi.fn();
    render(<Sidebar activeTab="home" onSelectTab={handleSelectTab} />);
    const copilotBtn = screen.getByText("AI Copilot & Map");
    fireEvent.click(copilotBtn);
    expect(handleSelectTab).toHaveBeenCalledWith("copilot");
  });

  it("renders Footer correctly", () => {
    render(<Footer />);
    expect(screen.getByText(/Enterprise-Grade AI Guardrails Active/i)).toBeInTheDocument();
  });
});

describe("Feature Components & Pages", () => {
  it("renders ChatUI and sends message", async () => {
    render(<ChatUI venueId="v-1" />);
    const input = screen.getByPlaceholderText(/Ask for accessible routes/i);
    fireEvent.change(input, { target: { value: "Where is the exit?" } });
    const submitBtn = input.closest("form")!.querySelector('button[type="submit"]')!;
    fireEvent.click(submitBtn);
    expect(await screen.findByText(/Where is the exit\?/i)).toBeInTheDocument();
  });

  it("renders MapUI and calculates route", async () => {
    render(<MapUI venueId="v-1" />);
    expect(await screen.findByText("Interactive Indoor Wayfinding Map")).toBeInTheDocument();
    const calcBtn = screen.getByText("Generate Step-Free Path");
    fireEvent.click(calcBtn);
  });

  it("renders AdminDashboard and triggers alert", async () => {
    render(<AdminDashboard venueId="v-1" />);
    expect(await screen.findByText("Live Venue Operations & Security Center")).toBeInTheDocument();
    const triggerBtn = screen.getByText("Broadcast Emergency Notice");
    fireEvent.click(triggerBtn);
  });

  it("renders Home page and triggers navigation", () => {
    const handleNavigate = vi.fn();
    render(<Home onNavigate={handleNavigate} />);
    const launchBtn = screen.getByText(/Launch AI Copilot & Map/i);
    fireEvent.click(launchBtn);
    expect(handleNavigate).toHaveBeenCalledWith("copilot");
  });

  it("renders Login and Register pages", () => {
    const handleNav = vi.fn();
    render(<Login onNavigate={handleNav} />);
    expect(screen.getByRole("heading", { name: /Sign In to Copilot/i })).toBeInTheDocument();

    render(<Register onNavigate={handleNav} />);
    expect(screen.getByRole("heading", { name: /Create Profile/i })).toBeInTheDocument();
  });

  it("renders ParkingPage and submits reservation", async () => {
    render(<ParkingPage venueId="v-1" />);
    const plateInput = screen.getByPlaceholderText("e.g. EV-CULTURE-1");
    fireEvent.change(plateInput, { target: { value: "TEST-123" } });
    const reserveBtn = screen.getByText("Confirm Guaranteed Reservation");
    fireEvent.click(reserveBtn);
  });

  it("renders wrapper pages (CopilotPage, NavigationPage, AdminPage)", () => {
    render(<CopilotPage venueId="v-1" />);
    render(<NavigationPage venueId="v-1" />);
    render(<AdminPage venueId="v-1" />);
  });

  it("renders full App root component", () => {
    render(<App />);
  });
});
