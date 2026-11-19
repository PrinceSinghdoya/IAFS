"""
Adaptive feedback engine for the school learning platform.

Every category, strength and suggestion is computed from real MongoDB data:
  * completed quiz results (scores, topics, attempts)
  * topic coverage for the student's current class
  * optional text signals from class chat

It is deliberately rule-based and explainable - no black-box model and no
random text. The camera module is never used to judge a student.
"""
from datetime import datetime, timedelta, timezone
from statistics import mean

from bson import ObjectId

from curriculum import SUBJECTS, TOPIC_BY_SLUG, topics_for_class
from db import get_db
from utils import round1

CATEGORY_ORDER = [
    "Getting Started",
    "Needs Improvement",
    "Needs Practice",
    "Good Progress",
    "Excellent Performance",
]


def decide_category(percentage):
    """Map a percentage to the shared five-level feedback category."""
    if percentage is None:
        return "Getting Started"
    if percentage < 40:
        return "Needs Improvement"
    if percentage < 60:
        return "Needs Practice"
    if percentage < 85:
        return "Good Progress"
    return "Excellent Performance"


def _percentage(score, total):
    if not total:
        return 0.0
    return round1((score / total) * 100)


def _student(student_id):
    try:
        return get_db().users.find_one({"_id": ObjectId(str(student_id))})
    except Exception:
        return None


def results_for_student(student_id):
    """All completed results for a student, oldest first."""
    return list(
        get_db()
        .learning_results.find({"student_id": str(student_id)})
        .sort("created_at", 1)
    )


def topic_rows_for_student(student_id, class_level=None):
    """One row per curriculum topic for the student's class + subject."""
    student = _student(student_id) if class_level is None else None
    if class_level is None:
        class_level = (student or {}).get("class_level") or 1
    class_level = int(class_level)
    results = results_for_student(student_id)
    grouped = {}
    for result in results:
        grouped.setdefault(result.get("topic_slug"), []).append(result)

    rows = []
    for subject in SUBJECTS:
        for topic in topics_for_class(class_level, subject):
            topic_results = grouped.get(topic["slug"], [])
            scores = [item.get("percentage", 0) for item in topic_results]
            best = round1(max(scores)) if scores else None
            latest = round1(scores[-1]) if scores else None
            average = round1(mean(scores)) if scores else None
            if not scores:
                status = "Not started"
            elif best >= 80:
                status = "Strong"
            elif best >= 60:
                status = "Practising"
            else:
                status = "Needs review"
            rows.append(
                {
                    "slug": topic["slug"],
                    "title": topic["title"],
                    "subject": subject,
                    "emoji": topic["emoji"],
                    "icon": topic["icon"],
                    "level": topic["level"],
                    "attempts": len(topic_results),
                    "best": best,
                    "latest": latest,
                    "average": average,
                    "status": status,
                    "last_attempt_at": topic_results[-1].get("created_at")
                    if topic_results
                    else None,
                }
            )
    return rows


def subject_rows_for_student(student_id, class_level=None):
    rows = topic_rows_for_student(student_id, class_level)
    output = []
    for subject in SUBJECTS:
        subject_topics = [row for row in rows if row["subject"] == subject]
        attempted = [row for row in subject_topics if row["attempts"]]
        averages = [row["average"] for row in attempted if row["average"] is not None]
        output.append(
            {
                "subject": subject,
                "topics_total": len(subject_topics),
                "topics_started": len(attempted),
                "topics_strong": len([row for row in attempted if row["best"] >= 80]),
                "average": round1(mean(averages)) if averages else None,
                "best": round1(max(row["best"] for row in attempted))
                if attempted
                else None,
                "topics": subject_topics,
            }
        )
    return output


def learning_streak(student_id):
    """Number of consecutive days (ending today or yesterday) with a result."""
    db = get_db()
    results = list(
        db.learning_results.find({"student_id": str(student_id)}, {"created_at": 1})
    )
    if not results:
        return 0
    days = set()
    for result in results:
        created = result.get("created_at")
        if isinstance(created, datetime):
            days.add(created.date())
    if not days:
        return 0
    today = datetime.now(timezone.utc).date()
    cursor = today if today in days else today - timedelta(days=1)
    if cursor not in days:
        return 0
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _recent_chat_signal(student_id):
    """Optional supporting text signal. Never changes the category."""
    db = get_db()
    since = datetime.now(timezone.utc) - timedelta(days=14)
    messages = list(
        db.class_messages.find(
            {
                "student_id": str(student_id),
                "created_at": {"$gte": since},
                "analysis.learning_difficulty": "Possible",
            }
        )
        .sort("created_at", -1)
        .limit(5)
    )
    if not messages:
        return None
    latest = messages[0]
    analysis = latest.get("analysis") or {}
    return {
        "count": len(messages),
        "subtopic": analysis.get("subtopic"),
        "topic": analysis.get("topic"),
    }


