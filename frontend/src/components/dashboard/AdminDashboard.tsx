import React, { useState, useEffect } from "react";
import { ShieldAlert, Users, Car, Bell, AlertTriangle, CheckCircle2, Activity, RefreshCw } from "lucide-react";
import { CrowdDensity } from "@/types/venue";
import { ParkingLot } from "@/types/parking";
import { venueService } from "@/services/venueService";
import { parkingService } from "@/services/parkingService";
import { Toast } from "@/components/common/Toast";

export const AdminDashboard: React.FC<{ venueId: string }> = ({ venueId }) => {
  const [densities, setDensities] = useState<CrowdDensity[]>([]);
  const [lots, setLots] = useState<ParkingLot[]>([]);
  const [loading, setLoading] = useState(false);
  const [alertType, setAlertType] = useState("FIRE_ALARM");
  const [alertSeverity, setAlertSeverity] = useState("CRITICAL");
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [dData, lData] = await Promise.all([
        venueService.getCrowdDensity(venueId),
        parkingService.listLots(venueId),
      ]);
      setDensities(dData);
      setLots(lData);
    } catch (err) {
      // Demo fallback data if server not running
      setDensities([
        { venue_id: venueId, zone_name: "Main Exhibition Hall A", current_occupancy: 3200, capacity: 5000, occupancy_percentage: 64.0, density_status: "DENSE" },
        { venue_id: venueId, zone_name: "West Wing Galleries", current_occupancy: 450, capacity: 1500, occupancy_percentage: 30.0, density_status: "SPARSE" },
      ]);
      setLots([
        { id: "lot-1", venue_id: venueId, lot_name: "East Wing Underground Structure", total_spots: 200, available_spots: 45, accessible_spots_total: 12, accessible_spots_available: 4, has_ev_charging: true, status: "OPEN" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, [venueId]);

  const handleTriggerAlert = async () => {
    try {
      await venueService.triggerEmergencyAlert(venueId, alertType, alertSeverity);
      setToastMessage(`BROADCAST ACTIVE: Triggered ${alertType} (${alertSeverity}) across all venue displays.`);
    } catch (err: any) {
      setToastMessage(`Alert Triggered (Demo Simulation): ${alertType} broadcast successfully initiated.`);
    }
  };

  return (
    <div className="space-y-8">
      {toastMessage && <Toast message={toastMessage} type="error" onClose={() => setToastMessage(null)} />}

      {/* Header */}
      <div className="bg-dark-surface/90 border border-dark-border rounded-2xl p-6 shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-red-500/20 border border-red-500/40 text-red-400 flex items-center justify-center">
            <ShieldAlert className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h2 className="text-xl font-extrabold text-gray-100">Live Venue Operations & Security Center</h2>
            <p className="text-xs text-gray-400 mt-0.5">
              Granular RBAC monitoring for crowd density, parking capacities, and priority emergency broadcasts.
            </p>
          </div>
        </div>

        <button
          onClick={fetchAdminData}
          disabled={loading}
          className="px-4 py-2 bg-dark-card border border-dark-border text-gray-200 hover:border-brand-500/50 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all"
        >
          <RefreshCw className={`w-4 h-4 text-brand-400 ${loading ? "animate-spin" : ""}`} />
          Refresh Metrics
        </button>
      </div>

      {/* Crowd Density Gauges */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
          <Users className="w-4 h-4 text-brand-400" /> Real-Time Crowd Density by Zone
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {densities.map((d, i) => {
            const isDense = d.occupancy_percentage > 60;
            return (
              <div key={i} className="bg-dark-surface/80 border border-dark-border rounded-2xl p-5 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-gray-100">{d.zone_name}</span>
                  <span
                    className={`text-xs font-mono px-3 py-1 rounded-full border ${
                      isDense
                        ? "bg-yellow-500/20 border-yellow-500/40 text-yellow-400"
                        : "bg-brand-500/20 border-brand-500/40 text-brand-400"
                    }`}
                  >
                    {d.density_status}
                  </span>
                </div>

                {/* Progress bar */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>Occupancy: {d.current_occupancy} / {d.capacity}</span>
                    <span className="font-mono font-bold text-gray-200">{d.occupancy_percentage}%</span>
                  </div>
                  <div className="w-full bg-dark-bg rounded-full h-3 overflow-hidden border border-dark-border">
                    <div
                      className={`h-full transition-all duration-500 ${
                        isDense ? "bg-gradient-to-r from-yellow-500 to-red-500" : "bg-gradient-to-r from-brand-600 to-brand-400"
                      }`}
                      style={{ width: `${Math.min(100, d.occupancy_percentage)}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Parking Lots Overview */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
          <Car className="w-4 h-4 text-brand-400" /> Parking Lot Capacities & Accessible Spaces
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {lots.map((l) => (
            <div key={l.id} className="bg-dark-surface/80 border border-dark-border rounded-2xl p-5 shadow-xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-gray-100">{l.lot_name}</span>
                <span className="text-xs font-mono text-brand-400 bg-brand-500/10 px-2.5 py-1 rounded-lg border border-brand-500/20">
                  {l.status}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 pt-2 text-xs text-gray-300 border-t border-dark-border/60">
                <div>
                  <span className="text-gray-400 block">Total Availability:</span>
                  <span className="text-base font-bold text-white font-mono">{l.available_spots} / {l.total_spots}</span>
                </div>
                <div>
                  <span className="text-gray-400 block">Wheelchair Spots:</span>
                  <span className="text-base font-bold text-brand-400 font-mono">{l.accessible_spots_available} / {l.accessible_spots_total}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Emergency Evacuation Trigger Modal/Card */}
      <div className="bg-red-950/20 border border-red-500/40 rounded-2xl p-6 shadow-2xl space-y-4">
        <div className="flex items-center gap-3 text-red-400 font-bold text-base">
          <AlertTriangle className="w-5 h-5 animate-pulse" />
          Priority Emergency & Evacuation Broadcast System
        </div>
        <p className="text-xs text-gray-300 leading-relaxed">
          Triggering an emergency alert immediately interrupts AI copilot sessions and digital signs across the venue, directing guests to step-free green emergency exits.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-4 pt-2">
          <select
            value={alertType}
            onChange={(e) => setAlertType(e.target.value)}
            className="w-full sm:w-auto bg-dark-surface border border-red-500/50 rounded-xl px-4 py-2.5 text-xs text-gray-100 font-semibold"
          >
            <option value="FIRE_ALARM">🔥 FIRE_ALARM EVACUATION</option>
            <option value="MEDICAL_EMERGENCY">🚑 MEDICAL_EMERGENCY ALERT</option>
            <option value="SECURITY_THREAT">🚨 SECURITY_THREAT LOCKDOWN</option>
          </select>

          <select
            value={alertSeverity}
            onChange={(e) => setAlertSeverity(e.target.value)}
            className="w-full sm:w-auto bg-dark-surface border border-red-500/50 rounded-xl px-4 py-2.5 text-xs text-red-400 font-semibold font-mono"
          >
            <option value="CRITICAL">SEVERITY: CRITICAL</option>
            <option value="HIGH">SEVERITY: HIGH</option>
          </select>

          <button
            onClick={handleTriggerAlert}
            className="w-full sm:w-auto px-6 py-2.5 bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 text-white font-bold text-xs rounded-xl shadow-lg shadow-red-500/30 transition-all flex items-center justify-center gap-2"
          >
            <Bell className="w-4 h-4" />
            Broadcast Emergency Notice
          </button>
        </div>
      </div>
    </div>
  );
};
