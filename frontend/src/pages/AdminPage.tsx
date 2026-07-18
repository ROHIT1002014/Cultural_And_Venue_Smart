import React from "react";
import { AdminDashboard } from "@/components/dashboard/AdminDashboard";

export const AdminPage: React.FC<{ venueId: string }> = ({ venueId }) => {
  return (
    <div className="py-2">
      <AdminDashboard venueId={venueId} />
    </div>
  );
};