def build_snapshot(student_id, student=None):
    """Compute the complete evidence bundle for one student."""
    student = student or _student(student_id) or {}
    class_level = int(student.get("class_level") or 1)
    results = results_for_student(student_id)
    attempts = len(results)
    percentages = [result.get("percentage", 0) for result in results]
    average = round1(mean(percentages)) if percentages else None
    best = round1(max(percentages)) if percentages else None
    total_correct = sum(result.get("score", 0) for result in results)
    total_questions = sum(result.get("total", 0) for result in results)

    topics = topic_rows_for_student(student_id, class_level)
    subjects = subject_rows_for_student(student_id, class_level)
    attempted_topics = [row for row in topics if row["attempts"]]
    strengths = [
        row for row in attempted_topics if row["average"] is not None and row["average"] >= 80
    ]
    focus = [
        row for row in attempted_topics if row["average"] is not None and row["average"] < 60
    ]
    not_started = [row for row in topics if not row["attempts"]]

    strengths.sort(key=lambda row: row["average"], reverse=True)
    focus.sort(key=lambda row: row["average"])
    not_started.sort(key=lambda row: row["title"])

    recent = percentages[-5:]
    earlier = percentages[-10:-5]
    trend = "steady"
    if len(recent) >= 2:
        recent_avg = mean(recent)
        earlier_avg = mean(earlier) if earlier else mean(percentages[:-1])
        if recent_avg - earlier_avg >= 4:
            trend = "improving"
        elif recent_avg - earlier_avg <= -4:
            trend = "slipping"

    last_activity = results[-1].get("created_at") if results else None
    chat_signal = _recent_chat_signal(student_id)
    category = decide_category(average)

    snapshot = {
        "student_id": str(student_id),
        "student_name": student.get("name", "Student"),
        "class_level": class_level,
        "level": "Primary" if class_level <= 5 else "Secondary",
        "category": category,
        "attempts": attempts,
        "average": average,
        "best": best,
        "total_correct": total_correct,
        "total_questions": total_questions,
        "topics": topics,
        "subjects": subjects,
        "strengths": strengths[:3],
        "focus_topics": focus[:3],
        "not_started": not_started,
        "recent_scores": [round1(value) for value in recent],
        "trend": trend,
        "streak_days": learning_streak(student_id),
        "last_activity": last_activity,
        "chat_signal": chat_signal,
    }
    snapshot["headline"], snapshot["message"] = _headline_and_message(snapshot)
    snapshot["suggestions"] = _suggestions(snapshot)
    return snapshot


def _headline_and_message(snapshot):
    name = (snapshot["student_name"] or "Student").split()[0]
    category = snapshot["category"]
    class_level = snapshot["class_level"]
    attempts = snapshot["attempts"]

    if category == "Getting Started":
        return (
            "Let's start your learning journey",
            (
                f"{name}, you are in Class {class_level}. Choose English or "
                "Mathematics, read a short topic and try your first 8-question "
                "quiz. Your feedback will grow with every attempt."
            ),
        )

    average = snapshot["average"]
    best = snapshot["best"]
    focus = snapshot["focus_topics"]
    focus_text = (
        f" Your main topic to revisit is {focus[0]['title']} ({focus[0]['average']}%)."
        if focus
        else " Keep exploring new topics to find your next challenge."
    )

    if category == "Needs Improvement":
        return (
            "Small steps will make a big difference",
            (
                f"{name}, you have completed {attempts} quiz"
                f"{'' if attempts == 1 else 'zes'} with an average of {average}%. "
                f"Your best score so far is {best}%. Read the lesson again before "
                "the next quiz and ask the learning assistant whenever a step feels hard."
                f"{focus_text}"
            ),
        )
    if category == "Needs Practice":
        return (
            "You are building the basics",
            (
                f"{name}, your average is {average}% across {attempts} quiz"
                f"{'' if attempts == 1 else 'zes'}, and your best is {best}%. "
                "A little regular practice will lift this quickly. Try one easy quiz, "
                "review every explanation, then attempt the same topic again."
                f"{focus_text}"
            ),
        )
    if category == "Good Progress":
        return (
            "Good progress - keep the momentum",
            (
                f"{name}, you are averaging {average}% with a best score of {best}% "
                f"across {attempts} quiz{'' if attempts == 1 else 'zes'}. "
                "You understand most of the work. Focus on the few questions you miss "
                "and try a harder level when you feel ready."
                f"{focus_text}"
            ),
        )
    return (
        "Excellent performance",
        (
            f"{name}, you are averaging {average}% with a best score of {best}% "
            f"across {attempts} quiz{'' if attempts == 1 else 'zes'}. "
            "Your understanding is strong. Keep it sharp by trying harder questions "
            "and helping a classmate with a topic you know well."
        ),
    )


