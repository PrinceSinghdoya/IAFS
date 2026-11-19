"""
Backend test suite for the school learning platform.

Run from the backend folder:
    python -m unittest discover -s tests -v

The tests use a separate database (iafs_test) so demo data is never changed.
"""
import os
import sys
import unittest

# Must be set before importing config/db.
os.environ["DB_NAME"] = "iafs_test"
os.environ["JWT_SECRET"] = "iafs-test-secret-key-at-least-32-bytes-long"
# The suite seeds its own structure/users; startup auto-seeding would add demo
# quiz results and make clean-student assertions (e.g. topics_started) fail.
os.environ["AUTO_SEED"] = "false"

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from app import create_app  # noqa: E402
from db import get_client, get_db  # noqa: E402
from seed import seed_structure, seed_users  # noqa: E402
from services.feedback_engine import decide_category  # noqa: E402
from services.sentiment import analyze_message  # noqa: E402


class IAFSAPITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_client().drop_database("iafs_test")
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()
        db = get_db()
        seed_structure(db)
        seed_users(db)

    @classmethod
    def tearDownClass(cls):
        get_client().drop_database("iafs_test")
        get_client().close()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def login(self, email, password):
        response = self.client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        return response.get_json()["token"]

    def auth(self, token):
        return {"Authorization": f"Bearer {token}"}

    def complete_quiz(self, token, topic_slug, correct=True):
        start = self.client.post(
            "/api/quizzes/start",
            headers=self.auth(token),
            json={"topic_slug": topic_slug},
        )
        self.assertEqual(start.status_code, 201, start.get_data(as_text=True))
        session_id = start.get_json()["session_id"]
        body = None
        for _ in range(8):
            session = get_db().quiz_sessions.find_one({"_id": session_id})
            current = session["questions"][len(session["answers"])]
            selected = current["correct_index"] if correct else (current["correct_index"] + 1) % 4
            answer = self.client.post(
                f"/api/quizzes/{session_id}/answer",
                headers=self.auth(token),
                json={"question_id": current["id"], "selected_index": selected},
            )
            self.assertEqual(answer.status_code, 200, answer.get_data(as_text=True))
            body = answer.get_json()
        return session_id, body

    # ------------------------------------------------------------------
    # Public metadata and authentication
    # ------------------------------------------------------------------
    def test_health_and_meta(self):
        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.get_json()["status"], "ok")

        meta = self.client.get("/api/meta").get_json()
        self.assertEqual(meta["total_topics"], 35)
        self.assertEqual(len(meta["classes"]), 10)
        self.assertEqual([subject["name"] for subject in meta["subjects"]], ["English", "Mathematics"])
        self.assertTrue(meta["demo_accounts"])

    def test_register_login_profile_and_logout(self):
        response = self.client.post(
            "/api/auth/register",
            json={
                "name": "Test Child",
                "email": "test.child@example.com",
                "password": "secret123",
                "class_level": 4,
                "section": "B",
                "roll_no": "4B-01",
            },
        )
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        body = response.get_json()
        token = body["token"]
        self.assertEqual(body["user"]["role"], "student")
        self.assertEqual(body["user"]["class_level"], 4)
        self.assertEqual(body["user"]["level"], "Primary")
        self.assertNotIn("password_hash", body["user"])

        me = self.client.get("/api/auth/me", headers=self.auth(token))
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.get_json()["user"]["email"], "test.child@example.com")

        # Students can change class; the level follows automatically.
        profile = self.client.patch(
            "/api/auth/profile", headers=self.auth(token), json={"class_level": 7}
        )
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.get_json()["user"]["class_level"], 7)
        self.assertEqual(profile.get_json()["user"]["level"], "Secondary")

        # Duplicate email and weak password are rejected.
        duplicate = self.client.post(
            "/api/auth/register",
            json={
                "name": "Another",
                "email": "test.child@example.com",
                "password": "secret123",
                "class_level": 2,
            },
        )
        self.assertEqual(duplicate.status_code, 409)
        weak = self.client.post(
            "/api/auth/register",
            json={
                "name": "Weak",
                "email": "weak@example.com",
                "password": "123",
                "class_level": 2,
            },
        )
        self.assertEqual(weak.status_code, 400)
        missing_class = self.client.post(
            "/api/auth/register",
            json={"name": "No Class", "email": "noclass@example.com", "password": "secret123"},
        )
        self.assertEqual(missing_class.status_code, 400)

        logout = self.client.post("/api/auth/logout", headers=self.auth(token))
        self.assertEqual(logout.status_code, 200)
        bad = self.client.post(
            "/api/auth/login",
            json={"email": "test.child@example.com", "password": "wrongpass"},
        )
        self.assertEqual(bad.status_code, 401)

    def test_teacher_registration_requires_invite_code(self):
        blocked = self.client.post(
            "/api/auth/register",
            json={
                "name": "Fake Teacher",
                "email": "fake.teacher@example.com",
                "password": "secret123",
                "role": "teacher",
            },
        )
        self.assertEqual(blocked.status_code, 403)

        allowed = self.client.post(
            "/api/auth/register",
            json={
                "name": "Real Teacher",
                "email": "real.teacher@example.com",
                "password": "secret123",
                "role": "teacher",
                "invite_code": "IAFS2026",
            },
        )
        self.assertEqual(allowed.status_code, 201, allowed.get_data(as_text=True))
        self.assertEqual(allowed.get_json()["user"]["role"], "teacher")

    def test_role_based_access(self):
        student = self.login("aarav@iafs.school", "Student@123")
        teacher = self.login("teacher@iafs.school", "Teacher@123")
        admin = self.login("admin@iafs.school", "Admin@123")

        self.assertEqual(
            self.client.get("/api/teacher/dashboard", headers=self.auth(student)).status_code,
            403,
        )
        self.assertEqual(
            self.client.get("/api/student/dashboard", headers=self.auth(teacher)).status_code,
            403,
        )
        self.assertEqual(
            self.client.get("/api/admin/dashboard", headers=self.auth(teacher)).status_code,
            403,
        )
        self.assertEqual(
            self.client.get("/api/admin/dashboard", headers=self.auth(admin)).status_code,
            200,
        )
        self.assertEqual(self.client.get("/api/subjects").status_code, 401)

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------
    def test_class_aware_subjects_topics_and_lessons(self):
        token = self.login("aarav@iafs.school", "Student@123")
        subjects = self.client.get("/api/subjects", headers=self.auth(token))
        self.assertEqual(subjects.status_code, 200)
        body = subjects.get_json()
        self.assertEqual(body["class_level"], 4)
        self.assertEqual(body["level"], "Primary")
        self.assertEqual(len(body["subjects"]), 2)
        topics_total = {subject["name"]: subject["topics_total"] for subject in body["subjects"]}
        self.assertEqual(topics_total, {"English": 8, "Mathematics": 10})
        self.assertTrue(all(subject["topics_started"] == 0 for subject in body["subjects"]))

        topics = self.client.get("/api/topics?subject=Mathematics", headers=self.auth(token))
        self.assertEqual(topics.status_code, 200)
        rows = topics.get_json()["topics"]
        self.assertEqual(len(rows), 10)
        self.assertTrue(all("Fractions" in row["title"] or row["subject"] == "Mathematics" for row in rows))

        lesson = self.client.get("/api/topics/fractions", headers=self.auth(token))
        self.assertEqual(lesson.status_code, 200, lesson.get_data(as_text=True))
        topic = lesson.get_json()["topic"]
        self.assertTrue(topic["explanation"])
        self.assertTrue(topic["key_points"])
        self.assertTrue(topic["examples"])
        self.assertEqual(len(topic["practice"]), 2)
        for question in topic["practice"]:
            self.assertEqual(len(question["options"]), 4)
            self.assertIn(question["correct_index"], range(4))
            self.assertTrue(question["explanation"])

        blocked = self.client.get("/api/topics/algebra", headers=self.auth(token))
        self.assertEqual(blocked.status_code, 403)

        measurement = self.client.get("/api/topics/measurement", headers=self.auth(token))
        self.assertEqual(measurement.status_code, 200, measurement.get_data(as_text=True))
        self.assertEqual(measurement.get_json()["topic"]["title"], "Measurement")

        mensuration = self.client.get("/api/topics/mensuration", headers=self.auth(token))
        self.assertEqual(mensuration.status_code, 403)

        curriculum = self.client.get(
            "/api/curriculum", headers=self.auth(self.login("teacher@iafs.school", "Teacher@123"))
        )
        self.assertEqual(curriculum.status_code, 200)
        self.assertEqual(curriculum.get_json()["total_topics"], 35)

    # ------------------------------------------------------------------
    # Adaptive quiz
    # ------------------------------------------------------------------
    def test_adaptive_quiz_grading_and_review(self):
        token = self.login("priya@iafs.school", "Student@123")  # Class 8 starts at medium
        start = self.client.post(
            "/api/quizzes/start", headers=self.auth(token), json={"topic_slug": "algebra"}
        )
        self.assertEqual(start.status_code, 201, start.get_data(as_text=True))
        quiz = start.get_json()
        self.assertEqual(quiz["total_questions"], 8)
        self.assertEqual(quiz["class_level"], 8)
        self.assertEqual(quiz["difficulty"], "medium")
        self.assertNotIn("correct_index", quiz["question"])
        self.assertNotIn("explanation", quiz["question"])

        session_id = quiz["session_id"]
        session = get_db().quiz_sessions.find_one({"_id": session_id})
        current = session["questions"][0]
        wrong = (current["correct_index"] + 1) % 4
        easier = self.client.post(
            f"/api/quizzes/{session_id}/answer",
            headers=self.auth(token),
            json={"question_id": current["id"], "selected_index": wrong},
        )
        self.assertEqual(easier.status_code, 200)
        body = easier.get_json()
        self.assertFalse(body["correct"])
        self.assertEqual(body["correct_index"], current["correct_index"])
        self.assertTrue(body["explanation"])
        self.assertEqual(body["next_difficulty"], "easy")
        self.assertEqual(body["next_question"]["difficulty"], "easy")

        # Finish the quiz using the stored correct answers.
        for _ in range(7):
            session = get_db().quiz_sessions.find_one({"_id": session_id})
            current = session["questions"][len(session["answers"])]
            response = self.client.post(
                f"/api/quizzes/{session_id}/answer",
                headers=self.auth(token),
                json={
                    "question_id": current["id"],
                    "selected_index": current["correct_index"],
                },
            )
            self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        final = response.get_json()
        self.assertTrue(final["completed"])
        self.assertEqual(final["score"], 7)
        self.assertEqual(final["result"]["percentage"], 87.5)
        self.assertEqual(final["result"]["category"], "Excellent Performance")
        self.assertEqual(len(final["result"]["answers"]), 8)
        self.assertTrue(final["result"]["difficulty_path"])

        review = self.client.get(
            f"/api/student/results/{final['result']['id']}", headers=self.auth(token)
        )
        self.assertEqual(review.status_code, 200)
        self.assertEqual(len(review.get_json()["result"]["answers"]), 8)

        history = self.client.get("/api/quizzes/history", headers=self.auth(token))
        self.assertEqual(history.status_code, 200)
        self.assertGreaterEqual(len(history.get_json()["results"]), 1)

        bad_limit = self.client.get("/api/quizzes/history?limit=abc", headers=self.auth(token))
        self.assertEqual(bad_limit.status_code, 200, bad_limit.get_data(as_text=True))

    def test_student_cannot_read_another_students_result(self):
        aarav = self.login("aarav@iafs.school", "Student@123")
        priya = self.login("priya@iafs.school", "Student@123")
        _, final = self.complete_quiz(priya, "percentages")
        result_id = final["result"]["id"]

        blocked = self.client.get(
            f"/api/student/results/{result_id}", headers=self.auth(aarav)
        )
        self.assertEqual(blocked.status_code, 404)

        allowed = self.client.get(
            f"/api/student/results/{result_id}", headers=self.auth(priya)
        )
        self.assertEqual(allowed.status_code, 200)

    # ------------------------------------------------------------------
    # Feedback, dashboard and assistant
    # ------------------------------------------------------------------
    def test_feedback_categories(self):
        self.assertEqual(decide_category(None), "Getting Started")
        self.assertEqual(decide_category(10), "Needs Improvement")
        self.assertEqual(decide_category(45), "Needs Practice")
        self.assertEqual(decide_category(70), "Good Progress")
        self.assertEqual(decide_category(90), "Excellent Performance")

    def test_feedback_uses_real_quiz_data(self):
        token = self.login("aarav@iafs.school", "Student@123")
        _, final = self.complete_quiz(token, "addition")
        self.assertEqual(final["score"], 8)

        feedback = self.client.get("/api/feedback", headers=self.auth(token))
        self.assertEqual(feedback.status_code, 200, feedback.get_data(as_text=True))
        body = feedback.get_json()
        latest = body["latest"]
        self.assertIn(latest["category"], body["categories"])
        self.assertIn("average_percentage", latest["metrics"])
        self.assertGreaterEqual(latest["metrics"]["attempts"], 1)
        self.assertTrue(latest["suggestions"])
        self.assertIn("never used", body["explanation"].lower())

        refreshed = self.client.post("/api/feedback/refresh", headers=self.auth(token))
        self.assertEqual(refreshed.status_code, 201)
        self.assertTrue(refreshed.get_json()["latest"]["headline"])

        dashboard = self.client.get("/api/student/dashboard", headers=self.auth(token))
        self.assertEqual(dashboard.status_code, 200, dashboard.get_data(as_text=True))
        dashboard_body = dashboard.get_json()
        self.assertGreaterEqual(dashboard_body["summary"]["attempts"], 1)
        self.assertTrue(dashboard_body["recommendations"])
        self.assertTrue(dashboard_body["subjects"])
        self.assertIn("continue_learning", dashboard_body)
        self.assertTrue(dashboard_body["continue_learning"]["slug"])
        self.assertIn("is_demo", dashboard_body["recent_results"][0])

        progress = self.client.get("/api/student/progress", headers=self.auth(token))
        self.assertEqual(progress.status_code, 200)
        self.assertTrue(progress.get_json()["topics"])

    def test_assistant_is_class_aware_and_does_not_leak_quiz_answers(self):
        token = self.login("aarav@iafs.school", "Student@123")
        reply = self.client.post(
            "/api/assistant/ask",
            headers=self.auth(token),
            json={"message": "Give me the answer for fractions", "topic_slug": "fractions"},
        )
        self.assertEqual(reply.status_code, 200, reply.get_data(as_text=True))
        body = reply.get_json()
        self.assertEqual(body["topic_slug"], "fractions")
        self.assertIn("fractions", body["answer"].lower())
        self.assertIn("won't give", body["answer"].lower())
        self.assertEqual(body["class_level"], 4)
        self.assertTrue(body["suggestions"])

        greeting = self.client.post(
            "/api/assistant/ask", headers=self.auth(token), json={"message": "hello"}
        )
        self.assertEqual(greeting.status_code, 200)
        self.assertEqual(greeting.get_json()["kind"], "greeting")
        self.assertIn("Class 4", greeting.get_json()["answer"])

        # A primary student cannot get secondary content, even when requested.
        secondary = self.client.post(
            "/api/assistant/ask",
            headers=self.auth(token),
            json={"message": "Explain algebra step by step", "topic_slug": "algebra"},
        )
        self.assertEqual(secondary.status_code, 200, secondary.get_data(as_text=True))
        self.assertNotEqual(secondary.get_json()["topic_slug"], "algebra")

        suggestions = self.client.get("/api/assistant/suggestions", headers=self.auth(token))
        self.assertEqual(suggestions.status_code, 200)
        self.assertTrue(suggestions.get_json()["prompts"])

    # ------------------------------------------------------------------
    # Chat + optional focus check
    # ------------------------------------------------------------------
    def test_chat_is_class_scoped_and_analysed(self):
        aarav = self.login("aarav@iafs.school", "Student@123")
        priya = self.login("priya@iafs.school", "Student@123")

        sent = self.client.post(
            "/api/chat/messages",
            headers=self.auth(aarav),
            json={"text": "I do not understand fractions. Please explain again."},
        )
        self.assertEqual(sent.status_code, 201, sent.get_data(as_text=True))
        analysis = sent.get_json()["message"]["analysis"]
        self.assertEqual(analysis["learning_difficulty"], "Possible")
        self.assertEqual(analysis["topic_slug"], "fractions")

        bad_limit = self.client.get("/api/chat/messages?limit=abc", headers=self.auth(aarav))
        self.assertEqual(bad_limit.status_code, 200, bad_limit.get_data(as_text=True))

        class_four = self.client.get("/api/chat/messages", headers=self.auth(aarav))
        self.assertEqual(class_four.status_code, 200)
        texts = [message["text"] for message in class_four.get_json()["messages"]]
        self.assertIn("I do not understand fractions. Please explain again.", texts)
        self.assertTrue(
            all(message["class_level"] in (4, None) for message in class_four.get_json()["messages"])
        )

        class_eight = self.client.get("/api/chat/messages", headers=self.auth(priya))
        self.assertEqual(class_eight.status_code, 200)
        self.assertNotIn(
            "I do not understand fractions. Please explain again.",
            [message["text"] for message in class_eight.get_json()["messages"]],
        )

        my_analysis = self.client.get("/api/chat/my-analysis", headers=self.auth(aarav))
        self.assertEqual(my_analysis.status_code, 200)
        self.assertIn("not emotion detection", my_analysis.get_json()["note"])

        teacher = self.login("teacher@iafs.school", "Teacher@123")
        notice = self.client.post(
            "/api/chat/messages",
            headers=self.auth(teacher),
            json={"text": "Class 4: bring your Maths notebook tomorrow.", "class_level": 4},
        )
        self.assertEqual(notice.status_code, 201)
        self.assertTrue(notice.get_json()["message"]["is_teacher"])

    def test_focus_check_validation_and_privacy_note(self):
        token = self.login("aarav@iafs.school", "Student@123")
        response = self.client.post(
            "/api/engagement",
            headers=self.auth(token),
            json={
                "source": "camera",
                "session_seconds": 60,
                "total_samples": 100,
                "face_detected_samples": 90,
                "head_centered_samples": 70,
                "attentive_samples": 80,
            },
        )
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        record = response.get_json()["record"]
        self.assertEqual(record["face_ratio"], 90.0)
        self.assertEqual(record["engagement_score"], 84.0)
        self.assertEqual(record["attention_score"], 80.0)
        self.assertEqual(record["attention_indicator"], "Strong attention signal")
        self.assertEqual(record["indicator"], "Face visible and centred")
        self.assertIn("never used to grade", response.get_json()["note"])
        self.assertIn("attention estimate", response.get_json()["note"])

        invalid = self.client.post(
            "/api/engagement",
            headers=self.auth(token),
            json={"source": "camera", "total_samples": 0},
        )
        self.assertEqual(invalid.status_code, 400)

        # Manual check-ins have no camera ratios; teacher reports must still work.
        manual = self.client.post(
            "/api/engagement",
            headers=self.auth(token),
            json={"source": "manual", "session_seconds": 45, "focus_level": 4},
        )
        self.assertEqual(manual.status_code, 201, manual.get_data(as_text=True))
        self.assertIsNone(manual.get_json()["record"]["face_ratio"])
        self.assertEqual(manual.get_json()["record"]["attention_score"], 80.0)

        student_id = self.client.get("/api/auth/me", headers=self.auth(token)).get_json()["user"]["id"]
        teacher = self.login("teacher@iafs.school", "Teacher@123")
        detail = self.client.get(
            f"/api/teacher/students/{student_id}", headers=self.auth(teacher)
        )
        self.assertEqual(detail.status_code, 200, detail.get_data(as_text=True))
        self.assertEqual(detail.get_json()["focus"]["face_visible"], 90.0)
        self.assertEqual(detail.get_json()["focus"]["attention"], 80.0)

        latest = self.client.get("/api/engagement/latest", headers=self.auth(token))
        self.assertEqual(latest.status_code, 200)
        self.assertIsNotNone(latest.get_json()["latest"])
        self.assertIn("No images", latest.get_json()["note"])
        self.assertIn("attention estimate", latest.get_json()["note"])

    def test_sentiment_examples(self):
        negative = analyze_message("I am not understanding fractions.")
        self.assertEqual(negative["learning_difficulty"], "Possible")
        self.assertEqual(negative["topic_slug"], "fractions")
        self.assertEqual(negative["sentiment"], "Neutral")

        positive = analyze_message("I understood the concept, it was easy!")
        self.assertEqual(positive["sentiment"], "Positive")
        self.assertEqual(positive["learning_difficulty"], "Low")

        neutral = analyze_message("Hello class")
        self.assertEqual(neutral["sentiment"], "Neutral")
        self.assertEqual(neutral["learning_difficulty"], "Low")

    # ------------------------------------------------------------------
    # Teacher and admin dashboards
    # ------------------------------------------------------------------
    def test_teacher_dashboard_and_student_report(self):
        token = self.login("teacher@iafs.school", "Teacher@123")
        dashboard = self.client.get("/api/teacher/dashboard", headers=self.auth(token))
        self.assertEqual(dashboard.status_code, 200, dashboard.get_data(as_text=True))
        body = dashboard.get_json()
        self.assertGreaterEqual(body["summary"]["students"], 10)
        self.assertEqual(len(body["classes"]), 10)
        self.assertEqual(len(body["subjects"]), 2)
        self.assertTrue(body["weak_topics"] is not None)
        self.assertEqual(len(body["score_distribution"]), 4)
        self.assertEqual(len(body["feedback_categories"]), 5)
        self.assertEqual(
            sum(row["count"] for row in body["feedback_categories"]),
            body["summary"]["students"],
        )

        students = self.client.get("/api/teacher/students", headers=self.auth(token))
        self.assertEqual(students.status_code, 200)
        rows = students.get_json()["students"]
        self.assertGreaterEqual(len(rows), 10)

        filtered = self.client.get(
            "/api/teacher/students?class_level=8", headers=self.auth(token)
        )
        self.assertEqual(filtered.status_code, 200)
        self.assertTrue(all(row["class_level"] == 8 for row in filtered.get_json()["students"]))

        student_id = rows[0]["id"]
        detail = self.client.get(
            f"/api/teacher/students/{student_id}", headers=self.auth(token)
        )
        self.assertEqual(detail.status_code, 200, detail.get_data(as_text=True))
        detail_body = detail.get_json()
        self.assertIn("feedback", detail_body)
        self.assertIn("topics", detail_body)
        self.assertIn("focus", detail_body)

        note = self.client.post(
            "/api/teacher/notes",
            headers=self.auth(token),
            json={"student_id": student_id, "note": "Please revise fractions this week."},
        )
        self.assertEqual(note.status_code, 201)
        self.assertEqual(note.get_json()["note"]["note"], "Please revise fractions this week.")

        classes = self.client.get("/api/teacher/classes", headers=self.auth(token))
        self.assertEqual(classes.status_code, 200)
        self.assertEqual(len(classes.get_json()["classes"]), 10)

        topics = self.client.get("/api/teacher/topics?class_level=8", headers=self.auth(token))
        self.assertEqual(topics.status_code, 200)
        self.assertTrue(topics.get_json()["topics"])

    def test_admin_dashboard_users_and_structure(self):
        token = self.login("admin@iafs.school", "Admin@123")
        dashboard = self.client.get("/api/admin/dashboard", headers=self.auth(token))
        self.assertEqual(dashboard.status_code, 200, dashboard.get_data(as_text=True))
        body = dashboard.get_json()
        self.assertGreaterEqual(body["users"]["students"], 10)
        self.assertEqual(body["content"]["topics"], 35)
        self.assertEqual(len(body["class_counts"]), 10)
        self.assertEqual(len(body["subjects"]), 2)

        users = self.client.get("/api/admin/users", headers=self.auth(token))
        self.assertEqual(users.status_code, 200)
        self.assertGreaterEqual(users.get_json()["total"], 12)

        students = self.client.get("/api/admin/users?role=student", headers=self.auth(token))
        self.assertTrue(all(user["role"] == "student" for user in students.get_json()["users"]))

        structure = self.client.get("/api/admin/classes-subjects", headers=self.auth(token))
        self.assertEqual(structure.status_code, 200)
        self.assertEqual(structure.get_json()["total_topics"], 35)
        self.assertEqual(len(structure.get_json()["classes"]), 10)
        self.assertEqual(len(structure.get_json()["subjects"]), 2)

        created = self.client.post(
            "/api/admin/users",
            headers=self.auth(token),
            json={
                "name": "Admin Created",
                "email": "admin.created@example.com",
                "password": "secret123",
                "role": "student",
                "class_level": 3,
            },
        )
        self.assertEqual(created.status_code, 201, created.get_data(as_text=True))
        new_id = created.get_json()["user"]["id"]

        deactivate = self.client.patch(
            f"/api/admin/users/{new_id}", headers=self.auth(token), json={"is_active": False}
        )
        self.assertEqual(deactivate.status_code, 200)
        self.assertFalse(deactivate.get_json()["user"]["is_active"])

        reset = self.client.post(
            f"/api/admin/users/{new_id}/reset-password",
            headers=self.auth(token),
            json={"password": "newsecret123"},
        )
        self.assertEqual(reset.status_code, 200)

        # Changing a staff account into a student requires a class level.
        staff = self.client.post(
            "/api/admin/users",
            headers=self.auth(token),
            json={
                "name": "Former Teacher",
                "email": "former.teacher@example.com",
                "password": "secret123",
                "role": "teacher",
            },
        )
        self.assertEqual(staff.status_code, 201, staff.get_data(as_text=True))
        staff_id = staff.get_json()["user"]["id"]
        classless = self.client.patch(
            f"/api/admin/users/{staff_id}", headers=self.auth(token), json={"role": "student"}
        )
        self.assertEqual(classless.status_code, 400)
        promoted = self.client.patch(
            f"/api/admin/users/{staff_id}",
            headers=self.auth(token),
            json={"role": "student", "class_level": 5},
        )
        self.assertEqual(promoted.status_code, 200, promoted.get_data(as_text=True))
        student_token = self.login("former.teacher@example.com", "secret123")
        dashboard = self.client.get("/api/student/dashboard", headers=self.auth(student_token))
        self.assertEqual(dashboard.status_code, 200, dashboard.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
