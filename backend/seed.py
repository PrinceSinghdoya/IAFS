"""
Seed the IAFS school database with demo accounts and realistic activity.

Run once from the backend folder:
    python seed.py

It is safe to run again: accounts, content and demo activity are created only
when missing. All data is fictional. No photos, videos or real children's
information are stored.
"""
from datetime import datetime, timedelta, timezone

from auth_utils import hash_password
from curriculum import (
    CLASS_LEVELS,
    SUBJECT_INFO,
    SUBJECTS,
    TOPIC_BY_SLUG,
    TOPICS,
    generate_question,
    level_for_class,
    starting_difficulty,
)
from db import get_db, init_indexes, ping_database
from seed_data import (
    DEMO_USERS,
    SAMPLE_ATTEMPTS,
    SAMPLE_CHATS,
    SAMPLE_FOCUS,
    SAMPLE_NOTES,
)
from services.feedback_engine import decide_category, generate_feedback
from services.sentiment import analyze_message

QUESTIONS_PER_QUIZ = 8


def seed_structure(db):
    """Mirror the curriculum into small reference collections."""
    for class_level in CLASS_LEVELS:
        db.classes.update_one(
            {"class_level": class_level},
            {
                "$set": {
                    "class_level": class_level,
                    "level": level_for_class(class_level),
                    "label": f"Class {class_level}",
                }
            },
            upsert=True,
        )
    for subject in SUBJECTS:
        info = SUBJECT_INFO[subject]
        db.subjects.update_one(
            {"name": subject},
            {
                "$set": {
                    "name": subject,
                    "emoji": info["emoji"],
                    "tagline": info["tagline"],
                    "description": info["description"],
                    "topics": len(
                        [topic for topic in TOPICS if topic["subject"] == subject]
                    ),
                }
            },
            upsert=True,
        )
    # Keep a searchable topic catalogue in MongoDB as well as in Python.
    for topic in TOPICS:
        document = {key: value for key, value in topic.items() if key != "class_tips"}
        document["class_tips"] = topic.get("class_tips", {})
        db.topics.update_one({"slug": topic["slug"]}, {"$set": document}, upsert=True)
    print(
        f"  [ok] {len(CLASS_LEVELS)} classes, {len(SUBJECTS)} subjects and "
        f"{len(TOPICS)} topics ready"
    )


def seed_users(db):
    """Create or refresh the demo accounts so the printed logins always work."""
    created = 0
    for demo in DEMO_USERS:
        class_level = demo.get("class_level")
        profile = {
            "name": demo["name"],
            "email": demo["email"],
            "role": demo["role"],
            "class_level": class_level,
            "level": level_for_class(class_level) if class_level else None,
            "section": demo.get("section"),
            "roll_no": demo.get("roll_no"),
            "subjects": demo.get("subjects", []),
            "is_active": True,
            "is_demo": True,
        }
        existing = db.users.find_one({"email": demo["email"]})
        if existing:
            db.users.update_one({"_id": existing["_id"]}, {"$set": profile})
            continue
        profile.update(
            {
                "password_hash": hash_password(demo["password"]),
                "created_at": datetime.now(timezone.utc) - timedelta(days=40),
                "last_login": None,
            }
        )
        db.users.insert_one(profile)
        created += 1
    print(f"  [ok] demo accounts ready ({created} new)")


def _difficulty_path(score, class_level):
    """Build a believable easy/medium/hard path for a sample attempt."""
    difficulty = starting_difficulty(class_level)
    order = ["easy", "medium", "hard"]
    path = []
    streak = 0
    correct_left = score
    remaining = QUESTIONS_PER_QUIZ
    for index in range(remaining):
        path.append(difficulty)
        # Spread the correct answers through the attempt.
        should_be_correct = correct_left > 0 and (
            index < 3 or (index % max(remaining - 2, 1)) < correct_left
        )
        if should_be_correct:
            correct_left -= 1
        if should_be_correct:
            streak += 1
            if streak >= 2 and difficulty != "hard":
                difficulty = order[order.index(difficulty) + 1]
                streak = 0
        else:
            streak = 0
            if difficulty != "easy":
                difficulty = order[order.index(difficulty) - 1]
    return path


