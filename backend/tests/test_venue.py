import pytest
from uuid import uuid4
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_venue_crud_and_pois(client: AsyncClient) -> None:
    """Test creating venue, adding POIs, and computing routes."""
    # First register an admin user to get authorization token
    admin_payload = {
        "email": "admin@example.com",
        "password": "AdminPassword123!",
        "full_name": "Platform Admin",
        "role": "ADMIN"
    }
    reg_response = await client.post("/api/v1/auth/register", json=admin_payload)
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create venue
    venue_payload = {
        "name": "Metropolitan Exhibition Center",
        "address": "500 Art Way, City Center",
        "total_capacity": 8000
    }
    venue_resp = await client.post("/api/v1/venues", json=venue_payload, headers=headers)
    assert venue_resp.status_code == 201
    venue_id = venue_resp.json()["id"]

    # Add origin POI
    origin_payload = {
        "venue_id": venue_id,
        "name": "Main Entrance Lobby",
        "category": "exit",
        "floor_level": 1,
        "is_accessible": True
    }
    origin_resp = await client.post(f"/api/v1/venues/{venue_id}/pois", json=origin_payload, headers=headers)
    assert origin_resp.status_code == 201
    origin_id = origin_resp.json()["id"]

    # Add destination POI
    dest_payload = {
        "venue_id": venue_id,
        "name": "West Wing Restroom",
        "category": "restroom",
        "floor_level": 2,
        "is_accessible": True
    }
    dest_resp = await client.post(f"/api/v1/venues/{venue_id}/pois", json=dest_payload, headers=headers)
    assert dest_resp.status_code == 201
    dest_id = dest_resp.json()["id"]

    # Calculate step-free route
    route_payload = {
        "venue_id": venue_id,
        "origin_poi_id": origin_id,
        "destination_poi_id": dest_id,
        "require_accessible_route": True
    }
    route_resp = await client.post(f"/api/v1/venues/{venue_id}/routes", json=route_payload)
    assert route_resp.status_code == 200
    route_data = route_resp.json()
    assert route_data["is_accessible"] is True
    assert any("Elevator" in step for step in route_data["steps"])


