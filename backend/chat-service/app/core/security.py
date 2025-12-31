# ============================================================
# Chat Service - Security Module
# ============================================================

from typing import Optional, Dict, Any
from jose import jwt, JWTError
from datetime import datetime

from app.config import settings


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify JWT token and return payload.

    Args:
        token: JWT token string
        token_type: Type of token ('access' or 'refresh')

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Check token type
        if payload.get("type") != token_type:
            return None

        # Check expiration
        exp = payload.get("exp")
        if exp is None:
            return None

        if datetime.utcnow().timestamp() > exp:
            return None

        return payload

    except JWTError:
        return None
