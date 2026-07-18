from abc import abstractmethod
from uuid import UUID
from app.domain.entities.user import User, RefreshToken
from app.domain.repositories.base import IGenericRepository


class IUserRepository(IGenericRepository[User]):
    """Repository interface for User entity persistence."""

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by their unique email address."""
        pass


class IRefreshTokenRepository(IGenericRepository[RefreshToken]):
    """Repository interface for RefreshToken tracking and rotation."""

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """Retrieve a refresh token record by its cryptographic hash."""
        pass

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID) -> None:
        """Revoke all active refresh tokens for a specific user ID."""
        pass
