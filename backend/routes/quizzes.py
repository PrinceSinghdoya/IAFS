"""Adaptive 8-question quiz engine, server-side grading and result review."""
from datetime import datetime, timezone
from statistics import mean
from uuid import uuid4

from flask import Blueprint, g, jsonify, request

from auth_utils import require_auth
from curriculum import (
    SUBJECTS,
    TOPIC_BY_SLUG,
    generate_question,
    level_for_class,
    next_difficulty,
    starting_difficulty,
    topics_for_class,
)
from db import get_db
from services.feedback_engine import build_snapshot, decide_category, generate_feedback
from utils import json_safe, round1, serialize_question, serialize_result

quiz_bp = Blueprint("quizzes", __name__)

QUESTIONS_PER_QUIZ = 8


def _suggestions_for_result(topic_title, percentage, class_level):
    suggestions = []
    if percentage < 40:
        suggestions.append(
            f"Read the {topic_title} lesson again slowly. Focus on the key points and one worked example."
        )
        suggestions.append(
            "Try 2 practice questions on the lesson page before starting another quiz."
        )
    elif percentage < 60:
        suggestions.append(
            f"You are close. Review the {topic_title} explanations for the questions you missed."
        )
        suggestions.append(
            "Take the quiz again, and use the learning assistant if a step is unclear."
        )
    elif percentage < 85:
        suggestions.append(
            f"Good work. Revisit the {topic_title} questions you missed, then try a harder quiz."
        )
        suggestions.append(
            "Explain one answer aloud in your own words - it is a quick way to check understanding."
        )
    else:
        suggestions.append(
            f"Excellent. Try a harder {topic_title} quiz to stretch your understanding."
        )
        suggestions.append(
            "Help a classmate with one question - teaching it is a strong way to revise."
        )
    suggestions.append(
        f"Keep practising a little every day. This quiz started at "
        f"{'easy' if class_level <= 5 else 'medium'} level and adapted to your answers."
    )
    return suggestions


def _finalize_session(session):
    """Create the learning result and close the quiz session."""
    db = get_db()
    score = session["score"]
    total = session["total"]
    percentage = round1((score / total) * 100) if total else 0
    category = decide_category(percentage)
    topic = TOPIC_BY_SLUG.get(session["topic_slug"], {})
    answers = []
    for question, answer in zip(session["questions"], session["answers"]):
        answers.append(
            {
                "question": question["question"],
                "options": question["options"],
                "correct_index": question["correct_index"],
                "selected_index": answer["selected_index"],
                "is_correct": answer["is_correct"],
                "difficulty": question["difficulty"],
                "explanation": question["explanation"],
                "simpler_example": question.get("simpler_example"),
                "topic_slug": question["topic_slug"],
            }
        )

    result = {
        "session_id": session["_id"],
        "student_id": session["student_id"],
        "student_name": session["student_name"],
        "class_level": session["class_level"],
        "subject": session["subject"],
        "topic_slug": session["topic_slug"],
        "topic_title": session["topic_title"],
        "score": score,
        "total": total,
        "percentage": percentage,
        "category": category,
        "difficulty_path": session.get("difficulty_path", []),
        "answers": answers,
        "suggestions": _suggestions_for_result(
            session["topic_title"], percentage, session["class_level"]
        ),
        "started_at": session.get("started_at"),
        "created_at": datetime.now(timezone.utc),
    }
    result["_id"] = db.learning_results.insert_one(result).inserted_id
    db.quiz_sessions.update_one(
        {"_id": session["_id"]},
        {
            "$set": {
                "status": "completed",
                "score": score,
                "percentage": percentage,
                "category": category,
                "result_id": result["_id"],
                "completed_at": result["created_at"],
            }
        },
    )
    # Refresh the student's feedback immediately after a new quiz.
    generate_feedback(session["student_id"], persist=True)

    # The end-of-quiz summary also names the topics that need practice,
    # computed from every result saved for this student.
    snapshot = build_snapshot(session["student_id"])
    result["weak_topics"] = [
        {
            "slug": row.get("slug"),
            "title": row.get("title"),
            "subject": row.get("subject"),
            "average": row.get("average"),
        }
        for row in snapshot["focus_topics"]
    ]
    db.learning_results.update_one(
        {"_id": result["_id"]}, {"$set": {"weak_topics": result["weak_topics"]}}
    )
    return result