def _suggestions(snapshot):
    suggestions = []
    focus = snapshot["focus_topics"]
    strengths = snapshot["strengths"]
    subjects = snapshot["subjects"]
    not_started = snapshot["not_started"]

    if focus:
        topic = focus[0]
        suggestions.append(
            f"Revisit the {topic['title']} lesson, then try 8 questions again. "
            f"Your current average there is {topic['average']}%."
        )
    for subject in subjects:
        if subject["topics_started"] == 0:
            first = next(
                (row for row in subject["topics"] if not row["attempts"]), None
            )
            if first:
                suggestions.append(
                    f"Start {subject['subject']} with {first['title']} - it is a good first topic for Class {snapshot['class_level']}."
                )
            break
    if snapshot["trend"] == "slipping":
        suggestions.append(
            "Your last few scores dipped slightly. Review the explanations from your most recent quiz before starting a new one."
        )
    elif snapshot["trend"] == "improving":
        suggestions.append(
            "Your recent scores are improving. Keep the same routine: read, practise, then quiz."
        )
    if strengths:
        topic = strengths[0]
        suggestions.append(
            f"You are strong in {topic['title']} ({topic['average']}%). Try a harder quiz there to stretch yourself."
        )
    if not_started and len(suggestions) < 3:
        suggestions.append(
            f"New topic to explore: {not_started[0]['title']} in {not_started[0]['subject']}."
        )
    chat_signal = snapshot.get("chat_signal")
    if chat_signal and chat_signal.get("subtopic") and len(suggestions) < 4:
        suggestions.append(
            f"You asked about {chat_signal['subtopic']} in class chat. Revisit that topic and ask the assistant for a worked example."
        )
    suggestions.append(
        "Use the learning assistant to explain any step you found difficult - it will not just give you the quiz answer."
    )
    return suggestions[:5]


def generate_feedback(student_id, snapshot=None, persist=True):
    """Build and optionally store a feedback record for a student."""
    snapshot = snapshot or build_snapshot(student_id)
    record = {
        "student_id": str(student_id),
        "student_name": snapshot["student_name"],
        "class_level": snapshot["class_level"],
        "category": snapshot["category"],
        "headline": snapshot["headline"],
        "message": snapshot["message"],
        "suggestions": snapshot["suggestions"],
        "strengths": [
            {"slug": row["slug"], "title": row["title"], "percentage": row["average"]}
            for row in snapshot["strengths"]
        ],
        "focus_topics": [
            {"slug": row["slug"], "title": row["title"], "percentage": row["average"]}
            for row in snapshot["focus_topics"]
        ],
        "metrics": {
            "attempts": snapshot["attempts"],
            "average_percentage": snapshot["average"],
            "best_percentage": snapshot["best"],
            "total_correct": snapshot["total_correct"],
            "total_questions": snapshot["total_questions"],
            "topics_started": len([row for row in snapshot["topics"] if row["attempts"]]),
            "topics_total": len(snapshot["topics"]),
            "streak_days": snapshot["streak_days"],
            "trend": snapshot["trend"],
            "subject_averages": {
                row["subject"]: row["average"] for row in snapshot["subjects"]
            },
            "chat_help_requests": (snapshot.get("chat_signal") or {}).get("count", 0),
        },
        "source": "engine",
        "created_at": datetime.now(timezone.utc),
    }
    if persist:
        record["_id"] = get_db().adaptive_feedback.insert_one(record).inserted_id
    return record


def ensure_feedback(student_id):
    """
    Return the latest feedback record, regenerating it only when the
    underlying evidence has changed. This keeps the history meaningful.
    """
    snapshot = build_snapshot(student_id)
    latest = get_db().adaptive_feedback.find_one(
        {"student_id": str(student_id), "source": "engine"},
        sort=[("created_at", -1)],
    )
    if latest:
        metrics = latest.get("metrics") or {}
        same_attempts = metrics.get("attempts") == snapshot["attempts"]
        same_average = metrics.get("average_percentage") == snapshot["average"]
        same_correct = metrics.get("total_correct") == snapshot["total_correct"]
        if same_attempts and same_average and same_correct:
            return latest
    return generate_feedback(student_id, snapshot=snapshot, persist=True)


def serialize_feedback(record):
    if not record:
        return None
    return {
        "id": str(record["_id"]) if record.get("_id") else None,
        "student_id": record.get("student_id"),
        "student_name": record.get("student_name"),
        "class_level": record.get("class_level"),
        "category": record.get("category"),
        "headline": record.get("headline"),
        "message": record.get("message"),
        "suggestions": record.get("suggestions", []),
        "strengths": record.get("strengths", []),
        "focus_topics": record.get("focus_topics", []),
        "metrics": record.get("metrics", {}),
        "created_at": record.get("created_at"),
        "source": record.get("source", "engine"),
    }
