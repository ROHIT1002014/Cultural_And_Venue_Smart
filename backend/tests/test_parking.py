from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_parking_creation_and_reservation(client: AsyncClient) -> None:
    """Test creating parking lots and reserving accessible EV spots."""
    admin_payload = {
        "email": "parkingadmin@example.com",
        "password": "AdminPassword123!",
        "full_name": "Parking Manager",
        "role": "ADMIN"
    }
    reg_response = await client.post("/api/v1/auth/register", json=admin_payload)
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # First need a venue
    venue_resp = await client.post("/api/v1/venues", json={
        "name": "Parking Test Hall",
        "address": "123 Park Street Avenue"
    }, headers=headers)
    venue_id = venue_resp.json()["id"]

    # Create parking lot
    lot_payload = {
        "venue_id": venue_id,
        "lot_name": "Underground Structure B",
        "total_spots": 100,
        "accessible_spots_total": 10,
        "has_ev_charging": True
    }
    lot_resp = await client.post("/api/v1/parking/lots", json=lot_payload, headers=headers)
    assert lot_resp.status_code == 201
    lot_id = lot_resp.json()["id"]

    # Reserve spot requiring EV charger and wheelchair access
    res_payload = {
        "lot_id": lot_id,
        "vehicle_license": "EV-CULTURE-1",
        "requires_accessible_spot": True,
        "requires_ev_charger": True
    }
    res_resp = await client.post("/api/v1/parking/reserve", json=res_payload, headers=headers)
    assert res_resp.status_code == 201
    assert res_resp.json()["vehicle_license"] == "EV-CULTURE-1"


@pytest.mark.asyncio
async def test_reserve_spot_full_lot_error(client: AsyncClient) -> None:
    """Test reserving spot when lot is full returns validation error."""
    admin_payload = {
        "email": "fulladmin@example.com",
        "password": "AdminPassword123!",
        "full_name": "Full Lot Manager",
        "role": "ADMIN"
    }
    reg_response = await client.post("/api/v1/auth/register", json=admin_payload)
    headers = {"Authorization": f"Bearer {reg_response.json()['access_token']}"}

    venue_resp = await client.post("/api/v1/venues", json={"name": "Full Hall", "address": "456 Full Street Avenue"}, headers=headers)
    venue_id = venue_resp.json()["id"]

    lot_resp = await client.post("/api/v1/parking/lots", json={
        "venue_id": venue_id,
        "lot_name": "Small Lot",
        "total_spots": 1,
        "accessible_spots_total": 0,
        "has_ev_charging": False
    }, headers=headers)
    lot_id = lot_resp.json()["id"]

    # Reserve the only spot
    res1 = await client.post("/api/v1/parking/reserve", json={"lot_id": lot_id, "vehicle_license": "CAR-1"}, headers=headers)
    assert res1.status_code == 201

    # Try to reserve second spot
    res2 = await client.post("/api/v1/parking/reserve", json={"lot_id": lot_id, "vehicle_license": "CAR-2"}, headers=headers)
    assert res2.status_code == 422
    assert "full" in res2.json()["message"].lower()


@pytest.mark.asyncio
async def test_reserve_spot_no_accessible_spots_error(client: AsyncClient) -> None:
    """Test reserving accessible spot when none left returns validation error."""
    admin_payload = {
        "email": "accadmin@example.com",
        "password": "AdminPassword123!",
        "full_name": "Acc Manager",
        "role": "ADMIN"
    }
    reg_response = await client.post("/api/v1/auth/register", json=admin_payload)
    headers = {"Authorization": f"Bearer {reg_response.json()['access_token']}"}

    venue_resp = await client.post("/api/v1/venues", json={"name": "Acc Hall", "address": "789 Acc Street Avenue"}, headers=headers)
    venue_id = venue_resp.json()["id"]

    lot_resp = await client.post("/api/v1/parking/lots", json={
        "venue_id": venue_id,
        "lot_name": "Acc Lot",
        "total_spots": 10,
        "accessible_spots_total": 1,
        "has_ev_charging": False
    }, headers=headers)
    lot_id = lot_resp.json()["id"]

    # Reserve the only accessible spot
    res1 = await client.post("/api/v1/parking/reserve", json={"lot_id": lot_id, "vehicle_license": "ACC-1", "requires_accessible_spot": True}, headers=headers)
    assert res1.status_code == 201

    # Try to reserve second accessible spot
    res2 = await client.post("/api/v1/parking/reserve", json={"lot_id": lot_id, "vehicle_license": "ACC-2", "requires_accessible_spot": True}, headers=headers)
    assert res2.status_code == 422
    assert "wheelchair-accessible" in res2.json()["message"].lower()


