import json
import logging
import pytest
from uuid import uuid4
from datetime import timedelta
from app.core.pagination import PaginationParams, PaginatedResponse
from app.core.logging import JSONFormatter, setup_logging, get_logger
from app.core.security.jwt import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_access_token,
    revoke_access_token,
)
from app.core.security.rate_limiter import (
    check_account_lockout,
    record_login_attempt,
)
from app.core.exceptions import UnauthorizedException


def test_pagination_params_and_response() -> None:
    params = PaginationParams(page=2, page_size=10, sort_by="name", sort_order="desc")
    assert params.offset == 10

    items = ["item1", "item2"]
    resp = PaginatedResponse.create(items=items, total_count=25, params=params)
    assert resp.total_pages == 3
    assert resp.has_next is True
    assert resp.has_prev is True
    assert resp.items == items

    # Test edge case with 0 items
    params_zero = PaginationParams(page=1, page_size=10)
    resp_zero = PaginatedResponse.create(items=[], total_count=0, params=params_zero)
    assert resp_zero.total_pages == 0
    assert resp_zero.has_next is False
    assert resp_zero.has_prev is False


def test_json_formatter_and_setup_logging() -> None:
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Structured message",
        args=(),
        exc_info=None,
    )
    record.trace_id = "trace-123"
    record.user_id = "user-abc"
    record.project = "Copilot"
    record.agent_name = "NavAgent"
    record.latency_ms = 45.2

    formatted = formatter.format(record)
    data = json.loads(formatted)
    assert data["message"] == "Structured message"
    assert data["trace_id"] == "trace-123"
    assert data["user_id"] == "user-abc"
    assert data["agent_name"] == "NavAgent"
    assert data["latency_ms"] == 45.2

    # Test with exception
    try:
        raise ValueError("Simulated error")
    except ValueError as exc:
        record_exc = logging.LogRecord(
            name="exc.logger",
            level=logging.ERROR,
            pathname="exc.py",
            lineno=20,
            msg="Error occurred",
            args=(),
            exc_info=sys_exc_info(),
        )
        formatted_exc = formatter.format(record_exc)
        data_exc = json.loads(formatted_exc)
        assert "exception" in data_exc
        assert "ValueError: Simulated error" in data_exc["exception"]

    setup_logging(log_level="DEBUG")
    logger = get_logger("my.custom.logger")
    assert logger.name == "my.custom.logger"


def sys_exc_info():
    import sys
    return sys.exc_info()


@pytest.mark.asyncio
async def test_jwt_operations_valid_and_revocation() -> None:
    user_id = str(uuid4())
    token = create_access_token(user_id=user_id, role="USER", extra_claims={"custom": "val"})
    assert token is not None

    payload = await verify_access_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == "USER"
    assert payload["custom"] == "val"
    assert "jti" in payload

    # Test revocation
    await revoke_access_token(token)
    with pytest.raises(UnauthorizedException) as exc_info:
        await verify_access_token(token)
    assert "revoked or blacklisted" in str(exc_info.value)

    # Test refresh token hashing
    raw_rt, hash_rt = create_refresh_token(user_id)
    assert len(raw_rt) > 20
    assert hash_refresh_token(raw_rt) == hash_rt

    # Test malformed / invalid signature token
    with pytest.raises(UnauthorizedException):
        await verify_access_token("invalid.jwt.token")


@pytest.mark.asyncio
async def test_rate_limiter_and_account_lockout() -> None:
    email = "lockout_test@example.com"
    ip = "127.0.0.1"
    # Success clears attempts
    await record_login_attempt(email, success=True, ip_address=ip)
    await check_account_lockout(email)  # Should not raise

    # Record 4 failures (not locked yet, threshold is 5)
    for _ in range(4):
        await record_login_attempt(email, success=False, ip_address=ip)
    await check_account_lockout(email)  # Still not locked

    # Record 5th failure
    await record_login_attempt(email, success=False, ip_address=ip)
    with pytest.raises(UnauthorizedException) as exc_info:
        await check_account_lockout(email)
    assert "Account is temporarily locked" in str(exc_info.value)

    # Success clears lockout
    await record_login_attempt(email, success=True, ip_address=ip)
    await check_account_lockout(email)  # Should not raise anymore
