"""Registration, login and profile routes for the school platform."""
import re
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

from auth_utils import create_token, hash_password, public_user, require_auth, verify_password
from config import Config
from curriculum import CLASS_LEVELS, level_for_class
from db import get_db

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SECTIONS = {"A", "B", "C", "D"}


def _clean_class_level(value):
    try:
        class_level = int(value)
    except (TypeError, ValueError):
        return None
    return class_level if class_level in CLASS_LEVELS else None


def _password_problem(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must include at least one letter and one number"
    return None


@auth_bp.post("/register")
def register():
    """
    Create a student account, or a teacher account with the invite code.

    Students must choose a class from 1 to 10. Administrators are seeded only.
    """
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "student").strip().lower()

    if len(name) < 2:
        return jsonify({"error": "Please enter your full name"}), 400
    if len(name) > 60:
        return jsonify({"error": "Name is too long"}), 400
    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "Please enter a valid email address"}), 400
    password_error = _password_problem(password)
    if password_error:
        return jsonify({"error": password_error}), 400
    if role not in {"student", "teacher"}:
        return jsonify({"error": "Only student and teacher accounts can be created"}), 400

    db = get_db()
    if db.users.find_one({"email": email}):
        return jsonify({"error": "An account with this email already exists"}), 409

    class_level = None
    section = None
    roll_no = None

    if role == "student":
        class_level = _clean_class_level(data.get("class_level"))
        if not class_level:
            return jsonify({"error": "Please choose a class between 1 and 10"}), 400
        section = (data.get("section") or "").strip().upper()[:1]
        section = section if section in SECTIONS else None
        roll_no = (data.get("roll_no") or "").strip()[:20] or None
    else:
        invite_code = (data.get("invite_code") or "").strip()
        if invite_code != Config.TEACHER_INVITE_CODE:
            return jsonify({"error": "Teacher invite code is not correct"}), 403

    user = {
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "role": role,
        "class_level": class_level,
        "level": level_for_class(class_level) if class_level else None,
        "section": section,
        "roll_no": roll_no,
        "subjects": ["English", "Mathematics"] if role == "teacher" else [],
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "last_login": None,
    }
    user["_id"] = db.users.insert_one(user).inserted_id
    return jsonify({"token": create_token(user), "user": public_user(user)}), 201


@auth_bp.post("/login")
def login():
    """Log in with email and password."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    db = get_db()
    user = db.users.find_one({"email": email})
    if not user or not verify_password(password, user.get("password_hash", "")):
        return jsonify({"error": "Email or password is incorrect"}), 401
    if user.get("is_active") is False:
        return jsonify({"error": "This account has been deactivated. Please contact your teacher."}), 403

    db.users.update_one(
        {"_id": user["_id"]}, {"$set": {"last_login": datetime.now(timezone.utc)}}
    )
    return jsonify({"token": create_token(user), "user": public_user(user)})


@auth_bp.get("/me")
@require_auth()
def me():
    return jsonify({"user": public_user(g.user)})


@auth_bp.patch("/profile")
@require_auth()
def update_profile():
    """Update a student's class/section or a user's display name."""
    data = request.get_json(silent=True) or {}
    updates = {}

    if "name" in data:
        name = (data.get("name") or "").strip()
        if len(name) < 2:
            return jsonify({"error": "Please enter your full name"}), 400
        updates["name"] = name[:60]

    if g.user.get("role") == "student":
        if "class_level" in data:
            class_level = _clean_class_level(data.get("class_level"))
            if not class_level:
                return jsonify({"error": "Please choose a class between 1 and 10"}), 400
            updates["class_level"] = class_level
            updates["level"] = level_for_class(class_level)
            # Changing class resets the section to avoid invalid combinations.
            updates["section"] = None
            updates["roll_no"] = None
        if "section" in data:
            section = (data.get("section") or "").strip().upper()[:1]
            updates["section"] = section if section in SECTIONS else None
        if "roll_no" in data:
            updates["roll_no"] = (data.get("roll_no") or "").strip()[:20] or None

    if not updates:
        return jsonify({"error": "Nothing to update"}), 400

    get_db().users.update_one({"_id": g.user["_id"]}, {"$set": updates})
    user = get_db().users.find_one({"_id": g.user["_id"]})
    return jsonify({"user": public_user(user)})


@auth_bp.post("/logout")
@require_auth()
def logout():
    """Tokens are stateless; the client removes its copy."""
    return jsonify({"message": "Logged out"})
