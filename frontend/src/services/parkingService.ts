import api from "./api";
import { ParkingLot, ParkingReservation } from "@/types/parking";

export const parkingService = {
  async listLots(venueId: string): Promise<ParkingLot[]> {
    const response = await api.get<ParkingLot[]>(`/parking/lots/${venueId}`);
    return response.data;
  },

  async reserveSpot(lotId: string, license: string, accessible: boolean, ev: boolean): Promise<ParkingReservation> {
    const response = await api.post<ParkingReservation>("/parking/reserve", {
      lot_id: lotId,
      vehicle_license: license,
      requires_accessible_spot: accessible,
      requires_ev_charger: ev,
    });
    return response.data;
  },
};