@pytest.mark.asyncio
async def test_reserve_spot_no_ev_charging_error(client: AsyncClient) -> None:
    """Test reserving EV spot in lot without charging returns validation error."""
    admin_payload = {
        "email": "evadmin@example.com",
        "password": "AdminPassword123!",
        "full_name": "EV Manager",
        "role": "ADMIN"
    }
    reg_response = await client.post("/api/v1/auth/register", json=admin_payload)
    headers = {"Authorization": f"Bearer {reg_response.json()['access_token']}"}

    venue_resp = await client.post("/api/v1/venues", json={"name": "EV Hall", "address": "101 EV Street Avenue"}, headers=headers)
    venue_id = venue_resp.json()["id"]

    lot_resp = await client.post("/api/v1/parking/lots", json={
        "venue_id": venue_id,
        "lot_name": "No EV Lot",
        "total_spots": 10,
        "accessible_spots_total": 2,
        "has_ev_charging": False
    }, headers=headers)
    lot_id = lot_resp.json()["id"]

    res_resp = await client.post("/api/v1/parking/reserve", json={"lot_id": lot_id, "vehicle_license": "EV-C2", "requires_ev_charger": True}, headers=headers)
    assert res_resp.status_code == 422
    assert "ev charging" in res_resp.json()["message"].lower()


@pytest.mark.asyncio
async def test_reserve_spot_nonexistent_lot_error(client: AsyncClient) -> None:
    """Test reserving spot in nonexistent lot returns 404."""
    admin_payload = {
        "email": "notfoundadmin@example.com",
        "password": "AdminPassword123!",
        "full_name": "NF Manager",
        "role": "ADMIN"
    }
    reg_response = await client.post("/api/v1/auth/register", json=admin_payload)
    headers = {"Authorization": f"Bearer {reg_response.json()['access_token']}"}

    res_resp = await client.post("/api/v1/parking/reserve", json={"lot_id": str(uuid4()), "vehicle_license": "NF-1"}, headers=headers)
    assert res_resp.status_code == 404


@pytest.mark.asyncio
async def test_list_venue_lots_status(client: AsyncClient) -> None:
    """Test listing venue lots returns proper OPEN / FULL status strings."""
    admin_payload = {
        "email": "statusadmin@example.com",
        "password": "AdminPassword123!",
        "full_name": "Status Manager",
        "role": "ADMIN"
    }
    reg_response = await client.post("/api/v1/auth/register", json=admin_payload)
    headers = {"Authorization": f"Bearer {reg_response.json()['access_token']}"}

    venue_resp = await client.post("/api/v1/venues", json={"name": "Status Hall", "address": "202 Status Street Avenue"}, headers=headers)
    venue_id = venue_resp.json()["id"]

    await client.post("/api/v1/parking/lots", json={"venue_id": venue_id, "lot_name": "Open Lot", "total_spots": 5, "accessible_spots_total": 1, "has_ev_charging": True}, headers=headers)
    lot_full = await client.post("/api/v1/parking/lots", json={"venue_id": venue_id, "lot_name": "Full Lot", "total_spots": 1, "accessible_spots_total": 0, "has_ev_charging": False}, headers=headers)

    # Fill the second lot
    await client.post("/api/v1/parking/reserve", json={"lot_id": lot_full.json()["id"], "vehicle_license": "FILL-1"}, headers=headers)

    lots_resp = await client.get(f"/api/v1/parking/lots/{venue_id}")
    assert lots_resp.status_code == 200
    lots = lots_resp.json()
    assert len(lots) == 2

    status_map = {l["lot_name"]: l["status"] for l in lots}
    assert status_map["Open Lot"] == "OPEN"
    assert status_map["Full Lot"] == "FULL"
