from passlib.context import CryptContext

"""
Password hashing / verification.

Rule: use `pbkdf2_sha256` as the primary scheme with `bcrypt` as a
fallback (bcrypt may fail at runtime on some systems).
"""

# Use pbkdf2_sha256 for hashing by default; still accept bcrypt hashes.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Explicit scheme keeps pbkdf2_sha256 as the hashing primary.
    # Verification still accepts legacy bcrypt hashes.
    return pwd_context.hash(password, scheme="pbkdf2_sha256")
