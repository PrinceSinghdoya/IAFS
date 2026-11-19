"""Administrator routes: school overview, users and curriculum structure."""
import re
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

from auth_utils import hash_password, public_user, require_auth
from curriculum import CLASS_LEVELS, SUBJECTS, SUBJECT_INFO, TOPICS, level_for_class
from db import get_db
from services.analytics import admin_overview
from utils import json_safe, serialize_result, to_object_id

admin_bp = Blueprint("admin", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SECTIONS = {"A", "B", "C", "D"}


def _class_level(value):
    try:
        level = int(value)
    except (TypeError, ValueError):
        return None
    return level if level in CLASS_LEVELS else None


def _password_problem(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must include at least one letter and one number"
    return None


@admin_bp.get("/admin/dashboard")
@require_auth("admin")
def admin_dashboard():
    db = get_db()
    overview = admin_overview()
    recent_results = list(
        db.learning_results.find({}).sort("created_at", -1).limit(8)
    )
    overview["recent_results"] = [
        serialize_result(result) for result in recent_results
    ]
    overview["subjects"] = [
        {
            "name": subject,
            "emoji": SUBJECT_INFO[subject]["emoji"],
            "tagline": SUBJECT_INFO[subject]["tagline"],
            "topics": len([topic for topic in TOPICS if topic["subject"] == subject]),
        }
        for subject in SUBJECTS
    ]
    return jsonify(overview)


@admin_bp.get("/admin/users")
@require_auth("admin")
def admin_users():
    """Filterable user directory."""
    db = get_db()
    role = request.args.get("role")
    class_level = _class_level(request.args.get("class_level"))
    search = (request.args.get("search") or "").strip().lower()
    query = {}
    if role in {"student", "teacher", "admin"}:
        query["role"] = role
    if class_level:
        query["class_level"] = class_level
    users = list(db.users.find(query).sort([("role", 1), ("class_level", 1), ("name", 1)]))
    if search:
        users = [
            user
            for user in users
            if search in (user.get("name") or "").lower()
            or search in (user.get("email") or "").lower()
        ]
    results = list(db.learning_results.find({}))
    attempts_by_student = {}
    for result in results:
        key = str(result.get("student_id"))
        attempts_by_student[key] = attempts_by_student.get(key, 0) + 1

    return jsonify(
        {
            "users": [
                {
                    **public_user(user),
                    "attempts": attempts_by_student.get(str(user["_id"]), 0),
                    "last_login": json_safe(user.get("last_login")),
                }
                for user in users
            ],
            "total": len(users),
            "roles": ["student", "teacher", "admin"],
            "classes": CLASS_LEVELS,
        }
    )


@admin_bp.post("/admin/users")
@require_auth("admin")
def create_user():
    """Create a student or teacher account from the admin panel."""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "student").strip().lower()

    if len(name) < 2:
        return jsonify({"error": "Please enter a full name"}), 400
    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "Please enter a valid email address"}), 400
    password_error = _password_problem(password)
    if password_error:
        return jsonify({"error": password_error}), 400
    if role not in {"student", "teacher"}:
        return jsonify({"error": "Create only student or teacher accounts here"}), 400

    db = get_db()
    if db.users.find_one({"email": email}):
        return jsonify({"error": "An account with this email already exists"}), 409

    class_level = None
    section = None
    roll_no = None
    if role == "student":
        class_level = _class_level(data.get("class_level"))
        if not class_level:
            return jsonify({"error": "Choose a class from 1 to 10"}), 400
        section = (data.get("section") or "").strip().upper()[:1] or None
        section = section if section in SECTIONS else None
        roll_no = (data.get("roll_no") or "").strip()[:20] or None

    user = {
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "role": role,
        "class_level": class_level,
        "level": level_for_class(class_level) if class_level else None,
        "section": section,
        "roll_no": roll_no,
        "subjects": SUBJECTS if role == "teacher" else [],
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "last_login": None,
    }
    user["_id"] = db.users.insert_one(user).inserted_id
    return jsonify({"user": public_user(user)}), 201


