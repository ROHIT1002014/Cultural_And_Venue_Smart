export interface ParkingLot {
  id: string;
  venue_id: string;
  lot_name: string;
  total_spots: number;
  available_spots: number;
  accessible_spots_total: number;
  accessible_spots_available: number;
  has_ev_charging: boolean;
  status: "OPEN" | "FULL" | "MAINTENANCE";
}

export interface ParkingReservation {
  id: string;
  lot_id: string;
  user_id: string;
  vehicle_license: string;
  check_in_time: string;
  status: string;
}
