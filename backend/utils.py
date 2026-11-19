"""Small shared helpers for API responses."""
from datetime import datetime, timezone

from bson import ObjectId


def now():
    return datetime.now(timezone.utc)


def to_object_id(value):
    """Return an ObjectId or None when the value is not valid."""
    try:
        return ObjectId(str(value))
    except Exception:
        return None


def round1(value):
    """Round a number to one decimal place, safely."""
    try:
        return round(float(value), 1)
    except (TypeError, ValueError):
        return None


def json_safe(value):
    """
    Recursively convert MongoDB types into JSON-friendly values.

    pymongo returns ObjectId and datetime objects that Flask cannot always
    serialise, so every route uses this before jsonify().
    """
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def serialize_result(result, include_answers=False):
    """Shape a completed learning result document for the API."""
    data = {
        "id": str(result["_id"]),
        "session_id": result.get("session_id"),
        "student_id": result.get("student_id"),
        "student_name": result.get("student_name"),
        "class_level": result.get("class_level"),
        "subject": result.get("subject"),
        "topic_slug": result.get("topic_slug"),
        "topic": result.get("topic_title") or result.get("topic"),
        "score": result.get("score"),
        "total": result.get("total"),
        "percentage": result.get("percentage"),
        "category": result.get("category"),
        "suggestions": json_safe(result.get("suggestions", [])),
        "weak_topics": json_safe(result.get("weak_topics", [])),
        "is_demo": bool(result.get("is_demo")),
        "created_at": json_safe(result.get("created_at")),
    }
    if include_answers:
        data["answers"] = json_safe(result.get("answers", []))
        data["difficulty_path"] = json_safe(result.get("difficulty_path", []))
    return data


def serialize_question(question, include_answer=False):
    """Return a quiz question without leaking the answer by default."""
    data = {
        "id": question.get("id"),
        "topic_slug": question.get("topic_slug"),
        "question": question.get("question"),
        "options": question.get("options", []),
        "difficulty": question.get("difficulty"),
    }
    if include_answer:
        data["correct_index"] = question.get("correct_index")
        data["explanation"] = question.get("explanation")
        data["simpler_example"] = question.get("simpler_example")
    return data
