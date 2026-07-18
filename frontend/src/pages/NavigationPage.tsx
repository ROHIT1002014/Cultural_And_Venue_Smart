import React from "react";
import { MapUI } from "@/components/map/MapUI";

export const NavigationPage: React.FC<{ venueId: string }> = ({ venueId }) => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-extrabold text-gray-100">Full Screen Interactive Wayfinding Map</h2>
        <p className="text-xs text-gray-400 mt-1">
          Navigate floors, restrooms, emergency exits, and exhibits with certified step-free route guidance.
        </p>
      </div>
      <MapUI venueId={venueId} />
    </div>
  );
};