def _sample_answers(topic_slug, class_level, score):
    path = _difficulty_path(score, class_level)
    answers = []
    used = set()
    correct_remaining = score
    for index, difficulty in enumerate(path):
        question = None
        for _ in range(20):
            candidate = generate_question(topic_slug, class_level, difficulty)
            if candidate["question"] not in used:
                question = candidate
                break
        question = question or generate_question(topic_slug, class_level, difficulty)
        used.add(question["question"])
        is_correct = correct_remaining > 0 and (
            index < 3 or index % 2 == 0 or correct_remaining >= (QUESTIONS_PER_QUIZ - index)
        )
        if is_correct:
            correct_remaining -= 1
        selected = (
            question["correct_index"]
            if is_correct
            else (question["correct_index"] + 1) % 4
        )
        answers.append(
            {
                "question": question["question"],
                "options": question["options"],
                "correct_index": question["correct_index"],
                "selected_index": selected,
                "is_correct": is_correct,
                "difficulty": difficulty,
                "explanation": question["explanation"],
                "simpler_example": question.get("simpler_example"),
                "topic_slug": topic_slug,
            }
        )
    # Guarantee exactly the intended number of correct answers.
    actual = sum(1 for answer in answers if answer["is_correct"])
    if actual != score:
        if actual < score:
            for answer in answers:
                if not answer["is_correct"] and actual < score:
                    answer["is_correct"] = True
                    answer["selected_index"] = answer["correct_index"]
                    actual += 1
        else:
            for answer in answers:
                if answer["is_correct"] and actual > score:
                    answer["is_correct"] = False
                    answer["selected_index"] = (answer["correct_index"] + 1) % 4
                    actual -= 1
    return answers, path


def _result_suggestions(topic_title, percentage):
    if percentage < 40:
        return [
            f"Read the {topic_title} lesson again and study one worked example.",
            "Try two practice questions before starting another quiz.",
            "Ask the learning assistant to explain the step that felt hard.",
        ]
    if percentage < 60:
        return [
            f"Review the {topic_title} explanations for the questions you missed.",
            "Take the quiz again and use the assistant for any unclear step.",
            "Practise a little every day - short sessions work best.",
        ]
    if percentage < 85:
        return [
            f"Good work. Revisit the {topic_title} questions you missed.",
            "Try a harder quiz when you feel ready.",
            "Explain one answer aloud in your own words.",
        ]
    return [
        f"Excellent. Try a harder {topic_title} quiz to stretch yourself.",
        "Help a classmate with one question - teaching is great revision.",
        "Keep your daily practice routine going.",
    ]


def seed_results(db):
    """Add sample quiz attempts with full answer reviews."""
    added = 0
    for email, topic_slug, score, days_ago, hour in SAMPLE_ATTEMPTS:
        user = db.users.find_one({"email": email})
        topic = TOPIC_BY_SLUG.get(topic_slug)
        if not user or not topic:
            continue
        student_id = str(user["_id"])
        created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
        created_at = created_at.replace(hour=hour, minute=15, second=0, microsecond=0)

        # Avoid duplicating the same sample attempt on repeated seed runs.
        if db.learning_results.find_one(
            {"student_id": student_id, "topic_slug": topic_slug, "created_at": created_at}
        ):
            continue

        class_level = int(user.get("class_level") or 1)
        answers, path = _sample_answers(topic_slug, class_level, score)
        percentage = round(score / QUESTIONS_PER_QUIZ * 100, 1)
        result = {
            "session_id": f"demo-{student_id}-{topic_slug}-{days_ago}",
            "student_id": student_id,
            "student_name": user["name"],
            "class_level": class_level,
            "subject": topic["subject"],
            "topic_slug": topic_slug,
            "topic_title": topic["title"],
            "score": score,
            "total": QUESTIONS_PER_QUIZ,
            "percentage": percentage,
            "category": decide_category(percentage),
            "difficulty_path": path,
            "answers": answers,
            "suggestions": _result_suggestions(topic["title"], percentage),
            "started_at": created_at - timedelta(minutes=6),
            "created_at": created_at,
            "is_demo": True,
        }
        db.learning_results.insert_one(result)
        added += 1
    print(f"  [ok] demo quiz results ready ({added} new)")


