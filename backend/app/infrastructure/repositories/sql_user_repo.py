from uuid import UUID

from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import RefreshToken, User
from app.domain.repositories.user_repo import IRefreshTokenRepository, IUserRepository
from app.infrastructure.models.user_model import RefreshTokenORM, UserORM
from app.infrastructure.repositories.generic_repo import SQLAlchemyGenericRepository


class SQLUserRepository(SQLAlchemyGenericRepository[User, UserORM], IUserRepository):
    """Async repository implementation for User entity."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserORM)

    def _to_domain(self, orm_obj: UserORM | None) -> User | None:
        if not orm_obj:
            return None
        return User(
            id=orm_obj.id,
            email=orm_obj.email,
            hashed_password=orm_obj.hashed_password,
            full_name=orm_obj.full_name,
            role=orm_obj.role,
            is_active=orm_obj.is_active,
            is_verified=orm_obj.is_verified,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
        )

    def _to_orm(self, domain_entity: User) -> UserORM:
        return UserORM(
            id=domain_entity.id,
            email=domain_entity.email,
            hashed_password=domain_entity.hashed_password,
            full_name=domain_entity.full_name,
            role=domain_entity.role,
            is_active=domain_entity.is_active,
            is_verified=domain_entity.is_verified,
            created_at=domain_entity.created_at,
            updated_at=domain_entity.updated_at,
        )

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserORM).where(UserORM.email == email.lower())
        result = await self.session.execute(stmt)
        return self._to_domain(result.scalar_one_or_none())


class SQLRefreshTokenRepository(SQLAlchemyGenericRepository[RefreshToken, RefreshTokenORM], IRefreshTokenRepository):
    """Async repository implementation for RefreshToken tracking."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, RefreshTokenORM)

    def _to_domain(self, orm_obj: RefreshTokenORM | None) -> RefreshToken | None:
        if not orm_obj:
            return None
        return RefreshToken(
            id=orm_obj.id,
            user_id=orm_obj.user_id,
            token_hash=orm_obj.token_hash,
            expires_at=orm_obj.expires_at,
            is_revoked=orm_obj.is_revoked,
            ip_address=orm_obj.ip_address,
            created_at=orm_obj.created_at,
        )

    def _to_orm(self, domain_entity: RefreshToken) -> RefreshTokenORM:
        return RefreshTokenORM(
            id=domain_entity.id,
            user_id=domain_entity.user_id,
            token_hash=domain_entity.token_hash,
            expires_at=domain_entity.expires_at,
            is_revoked=domain_entity.is_revoked,
            ip_address=domain_entity.ip_address,
            created_at=domain_entity.created_at,
        )

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshTokenORM).where(RefreshTokenORM.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return self._to_domain(result.scalar_one_or_none())

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        stmt = sa_update(RefreshTokenORM).where(RefreshTokenORM.user_id == user_id).values(is_revoked=True)
        await self.session.execute(stmt)
        await self.session.commit()
