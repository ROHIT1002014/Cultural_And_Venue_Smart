from typing import Any
from uuid import UUID

from app.application.schemas.assistant import ExecutedToolDTO
from app.application.services.parking_service import ParkingService
from app.application.services.venue_service import NavigationService, VenueService


class BaseSubAgent:
    """Abstract base for specialized domain agents."""
    agent_name: str = "BaseSubAgent"

    async def execute(self, query: str, context: dict[str, Any]) -> tuple[str, list[ExecutedToolDTO]]:
        """Process query and return domain response alongside executed tool summary."""
        raise NotImplementedError


class NavigationAgent(BaseSubAgent):
    """Sub-agent specializing in indoor/outdoor navigation, accessible routes, and seat/restroom finder."""
    agent_name = "NavigationAgent"

    def __init__(self, venue_service: VenueService, nav_service: NavigationService):
        self.venue_service = venue_service
        self.nav_service = nav_service

    async def execute(self, query: str, context: dict[str, Any]) -> tuple[str, list[ExecutedToolDTO]]:
        venue_id: UUID = context.get("venue_id") or UUID("00000000-0000-0000-0000-000000000001")
        executed: list[ExecutedToolDTO] = []

        query_lower = query.lower()
        if "restroom" in query_lower or "toilet" in query_lower or "bathroom" in query_lower:
            accessible = "wheelchair" in query_lower or "accessible" in query_lower
            pois = await self.venue_service.list_pois(venue_id=venue_id, category="restroom", accessible_only=accessible)
            poi_summary = f"Found {len(pois)} restrooms: " + ", ".join([f"{p.name} (Floor {p.floor_level})" for p in pois])
            executed.append(
                ExecutedToolDTO(
                    agent_name=self.agent_name,
                    tool_name="find_poi",
                    arguments={"category": "restroom", "accessible_only": accessible},
                    output_summary=poi_summary,
                )
            )
            return f"Navigation Guidance: {poi_summary}. Step-free elevator routing is available.", executed

        return "Navigation Agent: Ready to assist with indoor maps and wheelchair-accessible paths.", executed


class ParkingAgent(BaseSubAgent):
    """Sub-agent specializing in real-time parking availability and EV charging status."""
    agent_name = "ParkingAgent"

    def __init__(self, parking_service: ParkingService):
        self.parking_service = parking_service

    async def execute(self, query: str, context: dict[str, Any]) -> tuple[str, list[ExecutedToolDTO]]:
        venue_id: UUID = context.get("venue_id") or UUID("00000000-0000-0000-0000-000000000001")
        lots = await self.parking_service.list_venue_lots(venue_id=venue_id)

        summary_lines = [f"{lot.lot_name}: {lot.available_spots}/{lot.total_spots} spots available (EV: {'Yes' if lot.has_ev_charging else 'No'})" for lot in lots]
        output_str = "; ".join(summary_lines) if summary_lines else "No parking lots currently registered for this venue."

        executed = [
            ExecutedToolDTO(
                agent_name=self.agent_name,
                tool_name="check_parking_status",
                arguments={"venue_id": str(venue_id)},
                output_summary=output_str,
            )
        ]
        return f"Parking Logistics Update: {output_str}.", executed


class EmergencyAgent(BaseSubAgent):
    """Sub-agent handling priority emergency alerts and evacuation guidance."""
    agent_name = "EmergencyAgent"

    async def execute(self, query: str, context: dict[str, Any]) -> tuple[str, list[ExecutedToolDTO]]:
        executed = [
            ExecutedToolDTO(
                agent_name=self.agent_name,
                tool_name="emergency_protocol_check",
                arguments={"query": query},
                output_summary="Emergency protocol active. Directing to nearest exits.",
            )
        ]
        return "⚠️ EMERGENCY GUIDANCE: Please stay calm. Follow the illuminated green exit signs immediately. Do NOT use elevators.", executed
