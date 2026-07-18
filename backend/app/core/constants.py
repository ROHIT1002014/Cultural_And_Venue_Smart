"""Application-wide constants and enumerations."""
from enum import StrEnum


class UserRole(StrEnum):
    """User role hierarchy levels."""
    ADMIN = "ADMIN"
    VOLUNTEER = "VOLUNTEER"
    USER = "USER"
    GUEST = "GUEST"


class POICategory(StrEnum):
    """Points of interest classification."""
    RESTROOM = "restroom"
    EXIT = "exit"
    FOOD = "food"
    SEATING = "seating"
    EXHIBIT = "exhibit"
    INFO_DESK = "info_desk"
    ELEVATOR = "elevator"


class ParkingStatus(StrEnum):
    """Parking lot operational state."""
    OPEN = "OPEN"
    FULL = "FULL"
    MAINTENANCE = "MAINTENANCE"


class AlertSeverity(StrEnum):
    """Emergency alert severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