def _session_result_payload(result):
    return {
        "id": str(result["_id"]),
        "session_id": result.get("session_id"),
        "student_id": result.get("student_id"),
        "student_name": result.get("student_name"),
        "class_level": result.get("class_level"),
        "subject": result.get("subject"),
        "topic_slug": result.get("topic_slug"),
        "topic": result.get("topic_title"),
        "score": result.get("score"),
        "total": result.get("total"),
        "percentage": result.get("percentage"),
        "category": result.get("category"),
        "difficulty_path": result.get("difficulty_path", []),
        "answers": result.get("answers", []),
        "suggestions": result.get("suggestions", []),
        "weak_topics": json_safe(result.get("weak_topics", [])),
        "created_at": json_safe(result.get("created_at")),
    }


def _unique_question(topic_slug, class_level, difficulty, used):
    question = None
    for _ in range(40):
        question = generate_question(topic_slug, class_level, difficulty)
        if question["question"] not in used:
            return question
    return question


@quiz_bp.post("/quizzes/start")
@require_auth("student")
def start_quiz():
    """
    Start a new adaptive quiz.

    Body: {topic_slug?} or {subject?}. If no topic is given, the weakest
    not-yet-attempted topic is chosen.
    """
    data = request.get_json(silent=True) or {}
    class_level = int(g.user.get("class_level") or 1)
    topic_slug = (data.get("topic_slug") or "").strip()
    subject = (data.get("subject") or "").strip()

    if subject and subject not in SUBJECTS:
        return jsonify({"error": "Unknown subject"}), 400
    topic = TOPIC_BY_SLUG.get(topic_slug) if topic_slug else None
    if topic_slug and not topic:
        return jsonify({"error": "Topic not found"}), 404
    if topic and topic["level"] != level_for_class(class_level):
        return jsonify({"error": "This topic is for a different class group"}), 403
    if not topic:
        candidates = topics_for_class(class_level, subject or None)
        if not candidates:
            return jsonify({"error": "No topics available for this class"}), 404
        topic = candidates[0]

    db = get_db()
    # Abandon old unfinished sessions so the dashboard stays clean.
    db.quiz_sessions.update_many(
        {"student_id": g.user_id, "status": "active"},
        {"$set": {"status": "abandoned", "abandoned_at": datetime.now(timezone.utc)}},
    )

    difficulty = starting_difficulty(class_level)
    question = _unique_question(topic["slug"], class_level, difficulty, set())
    now = datetime.now(timezone.utc)
    session = {
        "_id": uuid4().hex,
        "student_id": g.user_id,
        "student_name": g.user.get("name"),
        "class_level": class_level,
        "subject": topic["subject"],
        "topic_slug": topic["slug"],
        "topic_title": topic["title"],
        "status": "active",
        "difficulty": difficulty,
        "questions": [question],
        "answers": [],
        "score": 0,
        "total": QUESTIONS_PER_QUIZ,
        "streak": 0,
        "max_streak": 0,
        "difficulty_path": [difficulty],
        "started_at": now,
    }
    db.quiz_sessions.insert_one(session)
    return (
        jsonify(
            {
                "session_id": session["_id"],
                "topic": {
                    "slug": topic["slug"],
                    "title": topic["title"],
                    "subject": topic["subject"],
                    "emoji": topic["emoji"],
                },
                "subject": topic["subject"],
                "class_level": class_level,
                "total_questions": QUESTIONS_PER_QUIZ,
                "answered": 0,
                "score": 0,
                "difficulty": difficulty,
                "question": serialize_question(question),
            }
        ),
        201,
    )


