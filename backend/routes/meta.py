"""Public metadata used by the landing, login and registration pages."""
from flask import Blueprint, jsonify

from curriculum import CLASS_LEVELS, SUBJECT_INFO, SUBJECTS, TOPICS, level_for_class
from seed_data import DEMO_ACCOUNTS

meta_bp = Blueprint("meta", __name__)


@meta_bp.get("/meta")
def meta():
    classes = [
        {
            "class_level": class_level,
            "level": level_for_class(class_level),
        }
        for class_level in CLASS_LEVELS
    ]
    subjects = [
        {
            "name": subject,
            "emoji": SUBJECT_INFO[subject]["emoji"],
            "tagline": SUBJECT_INFO[subject]["tagline"],
            "description": SUBJECT_INFO[subject]["description"],
            "primary_topics": len(
                [topic for topic in TOPICS if topic["subject"] == subject and topic["level"] == "Primary"]
            ),
            "secondary_topics": len(
                [topic for topic in TOPICS if topic["subject"] == subject and topic["level"] == "Secondary"]
            ),
        }
        for subject in SUBJECTS
    ]
    return jsonify(
        {
            "name": "IAFS School Learning",
            "tagline": "Learning that adapts to every child",
            "classes": classes,
            "subjects": subjects,
            "total_topics": len(TOPICS),
            "demo_accounts": DEMO_ACCOUNTS,
        }
    )
