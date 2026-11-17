"""Class-aware, rule-based learning assistant routes."""
from flask import Blueprint, g, jsonify, request

from assistant_kb import build_reply
from auth_utils import require_auth
from curriculum import CLASS_LEVELS, SUBJECTS, topics_for_class

assistant_bp = Blueprint("assistant", __name__)

MAX_MESSAGE = 500


@assistant_bp.post("/assistant/ask")
@require_auth()
def ask_assistant():
    """
    Answer a learning question without revealing live quiz answers.

    Body: {message, topic_slug?, class_level?}
    `class_level` is only honoured for teachers and administrators.
    """
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if len(message) > MAX_MESSAGE:
        return jsonify({"error": "Please keep your question shorter than 500 characters"}), 400

    class_level = int(g.user.get("class_level") or 1)
    if g.user.get("role") in {"teacher", "admin"}:
        try:
            requested = int(data.get("class_level") or 0)
            if requested in CLASS_LEVELS:
                class_level = requested
        except (TypeError, ValueError):
            pass

    topic_slug = (data.get("topic_slug") or "").strip() or None
    reply = build_reply(message, class_level, topic_slug)
    reply["class_level"] = class_level
    return jsonify(reply)


@assistant_bp.get("/assistant/suggestions")
@require_auth()
def assistant_suggestions():
    """Prompt chips for the assistant page."""
    class_level = int(g.user.get("class_level") or 1)
    if g.user.get("role") in {"teacher", "admin"}:
        try:
            requested = int(request.args.get("class_level") or 0)
            if requested in CLASS_LEVELS:
                class_level = requested
        except (TypeError, ValueError):
            pass

    topics = topics_for_class(class_level)
    picks = [topics[index] for index in (0, 2, 9, 10) if index < len(topics)]
    if class_level <= 5:
        prompts = [
            "Explain fractions in a simple way.",
            "How do I use a and an?",
            "Give me an example of a naming word.",
            "How can I get better at spelling?",
            "What is a number pattern?",
        ]
    else:
        prompts = [
            "Explain algebra step by step.",
            "How do I change active voice to passive voice?",
            "What is the difference between mean and median?",
            "How do I find the main idea of a passage?",
            "Explain how to solve a linear equation.",
        ]
    return jsonify(
        {
            "class_level": class_level,
            "subjects": SUBJECTS,
            "prompts": prompts,
            "topics": [
                {"slug": topic["slug"], "title": topic["title"], "subject": topic["subject"]}
                for topic in picks
            ],
        }
    )
