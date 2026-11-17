"""Subjects, topics and lesson content for Classes 1-10."""
from flask import Blueprint, g, jsonify, request
from statistics import mean

from auth_utils import require_auth
from curriculum import (
    CLASS_LEVELS,
    SUBJECTS,
    SUBJECT_INFO,
    TOPIC_BY_SLUG,
    TOPICS,
    level_for_class,
    practice_questions,
    topic_document,
    topics_for_class,
)
from db import get_db
from services.feedback_engine import topic_rows_for_student
from utils import json_safe, round1

content_bp = Blueprint("content", __name__)


def _requested_class(user, param="class_level"):
    """Students are always limited to their own class."""
    if user.get("role") == "student":
        return int(user.get("class_level") or 1)
    try:
        value = int(request.args.get(param) or 0)
    except (TypeError, ValueError):
        return None
    return value if value in CLASS_LEVELS else None


def _topic_summary(topic, class_level, progress=None):
    data = {
        "slug": topic["slug"],
        "title": topic["title"],
        "subject": topic["subject"],
        "level": topic["level"],
        "icon": topic["icon"],
        "emoji": topic["emoji"],
        "order": topic["order"],
        "description": topic["description"],
        "estimated_minutes": 7 if topic["level"] == "Primary" else 10,
        "class_tip": (topic.get("class_tips") or {}).get(str(class_level), ""),
    }
    if progress:
        data.update(
            {
                "attempts": progress.get("attempts", 0),
                "best": progress.get("best"),
                "latest": progress.get("latest"),
                "average": progress.get("average"),
                "status": progress.get("status", "Not started"),
                "last_attempt_at": progress.get("last_attempt_at"),
            }
        )
    else:
        data.update(
            {
                "attempts": 0,
                "best": None,
                "latest": None,
                "average": None,
                "status": "Not started",
                "last_attempt_at": None,
            }
        )
    return data


@content_bp.get("/subjects")
@require_auth()
def list_subjects():
    """The two subjects with class-aware topic counts and progress."""
    class_level = _requested_class(g.user)
    if g.user.get("role") == "student" and not class_level:
        class_level = int(g.user.get("class_level") or 1)
    progress_rows = []
    if g.user.get("role") == "student":
        progress_rows = topic_rows_for_student(g.user_id, class_level)

    subjects = []
    for subject in SUBJECTS:
        info = SUBJECT_INFO[subject]
        topics = topics_for_class(class_level or 1, subject) if class_level else [
            topic for topic in TOPICS if topic["subject"] == subject
        ]
        subject_progress = [
            row for row in progress_rows if row["subject"] == subject and row["attempts"]
        ]
        averages = [row["average"] for row in subject_progress if row["average"] is not None]
        subjects.append(
            {
                "name": subject,
                "emoji": info["emoji"],
                "icon": info["icon"],
                "colour": info["colour"],
                "tagline": info["tagline"],
                "description": info["description"],
                "topics_total": len(topics),
                "topics_started": len(subject_progress),
                "average": round1(mean(averages)) if averages else None,
                "best": round1(max(row["best"] for row in subject_progress))
                if subject_progress
                else None,
            }
        )
    return jsonify(
        {
            "subjects": subjects,
            "class_level": class_level,
            "level": level_for_class(class_level) if class_level else None,
            "classes": CLASS_LEVELS,
        }
    )


@content_bp.get("/topics")
@require_auth()
def list_topics():
    """Topics for a class, optionally filtered by subject or search text."""
    class_level = _requested_class(g.user)
    subject = request.args.get("subject")
    search = (request.args.get("search") or "").strip().lower()

    progress_rows = []
    if g.user.get("role") == "student":
        progress_rows = topic_rows_for_student(g.user_id, class_level)
    progress_by_slug = {row["slug"]: row for row in progress_rows}

    if class_level:
        topics = topics_for_class(class_level, subject if subject in SUBJECTS else None)
    else:
        topics = [
            topic
            for topic in TOPICS
            if not subject or subject == topic["subject"]
        ]
        topics.sort(key=lambda item: (item["subject"], item["level"], item["order"]))

    if search:
        topics = [
            topic
            for topic in topics
            if search in topic["title"].lower() or search in topic["description"].lower()
        ]

    return jsonify(
        {
            "topics": [
                _topic_summary(topic, class_level or 1, progress_by_slug.get(topic["slug"]))
                for topic in topics
            ],
            "class_level": class_level,
            "level": level_for_class(class_level) if class_level else None,
        }
    )


@content_bp.get("/topics/<slug>")
@require_auth()
def get_topic(slug):
    """Full lesson content, class tip and practice questions with answers."""
    topic = TOPIC_BY_SLUG.get(slug)
    if not topic:
        return jsonify({"error": "Topic not found"}), 404

    class_level = int(g.user.get("class_level") or 1)
    if g.user.get("role") == "student" and topic["level"] != level_for_class(class_level):
        return jsonify({"error": "This topic is for a different class group"}), 403
    if g.user.get("role") != "student":
        try:
            requested = int(request.args.get("class_level") or 0)
            if requested in CLASS_LEVELS:
                class_level = requested
        except (TypeError, ValueError):
            pass

    document = topic_document(topic, class_level)
    document["practice"] = [
        {
            "id": question["id"],
            "question": question["question"],
            "options": question["options"],
            "correct_index": question["correct_index"],
            "explanation": question["explanation"],
            "difficulty": question["difficulty"],
        }
        for question in practice_questions(slug, class_level, count=2)
    ]
    document["class_tip"] = (topic.get("class_tips") or {}).get(str(class_level), "")

    if g.user.get("role") == "student":
        rows = topic_rows_for_student(g.user_id, class_level)
        row = next((item for item in rows if item["slug"] == slug), None)
        document["progress"] = row
        document["recent_results"] = json_safe(
            list(
                get_db()
                .learning_results.find({"student_id": g.user_id, "topic_slug": slug})
                .sort("created_at", -1)
                .limit(3)
            )
        )
    return jsonify({"topic": document, "class_level": class_level})


@content_bp.get("/curriculum")
@require_auth(["teacher", "admin"])
def get_curriculum():
    """Full curriculum catalogue for staff and admin screens."""
    grouped = []
    for subject in SUBJECTS:
        for level in ("Primary", "Secondary"):
            topics = [
                topic
                for topic in TOPICS
                if topic["subject"] == subject and topic["level"] == level
            ]
            grouped.append(
                {
                    "subject": subject,
                    "level": level,
                    "classes": list(range(1, 6)) if level == "Primary" else list(range(6, 11)),
                    "topics": [_topic_summary(topic, 1) for topic in topics],
                }
            )
    return jsonify({"groups": grouped, "total_topics": len(TOPICS)})