@pytest.mark.asyncio
async def test_get_venue_by_id_and_404(client: AsyncClient) -> None:
    """Test retrieving existing venue by ID and handling 404 for non-existent venue."""
    admin_payload = {
        "email": "getadmin@example.com",
        "password": "AdminPassword123!",
        "full_name": "Get Admin",
        "role": "ADMIN"
    }
    reg_response = await client.post("/api/v1/auth/register", json=admin_payload)
    headers = {"Authorization": f"Bearer {reg_response.json()['access_token']}"}

    venue_resp = await client.post("/api/v1/venues", json={"name": "Gallery A", "address": "1 A St"}, headers=headers)
    venue_id = venue_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/venues/{venue_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Gallery A"

    fake_id = str(uuid4())
    not_found_resp = await client.get(f"/api/v1/venues/{fake_id}")
    assert not_found_resp.status_code == 404


@pytest.mark.asyncio
async def test_list_pois_filtering(client: AsyncClient) -> None:
    """Test listing POIs with category and accessible_only filters."""
    admin_payload = {
        "email": "poiadmin@example.com",
        "password": "AdminPassword123!",
        "full_name": "POI Admin",
        "role": "ADMIN"
    }
    reg_response = await client.post("/api/v1/auth/register", json=admin_payload)
    headers = {"Authorization": f"Bearer {reg_response.json()['access_token']}"}

    venue_resp = await client.post("/api/v1/venues", json={"name": "Filter Venue", "address": "2 B St"}, headers=headers)
    venue_id = venue_resp.json()["id"]

    await client.post(f"/api/v1/venues/{venue_id}/pois", json={"venue_id": venue_id, "name": "Access Exit", "category": "exit", "floor_level": 1, "is_accessible": True}, headers=headers)
    await client.post(f"/api/v1/venues/{venue_id}/pois", json={"venue_id": venue_id, "name": "Stairway Gallery", "category": "exhibit", "floor_level": 2, "is_accessible": False}, headers=headers)

    # Filter accessible only
    acc_resp = await client.get(f"/api/v1/venues/{venue_id}/pois?accessible_only=true")
    assert acc_resp.status_code == 200
    acc_items = acc_resp.json()
    assert len(acc_items) == 1
    assert acc_items[0]["name"] == "Access Exit"

    # Filter category
    cat_resp = await client.get(f"/api/v1/venues/{venue_id}/pois?category=exhibit")
    assert cat_resp.status_code == 200
    assert len(cat_resp.json()) == 1
    assert cat_resp.json()[0]["name"] == "Stairway Gallery"


@pytest.mark.asyncio
async def test_crowd_density_endpoint(client: AsyncClient) -> None:
    """Test crowd density endpoint returns simulated zones."""
    admin_payload = {
        "email": "crowdadmin@example.com",
        "password": "AdminPassword123!",
        "full_name": "Crowd Admin",
        "role": "ADMIN"
    }
    reg_response = await client.post("/api/v1/auth/register", json=admin_payload)
    headers = {"Authorization": f"Bearer {reg_response.json()['access_token']}"}

    venue_resp = await client.post("/api/v1/venues", json={"name": "Crowd Venue", "address": "3 C Street Avenue"}, headers=headers)
    venue_id = venue_resp.json()["id"]

    crowd_resp = await client.get(f"/api/v1/venues/{venue_id}/crowd-density")
    assert crowd_resp.status_code == 200
    zones = crowd_resp.json()
    assert len(zones) >= 1
    assert any(z["density_status"] in ["SPARSE", "MODERATE", "DENSE", "OVERCROWDED"] for z in zones)


@pytest.mark.asyncio
async def test_trigger_emergency_alert(client: AsyncClient) -> None:
    """Test triggering an emergency evacuation alert."""
    admin_payload = {
        "email": "alertadmin@example.com",
        "password": "AdminPassword123!",
        "full_name": "Alert Admin",
        "role": "ADMIN"
    }
    reg_response = await client.post("/api/v1/auth/register", json=admin_payload)
    headers = {"Authorization": f"Bearer {reg_response.json()['access_token']}"}

    venue_resp = await client.post("/api/v1/venues", json={"name": "Alert Venue", "address": "4 D Street Avenue"}, headers=headers)
    venue_id = venue_resp.json()["id"]

    alert_payload = {
        "venue_id": venue_id,
        "alert_type": "FIRE_EVACUATION",
        "severity": "CRITICAL",
        "location": {"zone": "North Wing Floor 2"}
    }
    alert_resp = await client.post(f"/api/v1/venues/{venue_id}/alerts", json=alert_payload, headers=headers)
    assert alert_resp.status_code == 201
    alert_data = alert_resp.json()
    assert alert_data["alert_type"] == "FIRE_EVACUATION"
    assert alert_data["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_route_calculation_different_venue_error(client: AsyncClient) -> None:
    """Test calculating route with POIs from different venues returns validation error."""
    admin_payload = {
        "email": "routeadmin@example.com",
        "password": "AdminPassword123!",
        "full_name": "Route Admin",
        "role": "ADMIN"
    }
    reg_response = await client.post("/api/v1/auth/register", json=admin_payload)
    headers = {"Authorization": f"Bearer {reg_response.json()['access_token']}"}

    v1_resp = await client.post("/api/v1/venues", json={"name": "Venue 1", "address": "1000 First Street"}, headers=headers)
    v2_resp = await client.post("/api/v1/venues", json={"name": "Venue 2", "address": "2000 Second Street"}, headers=headers)
    v1_id = v1_resp.json()["id"]
    v2_id = v2_resp.json()["id"]

    p1_resp = await client.post(f"/api/v1/venues/{v1_id}/pois", json={"venue_id": v1_id, "name": "P1", "category": "exit", "floor_level": 1, "is_accessible": True}, headers=headers)
    p2_resp = await client.post(f"/api/v1/venues/{v2_id}/pois", json={"venue_id": v2_id, "name": "P2", "category": "exit", "floor_level": 1, "is_accessible": True}, headers=headers)

    route_payload = {
        "venue_id": v1_id,
        "origin_poi_id": p1_resp.json()["id"],
        "destination_poi_id": p2_resp.json()["id"]
    }
    route_resp = await client.post(f"/api/v1/venues/{v1_id}/routes", json=route_payload)
    assert route_resp.status_code == 422
