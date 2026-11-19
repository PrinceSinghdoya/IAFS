"""Shared read-only analytics used by student, teacher and admin dashboards."""
from datetime import datetime, timedelta, timezone
from statistics import mean

from curriculum import CLASS_LEVELS, SUBJECTS, TOPICS, TOPIC_BY_SLUG, level_for_class, topics_for_class
from db import get_db
from services.feedback_engine import (
    CATEGORY_ORDER,
    build_snapshot,
    decide_category,
    learning_streak,
    results_for_student,
    subject_rows_for_student,
    topic_rows_for_student,
)
from utils import round1


def student_learning_summary(student_id):
    """Compact metrics block used on dashboards."""
    snapshot = build_snapshot(student_id)
    return {
        "attempts": snapshot["attempts"],
        "average": snapshot["average"],
        "best": snapshot["best"],
        "topics_started": len([row for row in snapshot["topics"] if row["attempts"]]),
        "topics_total": len(snapshot["topics"]),
        "strong_topics": len(snapshot["strengths"]),
        "focus_topics": len(snapshot["focus_topics"]),
        "streak_days": snapshot["streak_days"],
        "trend": snapshot["trend"],
        "last_activity": snapshot["last_activity"],
        "recent_scores": snapshot["recent_scores"],
        "subject_averages": {
            row["subject"]: row["average"] for row in snapshot["subjects"]
        },
        "category": snapshot["category"],
    }


def topic_progress_for_student(student_id, class_level=None):
    return topic_rows_for_student(student_id, class_level)


def subject_progress_for_student(student_id, class_level=None):
    return subject_rows_for_student(student_id, class_level)


def student_streak(student_id):
    return learning_streak(student_id)


def _student_rows():
    return list(
        get_db()
        .users.find({"role": "student", "is_active": {"$ne": False}})
        .sort([("class_level", 1), ("name", 1)])
    )


def teacher_student_rows(class_level=None, subject=None, search=None):
    """One row per student with real performance data."""
    students = _student_rows()
    search_text = (search or "").strip().lower()
    rows = []
    for student in students:
        student_class = student.get("class_level")
        if class_level and student_class != int(class_level):
            continue
        if search_text and search_text not in (student.get("name") or "").lower() and search_text not in (
            student.get("email") or ""
        ).lower():
            continue

        snapshot = build_snapshot(str(student["_id"]), student=student)
        if subject:
            subject_row = next(
                (row for row in snapshot["subjects"] if row["subject"] == subject),
                None,
            )
            if not subject_row or subject_row["topics_started"] == 0:
                continue
            attempts = sum(
                topic["attempts"] for topic in subject_row["topics"]
            )
            average = subject_row["average"]
            best = subject_row["best"]
            focus_topic = next(
                (
                    topic
                    for topic in subject_row["topics"]
                    if topic["attempts"] and topic["average"] is not None and topic["average"] < 60
                ),
                None,
            )
            topics_started = subject_row["topics_started"]
            topics_total = subject_row["topics_total"]
        else:
            attempts = snapshot["attempts"]
            average = snapshot["average"]
            best = snapshot["best"]
            focus_topic = snapshot["focus_topics"][0] if snapshot["focus_topics"] else None
            topics_started = len([row for row in snapshot["topics"] if row["attempts"]])
            topics_total = len(snapshot["topics"])

        rows.append(
            {
                "id": str(student["_id"]),
                "name": student.get("name"),
                "email": student.get("email"),
                "class_level": student_class,
                "level": level_for_class(student_class) if student_class else None,
                "section": student.get("section"),
                "roll_no": student.get("roll_no"),
                "attempts": attempts,
                "average": average,
                "best": best,
                "topics_started": topics_started,
                "topics_total": topics_total,
                "category": decide_category(average),
                "trend": snapshot["trend"],
                "last_activity": snapshot["last_activity"],
                "focus_topic": focus_topic["title"] if focus_topic else None,
                "focus_percentage": focus_topic["average"] if focus_topic else None,
                "streak_days": snapshot["streak_days"],
                "is_demo": bool(student.get("is_demo")),
            }
        )
    rows.sort(key=lambda row: (row["class_level"] or 0, row["name"] or ""))
    return rows


def feedback_categories(rows=None):
    """Count students in each feedback category from their real averages."""
    rows = rows if rows is not None else teacher_student_rows()
    counts = {category: 0 for category in CATEGORY_ORDER}
    for row in rows:
        category = row.get("category") or decide_category(row.get("average"))
        counts[category] = counts.get(category, 0) + 1
    total = sum(counts.values())
    return [
        {
            "category": category,
            "count": counts[category],
            "percentage": round1(counts[category] * 100 / total) if total else 0,
        }
        for category in CATEGORY_ORDER
    ]


