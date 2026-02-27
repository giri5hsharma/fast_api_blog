from datetime import UTC, datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer

from pwdlib import PasswordHash
from config import settings #imports settings from the config file i just created

password_hash = PasswordHash.recommended() #creates a password hasher using the recommended algorithm (bcrypt)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")  # must match login endpoint path


def hash_password(password:str) -> str:
    return password_hash.hash(password) #hashes the password using the password hasher

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return password_hash.verify(plain_password, hashed_password) #verifies the plain password against the hashed password


#ENCRYPTION REVERSIBLE. HASHING ISNT. ARGON2 CREATES RANDOM SEED FOR EACH HASH. PREVENTS HACKERS FROM USING RAINBOW TABLES TO CRACK HASHES.
# BCRYPT ALSO USES SALTING AND IS SLOW BY DESIGN, MAKING IT RESISTANT TO BRUTE-FORCE ATTACKS. BOTH ARE GOOD CHOICES FOR PASSWORD HASHING, 
# WITH ARGON2 BEING THE MORE MODERN AND SECURE OPTION.

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes,
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )
    return encoded_jwt

def verify_access_token(token: str) -> str | None:
    """Verify a JWT access token and return the subject (user id) if valid."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")



#JWT STRUCTURE
# THE HEADER CONTAINS THE ALGORITHM AND TYPE
# PAYLOAD CONTAINS THE DATA AND THE EXPIRATION
# SIGNATURE: PROVE THE TOKEN WASNT TAMPERED WITH

# HEADER: {"alg": "HS256", "typ": "JWT"}
# PAYLOAD: {"sub": "user_id", "exp": "expiration_time"}
# SIGNATURE: HMACSHA256(base64UrlEncode(header) + "." + base64