def seed_chats(db):
    """Add realistic class chat messages, with light text analysis."""
    added = 0
    for email, role, class_level, text, minutes_ago in SAMPLE_CHATS:
        user = db.users.find_one({"email": email})
        if not user:
            continue
        if db.class_messages.find_one({"text": text}):
            continue
        is_teacher = role in {"teacher", "admin"}
        db.class_messages.insert_one(
            {
                "student_id": str(user["_id"]),
                "student_name": user["name"],
                "role": role,
                "class_level": class_level,
                "is_teacher": is_teacher,
                "text": text,
                "analysis": None
                if is_teacher
                else analyze_message(text, class_level),
                "is_demo": True,
                "created_at": datetime.now(timezone.utc)
                - timedelta(minutes=minutes_ago),
            }
        )
        added += 1
    print(f"  [ok] demo class chat messages ready ({added} new)")


def seed_focus(db):
    """Add aggregate-only demo focus checks. No media is stored."""
    added = 0
    for email, session_seconds, face_ratio, centered_ratio, days_ago in SAMPLE_FOCUS:
        user = db.users.find_one({"email": email})
        if not user:
            continue
        student_id = str(user["_id"])
        created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
        if db.focus_sessions.find_one({"student_id": student_id, "created_at": created_at}):
            continue
        face = round(face_ratio * 100, 1)
        centered = round(centered_ratio * 100, 1)
        score = round(face * 0.7 + centered * 0.3, 1)
        indicator = (
            "Face visible and centred"
            if score >= 75
            else "Partly visible"
            if score >= 45
            else "Low signal"
        )
        db.focus_sessions.insert_one(
            {
                "student_id": student_id,
                "student_name": user["name"],
                "class_level": user.get("class_level"),
                "session_seconds": session_seconds,
                "face_ratio": face,
                "centered_ratio": centered,
                "focus_score": score,
                "indicator": indicator,
                "source": "camera",
                "is_demo": True,
                "created_at": created_at,
            }
        )
        added += 1
    print(f"  [ok] demo focus checks ready ({added} new)")


def seed_notes(db):
    """Add a few private teacher notes."""
    teacher = db.users.find_one({"email": "teacher@iafs.school"})
    if not teacher:
        return
    added = 0
    for email, note_text, days_ago in SAMPLE_NOTES:
        student = db.users.find_one({"email": email})
        if not student or db.teacher_notes.find_one({"note": note_text}):
            continue
        db.teacher_notes.insert_one(
            {
                "student_id": str(student["_id"]),
                "student_name": student["name"],
                "teacher_id": str(teacher["_id"]),
                "teacher_name": teacher["name"],
                "note": note_text,
                "created_at": datetime.now(timezone.utc) - timedelta(days=days_ago),
            }
        )
        added += 1
    print(f"  [ok] teacher notes ready ({added} new)")


def seed_feedback(db):
    """Generate adaptive feedback from the seeded evidence."""
    added = 0
    for demo in DEMO_USERS:
        if demo["role"] != "student":
            continue
        user = db.users.find_one({"email": demo["email"]})
        if not user:
            continue
        student_id = str(user["_id"])
        if db.adaptive_feedback.find_one({"student_id": student_id, "source": "engine"}):
            continue
        generate_feedback(student_id)
        added += 1
    print(f"  [ok] adaptive feedback generated ({added} new)")


def main():
    ok, message = ping_database()
    print(message)
    if not ok:
        print("Start MongoDB, then run: python seed.py")
        raise SystemExit(1)

    db = get_db()
    init_indexes()

    print("Seeding IAFS school database...")
    seed_structure(db)
    seed_users(db)
    seed_results(db)
    seed_chats(db)
    seed_focus(db)
    seed_notes(db)
    seed_feedback(db)

    print("\nDemo accounts")
    print("  Administrator : admin@iafs.school / Admin@123")
    print("  Teacher       : teacher@iafs.school / Teacher@123")
    print("  Class 1       : kabir@iafs.school / Student@123")
    print("  Class 2       : sara@iafs.school / Student@123")
    print("  Class 4       : aarav@iafs.school / Student@123")
    print("  Class 8       : priya@iafs.school / Student@123")
    print("  Teacher invite code: IAFS2026")
    print("\nSeed complete. Start the API with: python app.py")


if __name__ == "__main__":
    main()
