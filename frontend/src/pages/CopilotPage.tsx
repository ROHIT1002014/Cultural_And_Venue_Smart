import React from "react";
import { ChatUI } from "@/components/chat/ChatUI";
import { MapUI } from "@/components/map/MapUI";

export const CopilotPage: React.FC<{ venueId: string }> = ({ venueId }) => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-extrabold text-gray-100">AI Copilot & Interactive Wayfinding</h2>
        <p className="text-xs text-gray-400 mt-1">
          Chat in natural language or interact directly with the step-free floor map below. Both systems share live context.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <div className="lg:col-span-5">
          <ChatUI venueId={venueId} />
        </div>
        <div className="lg:col-span-7">
          <MapUI venueId={venueId} />
        </div>
      </div>
    </div>
  );
};
