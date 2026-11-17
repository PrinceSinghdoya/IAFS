"""
MongoDB connection helper.

The project uses one small module so every route talks to the same client.
"""
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from config import Config

# A module-level client is reused for the lifetime of the Flask process.
_client = None


def get_client():
    """Return a lazily-created MongoDB client."""
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=4000)
    return _client


def get_db():
    """Return the configured database."""
    return get_client()[Config.DB_NAME]


def init_indexes():
    """Create the indexes we rely on (safe to call many times)."""
    db = get_db()

    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("role", ASCENDING), ("class_level", ASCENDING)])
    db.topics.create_index([("subject", ASCENDING), ("level", ASCENDING), ("order", ASCENDING)])
    db.quiz_sessions.create_index([("student_id", ASCENDING), ("started_at", DESCENDING)])
    db.quiz_sessions.create_index([("student_id", ASCENDING), ("status", ASCENDING)])
    db.learning_results.create_index([("student_id", ASCENDING), ("created_at", DESCENDING)])
    db.learning_results.create_index([("topic_slug", ASCENDING)])
    db.learning_results.create_index([("subject", ASCENDING), ("class_level", ASCENDING)])
    db.adaptive_feedback.create_index([("student_id", ASCENDING), ("created_at", DESCENDING)])
    db.teacher_notes.create_index([("student_id", ASCENDING), ("created_at", DESCENDING)])
    db.class_messages.create_index([("class_level", ASCENDING), ("created_at", DESCENDING)])
    db.focus_sessions.create_index([("student_id", ASCENDING), ("created_at", DESCENDING)])
    db.classes.create_index([("class_level", ASCENDING)], unique=True)
    db.subjects.create_index([("name", ASCENDING)], unique=True)


def ping_database():
    """Return (ok, message) so the health endpoint can report DB status."""
    try:
        get_client().admin.command("ping")
        return True, f"Connected to MongoDB database '{Config.DB_NAME}'"
    except (ServerSelectionTimeoutError, PyMongoError) as exc:
        return False, f"MongoDB is not reachable: {exc}"
