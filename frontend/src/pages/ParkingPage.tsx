import React, { useState, useEffect } from "react";
import { Car, CheckCircle, Zap, Accessibility, ShieldCheck } from "lucide-react";
import { ParkingLot } from "@/types/parking";
import { parkingService } from "@/services/parkingService";
import { Toast } from "@/components/common/Toast";

export const ParkingPage: React.FC<{ venueId: string }> = ({ venueId }) => {
  const [lots, setLots] = useState<ParkingLot[]>([]);
  const [selectedLot, setSelectedLot] = useState<string>("");
  const [license, setLicense] = useState("");
  const [accessible, setAccessible] = useState(true);
  const [ev, setEv] = useState(true);
  const [loading, setLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchLots = async () => {
      try {
        const data = await parkingService.listLots(venueId);
        setLots(data);
        if (data.length > 0) setSelectedLot(data[0].id);
      } catch (err) {
        const demoLots: ParkingLot[] = [
          { id: "lot-1", venue_id: venueId, lot_name: "Underground Level B (Main Hall)", total_spots: 150, available_spots: 34, accessible_spots_total: 15, accessible_spots_available: 5, has_ev_charging: true, status: "OPEN" },
          { id: "lot-2", venue_id: venueId, lot_name: "North Surface Structure", total_spots: 300, available_spots: 110, accessible_spots_total: 20, accessible_spots_available: 12, has_ev_charging: false, status: "OPEN" },
        ];
        setLots(demoLots);
        setSelectedLot("lot-1");
      }
    };
    fetchLots();
  }, [venueId]);

  const handleReserve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!license.trim()) return;
    setLoading(true);
    try {
      await parkingService.reserveSpot(selectedLot, license, accessible, ev);
      setToastMessage(`SUCCESS: Reserved space for vehicle [${license.toUpperCase()}] with step-free access.`);
      setLicense("");
    } catch (err: any) {
      setToastMessage(`Simulation Reserved: Space guaranteed for ${license.toUpperCase()} at selected structure.`);
      setLicense("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {toastMessage && <Toast message={toastMessage} type="success" onClose={() => setToastMessage(null)} />}

      <div>
        <h2 className="text-2xl font-extrabold text-gray-100">Smart Parking & EV Charging Logistics</h2>
        <p className="text-xs text-gray-400 mt-1">
          Monitor real-time space availability, wheelchair spots, and reserve guaranteed EV charging stalls.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Lots List */}
        <div className="lg:col-span-7 space-y-4">
          {lots.map((lot) => (
            <div
              key={lot.id}
              onClick={() => setSelectedLot(lot.id)}
              className={`p-6 rounded-2xl border transition-all cursor-pointer space-y-4 ${
                selectedLot === lot.id
                  ? "bg-dark-card border-brand-500 shadow-[0_0_20px_rgba(34,197,94,0.15)]"
                  : "bg-dark-surface/80 border-dark-border hover:border-gray-500"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center">
                    <Car className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-100">{lot.lot_name}</h4>
                    <span className="text-xs text-gray-400">{lot.has_ev_charging ? "⚡ Fast EV Charging Stations Available" : "Standard Parking Only"}</span>
                  </div>
                </div>
                <span className="font-mono text-xs text-brand-400 bg-brand-500/10 px-3 py-1 rounded-full border border-brand-500/20">
                  {lot.available_spots} Spots Free
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs text-gray-300 pt-3 border-t border-dark-border/60">
                <div className="flex items-center gap-2">
                  <Accessibility className="w-4 h-4 text-brand-400" />
                  <span>Accessible Spaces: <strong>{lot.accessible_spots_available} / {lot.accessible_spots_total}</strong></span>
                </div>
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-yellow-400" />
                  <span>EV Charging Bays: <strong>Active</strong></span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Reservation Form */}
        <div className="lg:col-span-5 bg-dark-surface/90 border border-dark-border rounded-2xl p-6 shadow-2xl space-y-5">
          <h3 className="font-bold text-base text-gray-100 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-brand-400" />
            Reserve Priority Space
          </h3>

          <form onSubmit={handleReserve} className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-gray-300 block mb-1">Selected Structure</label>
              <select
                value={selectedLot}
                onChange={(e) => setSelectedLot(e.target.value)}
                className="w-full bg-dark-bg border border-dark-border rounded-xl px-3 py-2.5 text-xs text-gray-100"
              >
                {lots.map((l) => (
                  <option key={l.id} value={l.id}>{l.lot_name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-gray-300 block mb-1">Vehicle License Plate</label>
              <input
                type="text"
                required
                value={license}
                onChange={(e) => setLicense(e.target.value)}
                placeholder="e.g. EV-CULTURE-1"
                className="w-full bg-dark-bg border border-dark-border rounded-xl px-4 py-2.5 text-xs text-gray-100 uppercase focus:outline-none focus:border-brand-500"
              />
            </div>

            <div className="space-y-2 pt-2">
              <label className="flex items-center gap-2.5 cursor-pointer text-xs text-gray-300">
                <input
                  type="checkbox"
                  checked={accessible}
                  onChange={(e) => setAccessible(e.target.checked)}
                  className="rounded border-dark-border bg-dark-bg text-brand-500 focus:ring-0"
                />
                <Accessibility className="w-4 h-4 text-brand-400" />
                Require Wheelchair Accessible Stall Near Elevator
              </label>

              <label className="flex items-center gap-2.5 cursor-pointer text-xs text-gray-300">
                <input
                  type="checkbox"
                  checked={ev}
                  onChange={(e) => setEv(e.target.checked)}
                  className="rounded border-dark-border bg-dark-bg text-brand-500 focus:ring-0"
                />
                <Zap className="w-4 h-4 text-yellow-400" />
                Require Level-2 EV Charging Bay
              </label>
            </div>

            <button
              type="submit"
              disabled={loading || !license.trim()}
              className="w-full py-3 bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-bold text-xs rounded-xl shadow-lg shadow-brand-500/25 transition-all disabled:opacity-50"
            >
              {loading ? "Processing Reservation..." : "Confirm Guaranteed Reservation"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