def class_performance():
    """Class-wise summary computed from real users and results."""
    db = get_db()
    students = _student_rows()
    results = list(db.learning_results.find({}))
    rows = []
    for class_level in CLASS_LEVELS:
        class_students = [item for item in students if item.get("class_level") == class_level]
        ids = {str(item["_id"]) for item in class_students}
        class_results = [
            result
            for result in results
            if str(result.get("student_id")) in ids
        ]
        scores = [result.get("percentage", 0) for result in class_results]
        rows.append(
            {
                "class_level": class_level,
                "level": level_for_class(class_level),
                "students": len(class_students),
                "active_students": len(
                    {str(result.get("student_id")) for result in class_results}
                ),
                "attempts": len(class_results),
                "average": round1(mean(scores)) if scores else None,
                "best": round1(max(scores)) if scores else None,
            }
        )
    return rows


def subject_performance(class_level=None):
    """Subject-wide performance for one class or the whole school."""
    db = get_db()
    query = {}
    if class_level:
        query["class_level"] = int(class_level)
    results = list(db.learning_results.find(query))
    rows = []
    for subject in SUBJECTS:
        subject_results = [item for item in results if item.get("subject") == subject]
        scores = [item.get("percentage", 0) for item in subject_results]
        rows.append(
            {
                "subject": subject,
                "attempts": len(subject_results),
                "students": len({str(item.get("student_id")) for item in subject_results}),
                "average": round1(mean(scores)) if scores else None,
                "best": round1(max(scores)) if scores else None,
                "topics": len(
                    [topic for topic in TOPICS if topic["subject"] == subject]
                ),
            }
        )
    return rows


def topic_performance_overall(class_level=None):
    """Aggregate every topic so teachers can spot weak areas."""
    db = get_db()
    query = {}
    if class_level:
        query["class_level"] = int(class_level)
    results = list(db.learning_results.find(query))
    grouped = {}
    for result in results:
        grouped.setdefault(result.get("topic_slug"), []).append(result)

    rows = []
    for topic in TOPICS:
        if class_level and topic["level"] != level_for_class(class_level):
            continue
        topic_results = grouped.get(topic["slug"], [])
        scores = [item.get("percentage", 0) for item in topic_results]
        rows.append(
            {
                "slug": topic["slug"],
                "title": topic["title"],
                "subject": topic["subject"],
                "level": topic["level"],
                "attempts": len(topic_results),
                "students": len({str(item.get("student_id")) for item in topic_results}),
                "average": round1(mean(scores)) if scores else None,
                "best": round1(max(scores)) if scores else None,
                "status": (
                    "Not attempted"
                    if not scores
                    else "Needs attention" if mean(scores) < 60 else "On track"
                ),
            }
        )
    rows.sort(key=lambda row: (row["subject"], row["level"], row["title"]))
    return rows


def weak_topics_overall(limit=6, class_level=None):
    rows = [
        row
        for row in topic_performance_overall(class_level)
        if row["attempts"] and row["average"] is not None and row["average"] < 60
    ]
    rows.sort(key=lambda row: row["average"])
    return rows[:limit]


