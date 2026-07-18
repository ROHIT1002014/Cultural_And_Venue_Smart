"""Application-wide constants and enumerations."""
from enum import Enum


class UserRole(str, Enum):
    """User role hierarchy levels."""
    ADMIN = "ADMIN"
    VOLUNTEER = "VOLUNTEER"
    USER = "USER"
    GUEST = "GUEST"


class POICategory(str, Enum):
    """Points of interest classification."""
    RESTROOM = "restroom"
    EXIT = "exit"
    FOOD = "food"
    SEATING = "seating"
    EXHIBIT = "exhibit"
    INFO_DESK = "info_desk"
    ELEVATOR = "elevator"


class ParkingStatus(str, Enum):
    """Parking lot operational state."""
    OPEN = "OPEN"
    FULL = "FULL"
    MAINTENANCE = "MAINTENANCE"


class AlertSeverity(str, Enum):
    """Emergency alert severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
