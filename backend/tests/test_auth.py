import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.infrastructure.models.user_model import UserORM


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient) -> None:
    """Test full user registration and subsequent login token exchange."""
    register_payload = {
        "email": "newuser@example.com",
        "password": "SecurePassword999!",
        "full_name": "New Registered User",
        "role": "USER"
    }
    reg_response = await client.post("/api/v1/auth/register", json=register_payload)
    assert reg_response.status_code == 201
    data = reg_response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "newuser@example.com"

    # Test login
    login_payload = {
        "username": "newuser@example.com",
        "password": "SecurePassword999!"
    }
    login_response = await client.post("/api/v1/auth/login", data=login_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data


@pytest.mark.asyncio
async def test_duplicate_user_registration_blocked(client: AsyncClient) -> None:
    """Test that registering the same email twice returns 422 Validation Error."""
    payload = {
        "email": "duplicate@example.com",
        "password": "SecurePassword999!",
        "full_name": "First User",
        "role": "USER"
    }
    await client.post("/api/v1/auth/register", json=payload)
    # Second attempt
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert "already registered" in response.json()["message"]


@pytest.mark.asyncio
async def test_invalid_login_credentials(client: AsyncClient) -> None:
    """Test invalid credentials return 401 Unauthorized."""
    login_payload = {
        "username": "nonexistent@example.com",
        "password": "WrongPassword123!"
    }
    response = await client.post("/api/v1/auth/login", data=login_payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_rotation_and_revocation(client: AsyncClient) -> None:
    """Test token rotation via refresh endpoint and rejection of reused/revoked tokens."""
    payload = {
        "email": "refreshuser@example.com",
        "password": "SecurePassword999!",
        "full_name": "Refresh User",
        "role": "USER"
    }
    reg_response = await client.post("/api/v1/auth/register", json=payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    refresh_token = reg_data["refresh_token"]

    # Rotate refresh token
    refresh_response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    rotated_data = refresh_response.json()
    assert "access_token" in rotated_data
    assert "refresh_token" in rotated_data
    assert rotated_data["refresh_token"] != refresh_token

    # Reusing the old refresh token must fail with 401
    old_reuse_response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert old_reuse_response.status_code == 401

    # Using invalid string must fail
    invalid_refresh_response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "fake-refresh-string-123"})
    assert invalid_refresh_response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile_and_logout_blacklist(client: AsyncClient) -> None:
    """Test accessing /me, performing logout, and ensuring blacklisted access tokens are rejected."""
    payload = {
        "email": "logoutuser@example.com",
        "password": "SecurePassword999!",
        "full_name": "Logout User",
        "role": "USER"
    }
    reg_resp = await client.post("/api/v1/auth/register", json=payload)
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify /me works
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "logoutuser@example.com"

    # Verify unauthenticated request returns 401
    unauth_resp = await client.get("/api/v1/auth/me")
    assert unauth_resp.status_code == 401

    # Logout
    logout_resp = await client.post("/api/v1/auth/logout", headers=headers)
    assert logout_resp.status_code == 200
    assert logout_resp.json()["success"] is True

    # Accessing /me after logout must return 401 because token is blacklisted in Redis
    post_logout_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert post_logout_resp.status_code == 401


@pytest.mark.asyncio
async def test_deactivated_user_blocked(client: AsyncClient, db_session) -> None:
    """Test that deactivated users cannot log in or refresh tokens."""
    payload = {
        "email": "deactivated@example.com",
        "password": "SecurePassword999!",
        "full_name": "Inactive User",
        "role": "USER"
    }
    await client.post("/api/v1/auth/register", json=payload)

    # Deactivate user in DB using shared db_session
    stmt = select(UserORM).where(UserORM.email == "deactivated@example.com")
    result = await db_session.execute(stmt)
    user = result.scalar_one()
    user.is_active = False
    await db_session.commit()

    # Login must fail
    login_resp = await client.post("/api/v1/auth/login", data={"username": "deactivated@example.com", "password": "SecurePassword999!"})
    assert login_resp.status_code == 401
    assert "deactivated" in login_resp.json()["message"].lower()
