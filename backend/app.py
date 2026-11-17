"""
IAFS backend entry point.

Run from the backend folder:
    python app.py

The React frontend runs separately on http://localhost:5173 and calls
http://127.0.0.1:5000/api.
"""
import logging
from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from db import init_indexes, ping_database
from routes.admin import admin_bp
from routes.assistant import assistant_bp
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.content import content_bp
from routes.engagement import engagement_bp
from routes.feedback import feedback_bp
from routes.meta import meta_bp
from routes.quizzes import quiz_bp
from routes.student import student_bp
from routes.teacher import teacher_bp

logging.basicConfig(level=logging.INFO)

# `npm run build` writes the React app into backend/static.
FRONTEND_DIST = Path(__file__).resolve().parent / "static"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.JWT_SECRET
    app.config["JSON_SORT_KEYS"] = False

    CORS(
        app,
        resources={r"/api/*": {"origins": Config.CORS_ORIGINS}},
        supports_credentials=True,
    )

    # Create database indexes at startup (fails gracefully if Mongo is down).
    try:
        init_indexes()
    except Exception as exc:  # pragma: no cover
        app.logger.warning("Could not initialise MongoDB indexes: %s", exc)

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(content_bp, url_prefix="/api")
    app.register_blueprint(quiz_bp, url_prefix="/api")
    app.register_blueprint(student_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(feedback_bp, url_prefix="/api")
    app.register_blueprint(engagement_bp, url_prefix="/api")
    app.register_blueprint(teacher_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api")
    app.register_blueprint(assistant_bp, url_prefix="/api")
    app.register_blueprint(meta_bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        """Used by the frontend and by the team during the demo."""
        db_ok, db_message = ping_database()
        return (
            jsonify(
                {
                    "status": "ok" if db_ok else "degraded",
                    "service": "IAFS API",
                    "database": db_message,
                }
            ),
            200 if db_ok else 503,
        )

    @app.get("/api")
    def api_index():
        return jsonify(
            {
                "name": "IAFS School Learning API",
                "message": "Adaptive English and Mathematics learning for Classes 1-10",
                "health": "/api/health",
                "meta": "/api/meta",
                "frontend": "http://localhost:5173",
            }
        )

    # ------------------------------------------------------------------
    # Optional single-server production mode
    # ------------------------------------------------------------------
    # During development React runs on Vite (port 5173). After
    # `npm run build`, Flask serves the compiled app and its client-side
    # routes from backend/static on the same port as the API.
    @app.get("/", defaults={"path": ""})
    @app.get("/<path:path>")
    def serve_frontend(path):
        if path.startswith("api/") or path == "api":
            return jsonify({"error": "API route not found"}), 404

        if not (FRONTEND_DIST / "index.html").exists():
            if not path:
                return api_index()
            return (
                jsonify(
                    {
                        "error": "Frontend build not found",
                        "hint": "Run `npm install && npm run build` inside the frontend folder, or use the Vite dev server on port 5173.",
                    }
                ),
                404,
            )

        # Serve real files (JS, CSS, fonts) and fall back to index.html so
        # React Router can handle deep links such as /teacher/students.
        candidate = FRONTEND_DIST / path
        if path and candidate.is_file():
            return send_from_directory(FRONTEND_DIST, path)
        return send_from_directory(FRONTEND_DIST, "index.html")

    # ------------------------------------------------------------------
    # Friendly JSON errors
    # ------------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "API route not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception("Unhandled server error: %s", error)
        return jsonify({"error": "Something went wrong on the server"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    print("IAFS API running at http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
