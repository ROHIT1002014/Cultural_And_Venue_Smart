import React, { useState } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { Home } from "@/pages/Home";
import { CopilotPage } from "@/pages/CopilotPage";
import { NavigationPage } from "@/pages/NavigationPage";
import { ParkingPage } from "@/pages/ParkingPage";
import { AdminPage } from "@/pages/AdminPage";
import { Login } from "@/pages/Login";
import { Register } from "@/pages/Register";

// Default venue ID for standalone testing and initialization
const DEFAULT_VENUE_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("home");

  const renderContent = () => {
    switch (activeTab) {
      case "home":
        return <Home onNavigate={setActiveTab} />;
      case "copilot":
        return <CopilotPage venueId={DEFAULT_VENUE_ID} />;
      case "navigation":
        return <NavigationPage venueId={DEFAULT_VENUE_ID} />;
      case "parking":
        return <ParkingPage venueId={DEFAULT_VENUE_ID} />;
      case "admin":
        return <AdminPage venueId={DEFAULT_VENUE_ID} />;
      case "login":
        return <Login onNavigate={setActiveTab} />;
      case "register":
        return <Register onNavigate={setActiveTab} />;
      default:
        return <Home onNavigate={setActiveTab} />;
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg flex flex-col justify-between text-gray-100 font-sans">
      <Navbar onNavigate={setActiveTab} />
      <div className="flex-1 flex">
        <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} />
        <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full overflow-y-auto">
          {renderContent()}
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default App;
