"""Student-facing adaptive feedback routes."""
from flask import Blueprint, g, jsonify

from auth_utils import require_auth
from db import get_db
from services.feedback_engine import (
    CATEGORY_ORDER,
    build_snapshot,
    ensure_feedback,
    generate_feedback,
    serialize_feedback,
)
from utils import json_safe

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.get("/feedback")
@require_auth("student")
def get_feedback():
    """Latest feedback plus history for the feedback page."""
    latest = ensure_feedback(g.user_id)
    history = list(
        get_db()
        .adaptive_feedback.find({"student_id": g.user_id, "source": "engine"})
        .sort("created_at", -1)
        .limit(20)
    )

    return jsonify(
        {
            "latest": serialize_feedback(latest),
            "history": [serialize_feedback(record) for record in history],
            "categories": CATEGORY_ORDER,
            "explanation": (
                "Your category is chosen from rules that combine your quiz scores, "
                "topic coverage and the number of questions you answer correctly. "
                "Class chat is only an optional supporting signal; it is never used "
                "to judge your emotions or your ability."
            ),
        }
    )


@feedback_bp.post("/feedback/refresh")
@require_auth("student")
def refresh_feedback():
    """Recalculate feedback from the latest evidence."""
    snapshot = build_snapshot(g.user_id, student=g.user)
    record = generate_feedback(g.user_id, snapshot=snapshot, persist=True)
    return jsonify({"latest": serialize_feedback(record), "snapshot": json_safe(snapshot)}), 201
