"""Teacher dashboard, class analytics and individual student reports."""
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

from auth_utils import public_user, require_auth
from curriculum import CLASS_LEVELS, SUBJECTS, level_for_class
from db import get_db
from services.analytics import (
    class_performance,
    feedback_categories,
    focus_summary,
    recent_activity,
    score_distribution,
    subject_performance,
    teacher_student_rows,
    topic_performance_overall,
    weak_topics_overall,
)
from services.feedback_engine import (
    build_snapshot,
    generate_feedback,
    serialize_feedback,
)
from utils import json_safe, serialize_result, to_object_id

teacher_bp = Blueprint("teacher", __name__)


def _class_param():
    try:
        value = int(request.args.get("class_level") or 0)
    except (TypeError, ValueError):
        return None
    return value if value in CLASS_LEVELS else None


@teacher_bp.get("/teacher/dashboard")
@require_auth(["teacher", "admin"])
def teacher_dashboard():
    """
    Every number on the teacher dashboard comes from real MongoDB records.
    """
    db = get_db()
    students = teacher_student_rows()
    results = list(db.learning_results.find({}))
    scores = [result.get("percentage", 0) for result in results]
    participating = [row for row in students if row["attempts"]]
    top_students = sorted(
        participating, key=lambda row: row["average"] or 0, reverse=True
    )[:5]
    focus_students = sorted(
        participating, key=lambda row: row["average"] or 0
    )[:5]

    return jsonify(
        {
            "summary": {
                "students": len(students),
                "students_active": len(participating),
                "attempts": len(results),
                "average": round(sum(scores) / len(scores), 1) if scores else None,
                "weak_topics": len(weak_topics_overall(limit=99)),
                "classes_with_students": len(
                    {row["class_level"] for row in students if row["class_level"]}
                ),
            },
            "classes": class_performance(),
            "subjects": subject_performance(),
            "weak_topics": weak_topics_overall(limit=6),
            "feedback_categories": feedback_categories(students),
            "score_distribution": score_distribution(),
            "recent_activity": json_safe(recent_activity(limit=8)),
            "top_students": top_students,
            "students_needing_support": focus_students,
        }
    )


@teacher_bp.get("/teacher/students")
@require_auth(["teacher", "admin"])
def teacher_students():
    """Filterable list of students with real performance rows."""
    class_level = _class_param()
    subject = request.args.get("subject")
    if subject not in SUBJECTS:
        subject = None
    search = request.args.get("search")
    rows = teacher_student_rows(class_level=class_level, subject=subject, search=search)
    return jsonify(
        {
            "students": rows,
            "total": len(rows),
            "classes": CLASS_LEVELS,
            "subjects": SUBJECTS,
        }
    )


@teacher_bp.get("/teacher/students/<student_id>")
@require_auth(["teacher", "admin"])
def teacher_student_detail(student_id):
    """Individual report: performance, feedback, notes, focus and class chat."""
    db = get_db()
    object_id = to_object_id(student_id)
    student = db.users.find_one({"_id": object_id, "role": "student"}) if object_id else None
    if not student:
        return jsonify({"error": "Student not found"}), 404

    snapshot = build_snapshot(str(student["_id"]), student=student)
    results = list(
        db.learning_results.find({"student_id": str(student["_id"])})
        .sort("created_at", -1)
        .limit(40)
    )
    notes = list(
        db.teacher_notes.find({"student_id": str(student["_id"])})
        .sort("created_at", -1)
        .limit(20)
    )
    latest_feedback = db.adaptive_feedback.find_one(
        {"student_id": str(student["_id"])},
        sort=[("created_at", -1)],
    )
    if not latest_feedback:
        latest_feedback = generate_feedback(
            str(student["_id"]), snapshot=snapshot, persist=False
        )
    messages = list(
        db.class_messages.find(
            {"student_id": str(student["_id"])}
        )
        .sort("created_at", -1)
        .limit(10)
    )

    return jsonify(
        {
            "student": public_user(student),
            "summary": {
                "attempts": snapshot["attempts"],
                "average": snapshot["average"],
                "best": snapshot["best"],
                "category": snapshot["category"],
                "topics_started": len([row for row in snapshot["topics"] if row["attempts"]]),
                "topics_total": len(snapshot["topics"]),
                "streak_days": snapshot["streak_days"],
                "trend": snapshot["trend"],
                "last_activity": snapshot["last_activity"],
            },
            "subjects": snapshot["subjects"],
            "topics": snapshot["topics"],
            "strengths": snapshot["strengths"],
            "focus_topics": snapshot["focus_topics"],
            "results": [serialize_result(result) for result in results],
            "feedback": serialize_feedback(latest_feedback),
            "notes": [
                {
                    "id": str(note["_id"]),
                    "note": note.get("note"),
                    "teacher_name": note.get("teacher_name"),
                    "created_at": json_safe(note.get("created_at")),
                }
                for note in notes
            ],
            "focus": focus_summary(str(student["_id"])),
            "messages": [
                {
                    "id": str(message["_id"]),
                    "text": message.get("text"),
                    "role": message.get("role"),
                    "created_at": json_safe(message.get("created_at")),
                }
                for message in messages
            ],
        }
    )


@teacher_bp.post("/teacher/notes")
@require_auth(["teacher", "admin"])
def add_note():
    """Add a private teacher note about a student."""
    data = request.get_json(silent=True) or {}
    student_id = to_object_id(data.get("student_id"))
    note_text = (data.get("note") or "").strip()
    if not student_id:
        return jsonify({"error": "Student is required"}), 400
    if not note_text:
        return jsonify({"error": "Please write a note"}), 400
    student = get_db().users.find_one({"_id": student_id, "role": "student"})
    if not student:
        return jsonify({"error": "Student not found"}), 404
    note = {
        "student_id": str(student_id),
        "student_name": student.get("name"),
        "teacher_id": g.user_id,
        "teacher_name": g.user.get("name"),
        "note": note_text[:1000],
        "created_at": datetime.now(timezone.utc),
    }
    note["_id"] = get_db().teacher_notes.insert_one(note).inserted_id
    return jsonify(
        {
            "note": {
                "id": str(note["_id"]),
                "note": note["note"],
                "teacher_name": note["teacher_name"],
                "created_at": json_safe(note["created_at"]),
            }
        }
    ), 201


@teacher_bp.get("/teacher/classes")
@require_auth(["teacher", "admin"])
def classes():
    """Class-wise performance for the classes overview."""
    return jsonify(
        {
            "classes": class_performance(),
            "subjects": subject_performance(),
            "levels": {"Primary": list(range(1, 6)), "Secondary": list(range(6, 11))},
        }
    )


@teacher_bp.get("/teacher/topics")
@require_auth(["teacher", "admin"])
def topics():
    """Topic performance, optionally filtered by class."""
    class_level = _class_param()
    rows = topic_performance_overall(class_level)
    return jsonify(
        {
            "topics": rows,
            "weak_topics": [row for row in rows if row["attempts"] and row["status"] == "Needs attention"],
            "class_level": class_level,
        }
    )
