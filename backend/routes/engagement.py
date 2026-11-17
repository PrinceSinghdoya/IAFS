"""
Optional, privacy-safe focus checks.

The browser processes camera frames locally with MediaPipe. Only aggregate
numbers are sent here: how often a face was visible, how often the head was
roughly centred and how long the check lasted. No images, video, facial
templates, identity data or emotion labels are uploaded or stored.

These numbers never affect a quiz score or the adaptive feedback category.
"""
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

from auth_utils import require_auth
from db import get_db
from utils import json_safe

engagement_bp = Blueprint("engagement", __name__)


def indicator_from_score(score):
    if score >= 75:
        return "Face visible and centred"
    if score >= 45:
        return "Partly visible"
    return "Low signal"


def serialize_record(record):
    if not record:
        return None
    centered = record.get("centered_ratio", record.get("head_centered_ratio"))
    return {
        "id": str(record["_id"]),
        "student_id": record.get("student_id"),
        "student_name": record.get("student_name"),
        "session_seconds": record.get("session_seconds"),
        "face_ratio": record.get("face_ratio"),
        "centered_ratio": centered,
        "head_centered_ratio": centered,
        "focus_score": record.get("focus_score", record.get("engagement_score")),
        "engagement_score": record.get("focus_score", record.get("engagement_score")),
        "indicator": record.get("indicator"),
        "source": record.get("source"),
        "created_at": json_safe(record.get("created_at")),
    }


@engagement_bp.post("/engagement")
@require_auth("student")
def save_focus_session():
    """
    Save one aggregated focus check.

    Camera body:
      {source: "camera", session_seconds: 120, total_samples: 100,
       face_detected_samples: 86, head_centered_samples: 61}

    Manual fallback body:
      {source: "manual", session_seconds: 120, focus_level: 4}
    """
    data = request.get_json(silent=True) or {}
    source = (data.get("source") or "camera").lower()
    if source not in {"camera", "manual"}:
        return jsonify({"error": "Invalid session source"}), 400

    try:
        session_seconds = int(data.get("session_seconds", 0) or 0)
    except (TypeError, ValueError):
        session_seconds = 0
    session_seconds = max(0, min(session_seconds, 7200))

    if source == "manual":
        try:
            focus_level = int(data.get("focus_level", 3) or 3)
        except (TypeError, ValueError):
            focus_level = 3
        focus_level = max(1, min(focus_level, 5))
        score = float(focus_level * 20)
        face_ratio = None
        centered_ratio = None
    else:
        try:
            total = int(data.get("total_samples", 0) or 0)
            face_samples = int(data.get("face_detected_samples", 0) or 0)
            centered_samples = int(data.get("head_centered_samples", 0) or 0)
        except (TypeError, ValueError):
            return jsonify({"error": "Camera samples must be numbers"}), 400
        if total <= 0:
            return jsonify({"error": "No camera samples were received"}), 400

        face_samples = max(0, min(face_samples, total))
        centered_samples = max(0, min(centered_samples, total))
        face_ratio = round(face_samples / total * 100, 1)
        centered_ratio = round(centered_samples / total * 100, 1)
        score = round(face_ratio * 0.7 + centered_ratio * 0.3, 1)

    record = {
        "student_id": g.user_id,
        "student_name": g.user.get("name"),
        "class_level": g.user.get("class_level"),
        "session_seconds": session_seconds,
        "face_ratio": face_ratio,
        "centered_ratio": centered_ratio,
        "focus_score": score,
        "indicator": indicator_from_score(score),
        "source": source,
        "created_at": datetime.now(timezone.utc),
    }
    record["_id"] = get_db().focus_sessions.insert_one(record).inserted_id

    return (
        jsonify(
            {
                "message": "Focus check saved",
                "record": serialize_record(record),
                "note": (
                    "Focus checks are optional and stored as aggregate numbers "
                    "only. They are never used to grade you or to judge your "
                    "emotions."
                ),
            }
        ),
        201,
    )


@engagement_bp.get("/engagement/latest")
@require_auth("student")
def latest_focus_session():
    """Latest focus check plus short history for the optional camera page."""
    db = get_db()
    latest = db.focus_sessions.find_one(
        {"student_id": g.user_id}, sort=[("created_at", -1)]
    )
    history = list(
        db.focus_sessions.find({"student_id": g.user_id})
        .sort("created_at", -1)
        .limit(10)
    )
    return jsonify(
        {
            "latest": serialize_record(latest),
            "history": [serialize_record(record) for record in history],
            "note": (
                "Camera use is optional and off by default. The browser only "
                "sends counts of face presence and head position. No images, "
                "video, identity or emotion data are stored."
            ),
        }
    )
