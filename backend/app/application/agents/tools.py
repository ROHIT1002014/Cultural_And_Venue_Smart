from typing import Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """OpenAI/Gemini function calling metadata specification."""
    name: str = Field(..., description="Function identifier name")
    description: str = Field(..., description="Clear explanation of what the tool executes")
    parameters: Dict[str, Any] = Field(..., description="JSON Schema object defining parameters")


# Pre-defined tool specifications for AI model function calling
TOOL_FIND_POI = ToolDefinition(
    name="find_poi",
    description="Find indoor or outdoor points of interest such as restrooms, exits, or seating.",
    parameters={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["restroom", "exit", "food", "seating", "exhibit", "elevator"],
                "description": "Category of the point of interest"
            },
            "accessible_only": {
                "type": "boolean",
                "description": "Filter strictly for wheelchair-accessible POIs"
            },
            "floor_level": {
                "type": "integer",
                "description": "Floor number to check"
            }
        },
        "required": ["category"]
    }
)

TOOL_CHECK_PARKING = ToolDefinition(
    name="check_parking_status",
    description="Check real-time available spots, EV charging status, and accessible spaces across parking lots.",
    parameters={
        "type": "object",
        "properties": {
            "lot_name": {
                "type": "string",
                "description": "Name of the parking lot (e.g., Lot A, Lot B)"
            }
        },
        "required": []
    }
)

TOOL_TRIGGER_EMERGENCY = ToolDefinition(
    name="trigger_emergency_alert",
    description="Trigger an immediate emergency evacuation notice across the venue. REQUIRES ADMIN/VOLUNTEER PERMISSION.",
    parameters={
        "type": "object",
        "properties": {
            "alert_type": {
                "type": "string",
                "description": "Nature of emergency (FIRE_ALARM, MEDICAL_EMERGENCY, SECURITY_THREAT)"
            },
            "severity": {
                "type": "string",
                "enum": ["HIGH", "CRITICAL"],
                "description": "Severity classification"
            }
        },
        "required": ["alert_type", "severity"]
    }
)

AVAILABLE_TOOLS: List[ToolDefinition] = [
    TOOL_FIND_POI,
    TOOL_CHECK_PARKING,
    TOOL_TRIGGER_EMERGENCY,
]