@admin_bp.patch("/admin/users/<user_id>")
@require_auth("admin")
def update_user(user_id):
    """Activate/deactivate a user or correct their profile details."""
    db = get_db()
    object_id = to_object_id(user_id)
    target = db.users.find_one({"_id": object_id}) if object_id else None
    if not target:
        return jsonify({"error": "User not found"}), 404
    if str(target["_id"]) == g.user_id and "is_active" in (request.get_json(silent=True) or {}):
        data = request.get_json(silent=True) or {}
        if data.get("is_active") is False:
            return jsonify({"error": "You cannot deactivate your own account"}), 400

    data = request.get_json(silent=True) or {}
    updates = {}
    if "name" in data:
        name = (data.get("name") or "").strip()
        if len(name) < 2:
            return jsonify({"error": "Please enter a full name"}), 400
        updates["name"] = name[:60]
    if "is_active" in data:
        updates["is_active"] = bool(data.get("is_active"))
        if str(target["_id"]) == g.user_id and updates["is_active"] is False:
            return jsonify({"error": "You cannot deactivate your own account"}), 400
        if target.get("role") == "admin" and updates["is_active"] is False:
            active_admins = db.users.count_documents({"role": "admin", "is_active": {"$ne": False}})
            if active_admins <= 1:
                return jsonify({"error": "At least one active administrator is required"}), 400
    if "role" in data:
        role = (data.get("role") or "").strip().lower()
        if role not in {"student", "teacher", "admin"}:
            return jsonify({"error": "Unknown role"}), 400
        if str(target["_id"]) == g.user_id and role != target.get("role"):
            return jsonify({"error": "You cannot change your own role"}), 400
        updates["role"] = role
        # A teacher or administrator has no class. Clear a stale class
        # unless the request also supplies a new one.
        if role != "student" and "class_level" not in data:
            updates["class_level"] = None
            updates["level"] = None
        elif role == "student" and "class_level" not in data:
            # Staff accounts have no class; a student must always have one.
            class_level = _class_level(target.get("class_level"))
            if not class_level:
                return jsonify({"error": "Choose a class from 1 to 10 for this student"}), 400
            updates["class_level"] = class_level
            updates["level"] = level_for_class(class_level)
    if "class_level" in data:
        class_level = _class_level(data.get("class_level"))
        effective_role = updates.get("role", target.get("role"))
        if effective_role == "student":
            if not class_level:
                return jsonify({"error": "Choose a class from 1 to 10"}), 400
            updates["class_level"] = class_level
            updates["level"] = level_for_class(class_level)
        else:
            updates["class_level"] = None
            updates["level"] = None
    if "section" in data:
        section = (data.get("section") or "").strip().upper()[:1]
        updates["section"] = section if section in SECTIONS else None
    if "roll_no" in data:
        updates["roll_no"] = (data.get("roll_no") or "").strip()[:20] or None

    if not updates:
        return jsonify({"error": "Nothing to update"}), 400

    db.users.update_one({"_id": object_id}, {"$set": updates})
    user = db.users.find_one({"_id": object_id})
    return jsonify({"user": public_user(user)})


@admin_bp.post("/admin/users/<user_id>/reset-password")
@require_auth("admin")
def reset_password(user_id):
    data = request.get_json(silent=True) or {}
    password = data.get("password") or ""
    password_error = _password_problem(password)
    if password_error:
        return jsonify({"error": password_error}), 400
    object_id = to_object_id(user_id)
    target = get_db().users.find_one({"_id": object_id}) if object_id else None
    if not target:
        return jsonify({"error": "User not found"}), 404
    get_db().users.update_one(
        {"_id": object_id},
        {"$set": {"password_hash": hash_password(password), "password_reset_at": datetime.now(timezone.utc)}},
    )
    return jsonify({"message": f"Password reset for {target.get('name')}"})


@admin_bp.get("/admin/classes-subjects")
@require_auth("admin")
def classes_subjects():
    """Class structure and the full subject/topic catalogue."""
    db = get_db()
    students = list(db.users.find({"role": "student", "is_active": {"$ne": False}}))
    classes = []
    for class_level in CLASS_LEVELS:
        classes.append(
            {
                "class_level": class_level,
                "level": level_for_class(class_level),
                "students": len(
                    [student for student in students if student.get("class_level") == class_level]
                ),
                "topics": len([topic for topic in TOPICS if topic["level"] == level_for_class(class_level)]),
            }
        )
    subjects = []
    for subject in SUBJECTS:
        info = SUBJECT_INFO[subject]
        subjects.append(
            {
                "name": subject,
                "emoji": info["emoji"],
                "tagline": info["tagline"],
                "description": info["description"],
                "primary_topics": len(
                    [topic for topic in TOPICS if topic["subject"] == subject and topic["level"] == "Primary"]
                ),
                "secondary_topics": len(
                    [topic for topic in TOPICS if topic["subject"] == subject and topic["level"] == "Secondary"]
                ),
                "topics": [
                    {
                        "slug": topic["slug"],
                        "title": topic["title"],
                        "level": topic["level"],
                        "classes": topic["classes"],
                        "emoji": topic["emoji"],
                    }
                    for topic in TOPICS
                    if topic["subject"] == subject
                ],
            }
        )
    return jsonify({"classes": classes, "subjects": subjects, "total_topics": len(TOPICS)})
