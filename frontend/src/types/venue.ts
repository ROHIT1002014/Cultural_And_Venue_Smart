export interface Venue {
  id: string;
  name: string;
  address: string;
  boundary_coordinates: Record<string, any>;
  total_capacity: number;
  current_occupancy: number;
  created_at: string;
  updated_at: string;
}

export interface POI {
  id: string;
  venue_id: string;
  name: string;
  category: "restroom" | "exit" | "food" | "seating" | "exhibit" | "elevator" | string;
  coordinates: Record<string, any>;
  floor_level: number;
  is_accessible: boolean;
}

export interface RouteRequest {
  venue_id: string;
  origin_poi_id: string;
  destination_poi_id: string;
  require_accessible_route?: boolean;
}

export interface RouteResponse {
  venue_id: string;
  origin_name: string;
  destination_name: string;
  total_distance_meters: number;
  estimated_time_minutes: number;
  steps: string[];
  is_accessible: boolean;
}

export interface CrowdDensity {
  venue_id: string;
  zone_name: string;
  current_occupancy: number;
  capacity: number;
  occupancy_percentage: number;
  density_status: "SPARSE" | "MODERATE" | "DENSE" | "OVERCROWDED";
}
