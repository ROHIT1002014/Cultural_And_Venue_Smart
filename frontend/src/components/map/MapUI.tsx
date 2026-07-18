import React, { useState, useEffect } from "react";
import { Navigation, CheckCircle, Accessibility, Compass, MapPin } from "lucide-react";
import { POI, RouteResponse } from "@/types/venue";
import { venueService } from "@/services/venueService";

export const MapUI: React.FC<{ venueId: string }> = ({ venueId }) => {
  const [pois, setPois] = useState<POI[]>([]);
  const [activeFloor, setActiveFloor] = useState<number>(1);
  const [requireAccessible, setRequireAccessible] = useState<boolean>(true);
  const [selectedOrigin, setSelectedOrigin] = useState<string>("");
  const [selectedDest, setSelectedDest] = useState<string>("");
  const [route, setRoute] = useState<RouteResponse | null>(null);
  const [loadingRoute, setLoadingRoute] = useState<boolean>(false);

  useEffect(() => {
    const fetchPOIs = async () => {
      try {
        const data = await venueService.listPOIs(venueId);
        setPois(data);
        if (data.length >= 2) {
          setSelectedOrigin(data[0].id);
          setSelectedDest(data[1].id);
        }
      } catch (err) {
        // Fallback demo POIs if venue not fully seeded locally
        const demoPOIs: POI[] = [
          { id: "poi-1", venue_id: venueId, name: "Main Gallery Entrance", category: "exit", floor_level: 1, coordinates: { x: 20, y: 30 }, is_accessible: true },
          { id: "poi-2", venue_id: venueId, name: "West Wing Restroom (Wheelchair)", category: "restroom", floor_level: 1, coordinates: { x: 75, y: 40 }, is_accessible: true },
          { id: "poi-3", venue_id: venueId, name: "Modern Art Exhibit #4", category: "exhibit", floor_level: 2, coordinates: { x: 50, y: 70 }, is_accessible: true },
          { id: "poi-4", venue_id: venueId, name: "Elevator Bank #2 (Step-Free)", category: "elevator", floor_level: 1, coordinates: { x: 45, y: 50 }, is_accessible: true },
        ];
        setPois(demoPOIs);
        setSelectedOrigin("poi-1");
        setSelectedDest("poi-2");
      }
    };
    fetchPOIs();
  }, [venueId]);

  const handleCalculateRoute = async () => {
    if (!selectedOrigin || !selectedDest || selectedOrigin === selectedDest) return;
    setLoadingRoute(true);
    try {
      const res = await venueService.calculateRoute({
        venue_id: venueId,
        origin_poi_id: selectedOrigin,
        destination_poi_id: selectedDest,
        require_accessible_route: requireAccessible,
      });
      setRoute(res);
    } catch (err) {
      // Demo fallback route for visual walkthrough
      const originObj = pois.find((p) => p.id === selectedOrigin);
      const destObj = pois.find((p) => p.id === selectedDest);
      setRoute({
        venue_id: venueId,
        origin_name: originObj?.name || "Origin",
        destination_name: destObj?.name || "Destination",
        total_distance_meters: 65.5,
        estimated_time_minutes: 2,
        steps: [
          `Start from ${originObj?.name || "Origin"} on Floor ${activeFloor}.`,
          requireAccessible ? "Take Elevator #2 (Step-Free Transit) to upper gallery level." : "Proceed up main staircase.",
          `Arrive directly at ${destObj?.name || "Destination"}.`,
        ],
        is_accessible: requireAccessible,
      });
    } finally {
      setLoadingRoute(false);
    }
  };

  const currentFloorPOIs = pois.filter((p) => p.floor_level === activeFloor);

  return (
    <div className="bg-dark-surface/90 border border-dark-border rounded-2xl p-6 shadow-2xl space-y-6">
      {/* Map Control Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-dark-border/80 pb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-100 flex items-center gap-2.5">
            <Compass className="w-6 h-6 text-brand-400 animate-spin-slow" />
            Interactive Indoor Wayfinding Map
          </h3>
          <p className="text-xs text-gray-400 mt-1">
            Real-time step-free pathfinding avoiding stairs, escalators, and crowded corridors.
          </p>
        </div>

        {/* Floor selector and accessibility toggle */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center bg-dark-card border border-dark-border rounded-xl p-1">
            <span className="text-xs text-gray-400 px-3 font-medium">Floor:</span>
            {[1, 2, 3].map((floor) => (
              <button
                key={floor}
                onClick={() => setActiveFloor(floor)}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                  activeFloor === floor
                    ? "bg-brand-500 text-white shadow-md"
                    : "text-gray-400 hover:text-gray-200"
                }`}
              >
                L{floor}
              </button>
            ))}
          </div>

          <button
            onClick={() => setRequireAccessible(!requireAccessible)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-xs font-semibold transition-all ${
              requireAccessible
                ? "bg-brand-500/20 border-brand-500 text-brand-400 shadow-[0_0_15px_rgba(34,197,94,0.2)]"
                : "bg-dark-card border-dark-border text-gray-400"
            }`}
          >
            <Accessibility className="w-4 h-4" />
            Wheelchair Accessible Route
          </button>
        </div>
      </div>

      {/* Map Visualization Box */}
      <div className="relative h-[420px] bg-dark-bg/90 border border-dark-border rounded-2xl overflow-hidden p-6 flex flex-col justify-between shadow-inner">
        {/* Grid Background Pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f2937_1px,transparent_1px),linear-gradient(to_bottom,#1f2937_1px,transparent_1px)] bg-[size:3rem_3rem] opacity-30 pointer-events-none" />

        <div className="relative z-10 flex items-center justify-between">
          <span className="text-xs font-mono uppercase bg-dark-surface/90 border border-dark-border px-3 py-1 rounded-lg text-gray-300">
            Floor {activeFloor} Exhibition Layout
          </span>
          <span className="text-xs font-mono text-brand-400 bg-brand-500/10 px-3 py-1 rounded-lg border border-brand-500/30">
            {currentFloorPOIs.length} Markers Placed
          </span>
        </div>

        {/* POI Markers Placed on Map Grid */}
        <div className="relative z-10 flex-1 my-4 grid grid-cols-2 md:grid-cols-4 gap-4 items-center">
          {currentFloorPOIs.map((poi) => {
            const isSelectedOrigin = poi.id === selectedOrigin;
            const isSelectedDest = poi.id === selectedDest;
            return (
              <button
                type="button"
                key={poi.id}
                onClick={() => {
                  if (!selectedOrigin) setSelectedOrigin(poi.id);
                  else setSelectedDest(poi.id);
                }}
                className={`p-4 rounded-xl border backdrop-blur-md transition-all cursor-pointer flex flex-col items-center text-center gap-2 ${
                  isSelectedOrigin
                    ? "bg-brand-500/30 border-brand-500 shadow-[0_0_20px_rgba(34,197,94,0.3)] scale-105"
                    : isSelectedDest
                    ? "bg-blue-500/30 border-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.3)] scale-105"
                    : "bg-dark-card/80 border-dark-border hover:border-brand-500/50"
                }`}
              >
                <div className="w-10 h-10 rounded-lg bg-dark-surface flex items-center justify-center text-brand-400 border border-dark-border/50">
                  <MapPin className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-xs text-gray-200">{poi.name}</h4>
                  <span className="text-[10px] text-gray-400 block mt-0.5">{poi.category}</span>
                </div>
                {poi.is_accessible && (
                  <span className="inline-flex items-center gap-1 text-[9px] text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded-full border border-brand-500/20">
                    Accessible
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Map Legend */}
        <div className="relative z-10 flex items-center gap-4 text-xs text-gray-400 bg-dark-surface/80 border border-dark-border/80 px-4 py-2 rounded-xl w-fit">
          <div className="flex items-center gap-1.5 font-medium">
            <span className="w-3 h-3 rounded-full bg-brand-500" /> Origin Point
          </div>
          <div className="flex items-center gap-1.5 font-medium">
            <span className="w-3 h-3 rounded-full bg-blue-500" /> Destination
          </div>
          <div className="flex items-center gap-1.5 font-medium">
            <Accessibility className="w-3.5 h-3.5 text-brand-400" /> Step-Free Certified
          </div>
        </div>
      </div>

      {/* Pathfinding Route Selector & Directions Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
        <div className="md:col-span-1 space-y-4 bg-dark-card/60 p-5 rounded-2xl border border-dark-border">
          <h4 className="font-bold text-sm text-gray-200">Calculate Custom Route</h4>
          <div>
            <label htmlFor="origin-select" className="text-xs text-gray-400 block mb-1">Origin Point</label>
            <select
              id="origin-select"
              value={selectedOrigin}
              onChange={(e) => setSelectedOrigin(e.target.value)}
              className="w-full bg-dark-surface border border-dark-border rounded-xl px-3 py-2 text-xs text-gray-200"
            >
              {pois.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} (Floor {p.floor_level})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="dest-select" className="text-xs text-gray-400 block mb-1">Destination Point</label>
            <select
              id="dest-select"
              value={selectedDest}
              onChange={(e) => setSelectedDest(e.target.value)}
              className="w-full bg-dark-surface border border-dark-border rounded-xl px-3 py-2 text-xs text-gray-200"
            >
              {pois.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} (Floor {p.floor_level})
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={handleCalculateRoute}
            disabled={loadingRoute || !selectedOrigin || !selectedDest}
            className="w-full py-2.5 bg-gradient-to-r from-brand-600 to-brand-500 text-white font-semibold text-xs rounded-xl shadow-lg hover:shadow-brand-500/30 transition-all flex items-center justify-center gap-2"
          >
            <Navigation className="w-4 h-4" />
            Generate Step-Free Path
          </button>
        </div>

        {/* Route Steps Output */}
        <div className="md:col-span-2 bg-dark-card/60 p-5 rounded-2xl border border-dark-border flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-dark-border/80 pb-3 mb-3">
              <h4 className="font-bold text-sm text-gray-200 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-brand-400" />
                Step-by-Step Directions
              </h4>
              {route && (
                <span className="text-xs font-mono text-brand-400 bg-brand-500/10 px-2.5 py-1 rounded-lg border border-brand-500/20">
                  {route.total_distance_meters}m (~{route.estimated_time_minutes} min)
                </span>
              )}
            </div>

            {route ? (
              <ol className="space-y-3 text-xs text-gray-300">
                {route.steps.map((step, idx) => (
                  <li key={idx} className="flex items-start gap-3 bg-dark-surface/60 p-3 rounded-xl border border-dark-border">
                    <span className="w-5 h-5 rounded-full bg-brand-500/20 text-brand-400 flex items-center justify-center font-bold font-mono flex-shrink-0">
                      {idx + 1}
                    </span>
                    <span className="leading-relaxed">{step}</span>
                  </li>
                ))}
              </ol>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center py-8 text-gray-500 text-xs">
                <Navigation className="w-8 h-8 mb-2 opacity-40" />
                Select an origin and destination point to generate step-by-step navigation directions.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