@quiz_bp.post("/quizzes/<session_id>/answer")
@require_auth("student")
def answer_question(session_id):
    """Grade one answer, adapt the difficulty and return the next question."""
    data = request.get_json(silent=True) or {}
    question_id = data.get("question_id")
    selected = data.get("selected_index")
    try:
        selected = int(selected)
    except (TypeError, ValueError):
        return jsonify({"error": "Please choose an option"}), 400
    if selected not in range(4):
        return jsonify({"error": "Please choose an option"}), 400

    db = get_db()
    session = db.quiz_sessions.find_one({"_id": session_id, "student_id": g.user_id})
    if not session:
        return jsonify({"error": "Quiz session not found"}), 404
    if session.get("status") != "active":
        return jsonify({"error": "This quiz has already finished"}), 409

    questions = session.get("questions", [])
    answers = session.get("answers", [])
    if not questions:
        return jsonify({"error": "Quiz session has no questions"}), 500
    current = questions[-1] if len(questions) > len(answers) else questions[len(answers)]
    if question_id and question_id != current["id"]:
        return jsonify(
            {"error": "This is not the current question", "question": serialize_question(current)}
        ), 409

    is_correct = selected == current["correct_index"]
    answer = {
        "question_id": current["id"],
        "selected_index": selected,
        "is_correct": is_correct,
        "difficulty": current["difficulty"],
        "answered_at": datetime.now(timezone.utc),
    }
    answers.append(answer)
    score = session["score"] + (1 if is_correct else 0)
    streak = session.get("streak", 0) + 1 if is_correct else 0
    max_streak = max(session.get("max_streak", 0), streak)
    next_level = next_difficulty(current["difficulty"], is_correct, streak)

    session["answers"] = answers
    session["score"] = score
    session["streak"] = streak
    session["max_streak"] = max_streak
    session["difficulty"] = next_level

    total = session.get("total", QUESTIONS_PER_QUIZ)
    if len(answers) >= total:
        result = _finalize_session(session)
        return jsonify(
            {
                "correct": is_correct,
                "correct_index": current["correct_index"],
                "selected_index": selected,
                "explanation": current["explanation"],
                "simpler_example": current.get("simpler_example"),
                "score": score,
                "answered": len(answers),
                "total": total,
                "percentage": round1((score / total) * 100),
                "difficulty": current["difficulty"],
                "next_difficulty": None,
                "completed": True,
                "result": _session_result_payload(result),
            }
        )

    used = {question["question"] for question in questions}
    new_question = _unique_question(
        session["topic_slug"], session["class_level"], next_level, used
    )
    session["questions"].append(new_question)
    session["difficulty_path"].append(next_level)
    db.quiz_sessions.update_one(
        {"_id": session_id},
        {
            "$set": {
                "questions": session["questions"],
                "answers": answers,
                "score": score,
                "streak": streak,
                "max_streak": max_streak,
                "difficulty": next_level,
                "difficulty_path": session["difficulty_path"],
            }
        },
    )
    return jsonify(
        {
            "correct": is_correct,
            "correct_index": current["correct_index"],
            "selected_index": selected,
            "explanation": current["explanation"],
            "simpler_example": current.get("simpler_example"),
            "score": score,
            "answered": len(answers),
            "total": total,
            "percentage": round1((score / total) * 100),
            "difficulty": next_level,
            "next_difficulty": next_level,
            "completed": False,
            "next_question": serialize_question(new_question),
        }
    )


@quiz_bp.get("/quizzes/<session_id>/result")
@require_auth(["student", "teacher", "admin"])
def quiz_result(session_id):
    """Full review for a completed quiz."""
    db = get_db()
    query = {"_id": session_id}
    if g.user.get("role") == "student":
        query["student_id"] = g.user_id
    session = db.quiz_sessions.find_one(query)
    if not session:
        return jsonify({"error": "Quiz session not found"}), 404
    if session.get("status") != "completed":
        return jsonify({"error": "Quiz is not finished yet"}), 409
    result = db.learning_results.find_one({"session_id": session_id})
    if not result:
        return jsonify({"error": "Result not found"}), 404
    return jsonify({"result": _session_result_payload(result)})


@quiz_bp.get("/quizzes/history")
@require_auth("student")
def quiz_history():
    """Completed quiz history for the signed-in student."""
    db = get_db()
    query = {"student_id": g.user_id}
    subject = request.args.get("subject")
    topic_slug = request.args.get("topic")
    if subject in SUBJECTS:
        query["subject"] = subject
    if topic_slug:
        query["topic_slug"] = topic_slug
    limit = min(int(request.args.get("limit", 30) or 30), 100)
    results = list(
        db.learning_results.find(query).sort("created_at", -1).limit(limit)
    )
    return jsonify({"results": [serialize_result(result) for result in results]})


@quiz_bp.get("/quizzes/summary")
@require_auth("student")
def quiz_summary():
    """Small summary used by the topic and result pages."""
    db = get_db()
    results = list(db.learning_results.find({"student_id": g.user_id}))
    scores = [item.get("percentage", 0) for item in results]
    return jsonify(
        {
            "attempts": len(results),
            "average": round1(mean(scores)) if scores else None,
            "best": round1(max(scores)) if scores else None,
            "recent": [serialize_result(item) for item in results[-4:]][::-1],
        }
    )
