import bcrypt
import passlib.handlers.bcrypt
from passlib.context import CryptContext

# Patch bcrypt.hashpw directly so passlib 1.7.4 does not crash when testing secrets > 72 bytes on bcrypt 4.0+
_original_bcrypt_hashpw = bcrypt.hashpw
def _patched_hashpw(password: bytes | str, salt: bytes | str) -> bytes:
    if isinstance(password, str):
        password = password.encode("utf-8")
    if len(password) > 72:
        password = password[:72]
    if isinstance(salt, str):
        salt = salt.encode("utf-8")
    return _original_bcrypt_hashpw(password, salt)

bcrypt.hashpw = _patched_hashpw
if hasattr(passlib.handlers.bcrypt, "_bcrypt") and passlib.handlers.bcrypt._bcrypt:
    passlib.handlers.bcrypt._bcrypt.hashpw = _patched_hashpw
if hasattr(passlib.handlers.bcrypt, "detect_wrap_bug"):
    passlib.handlers.bcrypt.detect_wrap_bug = lambda *a, **k: False

# Use bcrypt as default secure hashing algorithm, compatible with argon2 when installed
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt algorithm with automatic salt."""
    return str(pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against its hashed representation securely."""
    return bool(pwd_context.verify(plain_password, hashed_password))
