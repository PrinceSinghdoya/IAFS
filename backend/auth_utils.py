"""
Authentication helpers: password hashing + JWT tokens + route decorators.
"""
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from bson import ObjectId
from flask import g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from db import get_db


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash a password with Werkzeug's salted PBKDF2/scrypt implementation."""
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------
def create_token(user) -> str:
    """Create a signed JWT for a user document."""
    payload = {
        "sub": str(user["_id"]),
        "role": user["role"],
        "email": user["email"],
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=Config.JWT_EXPIRES_HOURS),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def decode_token(token: str):
    """Return the token payload or raise jwt exceptions."""
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])


def public_user(user) -> dict:
    """Remove sensitive fields before sending a user to the frontend."""
    class_level = user.get("class_level")
    return {
        "id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "role": user.get("role"),
        "class_level": class_level,
        "level": user.get("level") or ("Primary" if class_level and class_level <= 5 else "Secondary" if class_level else None),
        "section": user.get("section"),
        "roll_no": user.get("roll_no"),
        "subjects": user.get("subjects", []),
        "is_active": user.get("is_active", True),
        "is_demo": bool(user.get("is_demo")),
        "created_at": user.get("created_at"),
    }


# ---------------------------------------------------------------------------
# Route protection decorators
# ---------------------------------------------------------------------------
def require_auth(role=None):
    """
    Decorator that validates the Bearer token and (optionally) the user role.

    Usage:
        @require_auth()
        @require_auth("teacher")
        @require_auth(["teacher", "admin"])
    """

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Authentication required"}), 401

            token = auth_header.split(" ", 1)[1].strip()
            try:
                payload = decode_token(token)
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Session expired, please log in again"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid login token"}), 401

            try:
                user = get_db().users.find_one({"_id": ObjectId(payload["sub"])})
            except Exception:
                user = None

            if not user:
                return jsonify({"error": "User account not found"}), 401

            if user.get("is_active") is False:
                return jsonify({"error": "This account has been deactivated"}), 403

            allowed = None
            if role:
                allowed = set(role) if isinstance(role, (list, tuple, set)) else {role}
                if user.get("role") not in allowed:
                    return jsonify({"error": "You do not have access to this resource"}), 403

            # Make the current user available inside the route.
            g.user = user
            g.user_id = str(user["_id"])
            return view(*args, **kwargs)

        return wrapped

    return decorator


def require_roles(*roles):
    """Small convenience wrapper for multi-role routes."""
    return require_auth(list(roles))
