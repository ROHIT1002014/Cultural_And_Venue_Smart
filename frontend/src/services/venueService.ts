import api from "./api";
import { CrowdDensity, POI, RouteRequest, RouteResponse, Venue } from "@/types/venue";

export const venueService = {
  async getVenue(venueId: string): Promise<Venue> {
    const response = await api.get<Venue>(`/venues/${venueId}`);
    return response.data;
  },

  async listPOIs(venueId: string, category?: string, accessibleOnly?: boolean): Promise<POI[]> {
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (accessibleOnly) params.append("accessible_only", "true");
    const response = await api.get<POI[]>(`/venues/${venueId}/pois?${params.toString()}`);
    return response.data;
  },

  async calculateRoute(payload: RouteRequest): Promise<RouteResponse> {
    const response = await api.post<RouteResponse>(`/venues/${payload.venue_id}/routes`, payload);
    return response.data;
  },

  async getCrowdDensity(venueId: string): Promise<CrowdDensity[]> {
    const response = await api.get<CrowdDensity[]>(`/venues/${venueId}/crowd-density`);
    return response.data;
  },

  async triggerEmergencyAlert(venueId: string, alertType: string, severity: string = "HIGH"): Promise<any> {
    const response = await api.post(`/venues/${venueId}/alerts`, {
      venue_id: venueId,
      alert_type: alertType,
      severity,
      location: { zone: "Main Complex" },
    });
    return response.data;
  },
};
