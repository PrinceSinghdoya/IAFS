"""Student dashboard, progress and result review routes."""
from flask import Blueprint, g, jsonify, request

from auth_utils import public_user, require_auth
from curriculum import SUBJECTS, TOPIC_BY_SLUG, level_for_class
from db import get_db
from services.analytics import (
    student_learning_summary,
    student_streak,
    subject_progress_for_student,
    topic_progress_for_student,
)
from services.feedback_engine import (
    build_snapshot,
    ensure_feedback,
    serialize_feedback,
)
from utils import json_safe, serialize_result, to_object_id

student_bp = Blueprint("student", __name__)


def _recommendations(snapshot, limit=3):
    """Real recommendations based on weak topics and untouched topics."""
    items = []
    for row in snapshot["focus_topics"]:
        items.append(
            {
                "slug": row["slug"],
                "title": row["title"],
                "subject": row["subject"],
                "emoji": row["emoji"],
                "icon": row.get("icon"),
                "reason": f"Your average here is {row['average']}% - a short review will help.",
                "action": "Revise topic",
            }
        )
    for row in snapshot["not_started"]:
        if len(items) >= limit:
            break
        items.append(
            {
                "slug": row["slug"],
                "title": row["title"],
                "subject": row["subject"],
                "emoji": row["emoji"],
                "icon": row.get("icon"),
                "reason": "You have not tried this topic yet.",
                "action": "Start learning",
            }
        )
    for row in snapshot["strengths"]:
        if len(items) >= limit:
            break
        items.append(
            {
                "slug": row["slug"],
                "title": row["title"],
                "subject": row["subject"],
                "emoji": row["emoji"],
                "icon": row.get("icon"),
                "reason": f"You are strong here ({row['average']}%). Try a harder quiz.",
                "action": "Challenge me",
            }
        )
    return items[:limit]


@student_bp.get("/student/dashboard")
@require_auth("student")
def dashboard():
    """
    Everything the student dashboard needs, computed from live MongoDB data.
    No numbers here are hardcoded.
    """
    db = get_db()
    snapshot = build_snapshot(g.user_id, student=g.user)
    feedback = ensure_feedback(g.user_id)
    summary = student_learning_summary(g.user_id)
    subjects = subject_progress_for_student(g.user_id, g.user.get("class_level"))
    recent_results = [
        serialize_result(result)
        for result in db.learning_results.find({"student_id": g.user_id})
        .sort("created_at", -1)
        .limit(4)
    ]
    latest_message = db.class_messages.find_one(
        {
            "$or": [
                {"class_level": g.user.get("class_level")},
                {"class_level": None},
            ]
        },
        sort=[("created_at", -1)],
    )
    recommendations = _recommendations(snapshot)
    continue_learning = None
    if recent_results:
        latest = recent_results[0]
        topic = TOPIC_BY_SLUG.get(latest.get("topic_slug") or "")
        if topic and (latest.get("percentage") or 0) < 85:
            continue_learning = {
                "slug": topic["slug"],
                "title": topic["title"],
                "subject": topic["subject"],
                "emoji": topic["emoji"],
                "icon": topic["icon"],
                "reason": f"Your last quiz scored {latest.get('percentage')}%. A short review will help.",
                "action": "Practise again",
                "last_result_id": latest.get("id"),
                "last_percentage": latest.get("percentage"),
                "last_attempt": latest.get("created_at"),
            }
    if continue_learning is None and recommendations:
        item = recommendations[0]
        continue_learning = {
            **item,
            "last_result_id": None,
            "last_percentage": None,
            "last_attempt": None,
        }

    return jsonify(
        {
            "user": public_user(g.user),
            "class_level": g.user.get("class_level"),
            "level": level_for_class(g.user.get("class_level") or 1),
            "summary": summary,
            "subjects": subjects,
            "recent_results": recent_results,
            "recommendations": recommendations,
            "continue_learning": continue_learning,
            "feedback": serialize_feedback(feedback),
            "streak_days": student_streak(g.user_id),
            "latest_message": json_safe(latest_message),
            "subjects_available": SUBJECTS,
        }
    )


@student_bp.get("/student/progress")
@require_auth("student")
def progress():
    """Detailed subject/topic progress plus full result history."""
    db = get_db()
    snapshot = build_snapshot(g.user_id, student=g.user)
    history = list(
        db.learning_results.find({"student_id": g.user_id})
        .sort("created_at", -1)
        .limit(50)
    )
    return jsonify(
        {
            "summary": student_learning_summary(g.user_id),
            "subjects": snapshot["subjects"],
            "topics": snapshot["topics"],
            "strengths": snapshot["strengths"],
            "focus_topics": snapshot["focus_topics"],
            "results": [serialize_result(result) for result in history],
            "streak_days": snapshot["streak_days"],
            "class_level": g.user.get("class_level"),
        }
    )


@student_bp.get("/student/results")
@require_auth("student")
def results():
    db = get_db()
    subject = request.args.get("subject")
    query = {"student_id": g.user_id}
    if subject in SUBJECTS:
        query["subject"] = subject
    rows = list(
        db.learning_results.find(query).sort("created_at", -1).limit(60)
    )
    return jsonify({"results": [serialize_result(row) for row in rows]})


@student_bp.get("/student/results/<result_id>")
@require_auth(["student", "teacher", "admin"])
def result_detail(result_id):
    db = get_db()
    query = {"_id": to_object_id(result_id)}
    if g.user.get("role") == "student":
        query["student_id"] = g.user_id
    result = db.learning_results.find_one(query)
    if not result:
        return jsonify({"error": "Result not found"}), 404
    return jsonify({"result": serialize_result(result, include_answers=True)})


@student_bp.get("/student/topics/<slug>")
@require_auth("student")
def topic_progress(slug):
    topic = TOPIC_BY_SLUG.get(slug)
    if not topic:
        return jsonify({"error": "Topic not found"}), 404
    rows = topic_progress_for_student(g.user_id, g.user.get("class_level"))
    row = next((item for item in rows if item["slug"] == slug), None)
    history = list(
        get_db()
        .learning_results.find({"student_id": g.user_id, "topic_slug": slug})
        .sort("created_at", -1)
        .limit(10)
    )
    return jsonify(
        {
            "topic": {"slug": topic["slug"], "title": topic["title"], "subject": topic["subject"]},
            "progress": row,
            "results": [serialize_result(item) for item in history],
        }
    )
