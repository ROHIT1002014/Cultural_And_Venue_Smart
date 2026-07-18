from typing import Set
from app.core.constants import UserRole

# Define granular permission strings for domain actions
PERMISSION_VENUE_READ = "venue:read"
PERMISSION_VENUE_CREATE = "venue:create"
PERMISSION_VENUE_UPDATE = "venue:update"
PERMISSION_VENUE_DELETE = "venue:delete"

PERMISSION_PARKING_READ = "parking:read"
PERMISSION_PARKING_UPDATE = "parking:update"
PERMISSION_PARKING_RESERVE = "parking:reserve"

PERMISSION_EMERGENCY_TRIGGER = "emergency:trigger"
PERMISSION_EMERGENCY_RESOLVE = "emergency:resolve"

PERMISSION_USER_MANAGE = "user:manage"
PERMISSION_AI_CHAT = "ai:chat"

# Role hierarchy mappings to permissions (Inheritance and Least Privilege)
ROLE_PERMISSIONS_MATRIX: dict[UserRole, Set[str]] = {
    UserRole.GUEST: {
        PERMISSION_VENUE_READ,
        PERMISSION_PARKING_READ,
    },
    UserRole.USER: {
        PERMISSION_VENUE_READ,
        PERMISSION_PARKING_READ,
        PERMISSION_PARKING_RESERVE,
        PERMISSION_AI_CHAT,
    },
    UserRole.VOLUNTEER: {
        PERMISSION_VENUE_READ,
        PERMISSION_VENUE_UPDATE,
        PERMISSION_PARKING_READ,
        PERMISSION_PARKING_UPDATE,
        PERMISSION_PARKING_RESERVE,
        PERMISSION_AI_CHAT,
        PERMISSION_EMERGENCY_TRIGGER,
    },
    UserRole.ADMIN: {
        PERMISSION_VENUE_READ,
        PERMISSION_VENUE_CREATE,
        PERMISSION_VENUE_UPDATE,
        PERMISSION_VENUE_DELETE,
        PERMISSION_PARKING_READ,
        PERMISSION_PARKING_UPDATE,
        PERMISSION_PARKING_RESERVE,
        PERMISSION_EMERGENCY_TRIGGER,
        PERMISSION_EMERGENCY_RESOLVE,
        PERMISSION_USER_MANAGE,
        PERMISSION_AI_CHAT,
    },
}


def get_permissions_for_role(role: UserRole | str) -> Set[str]:
    """Retrieve all permissions assigned to a specific role."""
    try:
        enum_role = UserRole(role) if isinstance(role, str) else role
        return ROLE_PERMISSIONS_MATRIX.get(enum_role, set())
    except ValueError:
        return set()


def has_permission(user_role: UserRole | str, required_permission: str) -> bool:
    """Verify if a given role possesses the required permission string."""
    permissions = get_permissions_for_role(user_role)
    return required_permission in permissions
