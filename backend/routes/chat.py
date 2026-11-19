"""Class-scoped classroom chat for students and teachers."""
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

from auth_utils import require_auth
from curriculum import CLASS_LEVELS, level_for_class
from db import get_db
from services.sentiment import analyze_message
from utils import json_safe

chat_bp = Blueprint("chat", __name__)

MAX_MESSAGE_LENGTH = 600


def _clean_class(value):
    try:
        class_level = int(value)
    except (TypeError, ValueError):
        return None
    return class_level if class_level in CLASS_LEVELS else None


def serialize_message(message):
    return {
        "id": str(message["_id"]),
        "student_id": message.get("student_id"),
        "student_name": message.get("student_name"),
        "role": message.get("role", "student"),
        "class_level": message.get("class_level"),
        "is_teacher": bool(message.get("is_teacher")),
        "text": message.get("text"),
        "analysis": json_safe(message.get("analysis")),
        "is_demo": bool(message.get("is_demo")),
        "created_at": json_safe(message.get("created_at")),
    }


@chat_bp.get("/chat/messages")
@require_auth()
def list_messages():
    """
    Return the latest messages for the signed-in user's class.

    Students only ever see their own class and whole-school notices.
    Teachers can filter by class_level; staff also see notices.
    """
    try:
        limit = int(request.args.get("limit", 60) or 60)
    except (TypeError, ValueError):
        limit = 60
    limit = max(1, min(limit, 100))
    query = {}
    if g.user.get("role") == "student":
        class_level = g.user.get("class_level")
        query = {"$or": [{"class_level": class_level}, {"class_level": None}]}
    else:
        requested = _clean_class(request.args.get("class_level"))
        if requested:
            query = {"class_level": requested}

    messages = list(
        get_db().class_messages.find(query).sort("created_at", -1).limit(limit)
    )
    messages.reverse()
    return jsonify(
        {
            "messages": [serialize_message(message) for message in messages],
            "class_level": g.user.get("class_level"),
            "level": level_for_class(g.user.get("class_level") or 1),
        }
    )


@chat_bp.post("/chat/messages")
@require_auth()
def send_message():
    """Post a class message. Student text gets a light, private help signal."""
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Message cannot be empty"}), 400
    if len(text) > MAX_MESSAGE_LENGTH:
        return (
            jsonify({"error": f"Message must be under {MAX_MESSAGE_LENGTH} characters"}),
            400,
        )

    role = g.user.get("role")
    is_teacher = role in {"teacher", "admin"}
    if is_teacher:
        class_level = _clean_class(data.get("class_level"))
        if class_level is None and role == "teacher":
            class_level = g.user.get("class_level")
        # None means a whole-school notice from staff.
    else:
        class_level = g.user.get("class_level")
        if not class_level:
            return jsonify({"error": "Choose your class before joining class chat"}), 400

    analysis = None if is_teacher else analyze_message(text, class_level)
    message = {
        "student_id": g.user_id,
        "student_name": g.user.get("name"),
        "role": role,
        "class_level": class_level,
        "is_teacher": is_teacher,
        "text": text,
        "analysis": analysis,
        "created_at": datetime.now(timezone.utc),
    }
    message["_id"] = get_db().class_messages.insert_one(message).inserted_id

    return jsonify({"message": serialize_message(message)}), 201


@chat_bp.get("/chat/my-analysis")
@require_auth("student")
def my_analysis():
    """Private summary of the student's own messages for a small sidebar."""
    chats = list(
        get_db()
        .class_messages.find(
            {"student_id": g.user_id, "is_teacher": {"$ne": True}}
        )
        .sort("created_at", -1)
        .limit(10)
    )
    analyses = [chat.get("analysis") for chat in chats if chat.get("analysis")]
    return jsonify(
        {
            "messages_analyzed": len(analyses),
            "difficulty_signals": sum(
                1 for item in analyses if item.get("learning_difficulty") == "Possible"
            ),
            "topics": list(
                {
                    item.get("subtopic")
                    for item in analyses
                    if item.get("learning_difficulty") == "Possible"
                    and item.get("subtopic")
                }
            ),
            "recent": [
                {
                    "text": chat.get("text"),
                    "analysis": json_safe(chat.get("analysis")),
                    "created_at": json_safe(chat.get("created_at")),
                }
                for chat in chats[:5]
            ],
            "note": (
                "This is a rough text signal from a few word patterns. It is "
                "not emotion detection, and only you and your teacher can see it."
            ),
        }
    )