def recent_activity(limit=8):
    """Merge results, chat and focus records into one activity feed."""
    db = get_db()
    items = []
    for result in db.learning_results.find({}).sort("created_at", -1).limit(limit):
        items.append(
            {
                "type": "quiz",
                "title": f"{result.get('student_name')} completed {result.get('topic_title')}",
                "detail": f"Score {result.get('score')}/{result.get('total')} ({result.get('percentage')}%)",
                "created_at": result.get("created_at"),
                "class_level": result.get("class_level"),
                "is_demo": bool(result.get("is_demo")),
            }
        )
    for message in db.class_messages.find({}).sort("created_at", -1).limit(limit):
        items.append(
            {
                "type": "chat",
                "title": f"{message.get('student_name')} posted in class chat",
                "detail": (message.get("text") or "")[:110],
                "created_at": message.get("created_at"),
                "class_level": message.get("class_level"),
                "is_demo": bool(message.get("is_demo")),
            }
        )
    for record in db.focus_sessions.find({}).sort("created_at", -1).limit(limit):
        items.append(
            {
                "type": "focus",
                "title": f"{record.get('student_name')} saved a focus check",
                "detail": f"{record.get('session_seconds', 0)} seconds, {record.get('indicator', 'Low signal')}",
                "created_at": record.get("created_at"),
                "class_level": record.get("class_level"),
                "is_demo": bool(record.get("is_demo")),
            }
        )
    items.sort(key=lambda item: item.get("created_at") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return items[:limit]


def score_distribution(class_level=None):
    """Distribution used by the teacher dashboard chart."""
    query = {}
    if class_level:
        query["class_level"] = int(class_level)
    results = list(get_db().learning_results.find(query))
    buckets = [
        {"label": "Below 40", "min": 0, "max": 40, "count": 0},
        {"label": "40-59", "min": 40, "max": 60, "count": 0},
        {"label": "60-84", "min": 60, "max": 85, "count": 0},
        {"label": "85-100", "min": 85, "max": 101, "count": 0},
    ]
    for result in results:
        percentage = result.get("percentage", 0)
        for bucket in buckets:
            if bucket["min"] <= percentage < bucket["max"]:
                bucket["count"] += 1
                break
    return buckets


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _focus_average(records, key, fallback_key=None):
    """Average only numeric values; manual checks store no camera ratios."""
    values = []
    for record in records:
        value = record.get(key)
        if value is None and fallback_key:
            value = record.get(fallback_key)
        if _is_number(value):
            values.append(value)
    return round1(mean(values)) if values else None


def _attention_average(records):
    """Average stored attention estimates, with a fallback for older records."""
    values = []
    for record in records:
        value = record.get("attention_score")
        if not _is_number(value):
            face = record.get("face_ratio")
            centered = record.get("centered_ratio", record.get("head_centered_ratio"))
            candidates = [item for item in (face, centered) if _is_number(item)]
            value = min(candidates) if candidates else None
        if _is_number(value):
            values.append(float(value))
    return round1(mean(values)) if values else None


def focus_summary(student_id):
    """Aggregate optional focus checks. Never used to grade a student."""
    records = list(
        get_db().focus_sessions.find({"student_id": str(student_id)}).sort("created_at", -1)
    )
    if not records:
        return {
            "sessions": 0,
            "average_seconds": None,
            "face_visible": None,
            "head_centered": None,
            "attention": None,
            "last_session": None,
        }
    return {
        "sessions": len(records),
        "average_seconds": _focus_average(records, "session_seconds"),
        "face_visible": _focus_average(records, "face_ratio"),
        "head_centered": _focus_average(records, "centered_ratio", "head_centered_ratio"),
        "attention": _attention_average(records),
        "last_session": records[0].get("created_at"),
    }


def admin_overview():
    """School-wide counts for the administrator dashboard."""
    db = get_db()
    users = list(db.users.find({}))
    students = [user for user in users if user.get("role") == "student"]
    teachers = [user for user in users if user.get("role") == "teacher"]
    admins = [user for user in users if user.get("role") == "admin"]
    results = list(db.learning_results.find({}))
    scores = [result.get("percentage", 0) for result in results]
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_users = list(db.users.find({"created_at": {"$gte": week_ago}}).sort("created_at", -1).limit(6))
    recent_results = list(db.learning_results.find({"created_at": {"$gte": week_ago}}))

    class_counts = []
    for class_level in CLASS_LEVELS:
        count = len([student for student in students if student.get("class_level") == class_level])
        class_counts.append(
            {
                "class_level": class_level,
                "level": level_for_class(class_level),
                "students": count,
            }
        )
    return {
        "users": {
            "total": len(users),
            "students": len(students),
            "teachers": len(teachers),
            "admins": len(admins),
            "active": len([user for user in users if user.get("is_active") is not False]),
        },
        "content": {
            "subjects": len(SUBJECTS),
            "topics": len(TOPICS),
            "primary_topics": len([topic for topic in TOPICS if topic["level"] == "Primary"]),
            "secondary_topics": len([topic for topic in TOPICS if topic["level"] == "Secondary"]),
        },
        "learning": {
            "attempts": len(results),
            "average": round1(mean(scores)) if scores else None,
            "attempts_this_week": len(recent_results),
            "active_students": len({str(result.get("student_id")) for result in results}),
        },
        "class_counts": class_counts,
        "recent_users": [
            {
                "id": str(user["_id"]),
                "name": user.get("name"),
                "email": user.get("email"),
                "role": user.get("role"),
                "class_level": user.get("class_level"),
                "created_at": user.get("created_at"),
            }
            for user in recent_users
        ],
    }
