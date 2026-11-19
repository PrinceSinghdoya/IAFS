# IAFS — Final Project Report

**Intelligent Adaptive Feedback System for Classes 1–10 English and Mathematics**

A full-stack school learning platform with adaptive quizzes, transparent rule-based feedback, a class-aware learning assistant, an optional privacy-safe focus check, and real database-backed dashboards for teachers and administrators.

---

## A. Audit of the starting project

The project already existed as a React 18 / Vite / Tailwind CSS frontend with a Flask + MongoDB backend, JWT authentication, three roles and cloud deployment configuration. The task was to finish and harden it rather than rebuild it, so the stack, auth model and deployment files were preserved.

The audit found and fixed these problems:

| # | Problem found | Fix applied |
| --- | --- | --- |
| 1 | Curriculum covered only 32 topics and some class/subject pages showed the wrong totals. | Grew the catalogue to **35 topics** (8 Primary English, 10 Primary Mathematics, 8 Secondary English, 9 Secondary Mathematics), each with explanation, examples, key points, class tips and a question generator. |
| 2 | Some dashboard numbers were placeholders or not traceable to records. | All summary, subject, topic, feedback and activity numbers now come from MongoDB queries. |
| 3 | Demo/seed records were indistinguishable from real activity. | Added an `is_demo` flag through serializers and a reusable **Demo** badge in the UI. |
| 4 | Teacher links to a student's result opened a page that only students could access. | Moved `/results/:id` into the shared signed-in route group and made `ResultReview` role-aware. |
| 5 | Teacher dashboard read the wrong field names for classes/subjects and used an outdated class-row shape. | Corrected to `subject.subject`, `subject.topics`, and the current analytics payload. |
| 6 | Admin role changes left stale class fields on non-student accounts. | Role updates now clear class-only fields when the role is not `student`. |
| 7 | Recommendation items lacked curriculum icons, so topic icons rendered incorrectly. | Recommendation and topic payloads now include `icon`. |
| 8 | The "Apply" button on the teacher student search sat outside its form. | Moved it inside the form so Enter and click both work. |
| 9 | Dark mode was incomplete on several pages and camera copy was light-only. | Swept every page onto semantic tokens (`bg-canvas`, `bg-surface`, `bg-surface-2`, `text-ink`, `text-muted`, `border-line`). |
| 10 | Old `/materials` and `/quizzes` links were dead after the page rebuild. | Kept them as redirects to the new routes. |
| 11 | Several old pages were unreferenced and still shipped in the bundle. | Removed unused pages and added a proper `NotFound`. |
| 12 | Demo credentials in `run-dev.ps1` used the wrong email domain. | Corrected to `@iafs.school`. |

The result is a working platform whose behaviour can be explained line by line: every score, category and recommendation maps to a stored record and a readable Python rule.

---

## B. Features delivered

### Student
- Register or sign in and choose a class from 1 to 10.
- Dashboard with real averages, best score, topics started, streak, subject averages, recent results, a **Continue learning** card and a next recommended step.
- Browse English and Mathematics for the Primary (1–5) or Secondary (6–10) level. A student only ever sees their own level.
- Every topic has an explanation, worked examples, key points, class-specific tips, illustrations, practice questions, answers and explanations.
- **Adaptive quiz**: 8 multiple-choice questions, four options each, graded on the server. The correct answer never leaves the server before submission.
  - A wrong answer returns the correct option, an explanation and a simpler retry.
  - A correct answer moves the next question to a harder difficulty.
  - Repeated struggle drops the difficulty again.
  - The end screen shows score, percentage, category, weak topics and suggestions.
- Full answer review after every quiz.
- Progress and feedback pages generated from saved results.
- Class-scoped chat with transparent sentiment/learning-signal analysis.
- Optional focus check that uses the camera only after explicit permission.
- Complete light/dark theme, responsive layout and keyboard-friendly controls.

### Teacher
- Overview of students, active students, attempts, averages, weak topics, a **feedback mix** card, score distribution and students needing support.
- Filterable student list by class, subject and search term.
- Individual student report: performance, subject and topic breakdown, strengths, focus topics, result history, feedback, focus checks, class messages and private notes.
- Class and subject performance pages.
- Class-aware learning assistant for planning explanations.

### Administrator
- School overview: account totals, active accounts, curriculum size, school average and weekly activity.
- User directory: create accounts, correct names/roles/classes, reset passwords and deactivate access.
- Curriculum catalogue with all 35 topics, level filters and search.
- Full access to teacher analytics pages.

### Cross-cutting
- Role enforcement on both frontend routes and backend endpoints.
- Server-side grading and answer privacy.
- Reusable demo labelling.
- Semantic-colour dark mode saved in `localStorage`.
- Responsive layouts from phone to desktop.
- Privacy-safe camera behaviour with cleanup.

---

## C. How the original objectives are met

| Original objective | How it is met |
| --- | --- |
| Adaptive learning | Server-side difficulty changes after each answer: harder after success, simpler after a mistake, further simplification after repeated struggle. The path is stored on the result. |
| Personalised feedback | A transparent rule engine (`services/feedback_engine.py`) combines quiz percentages, topics started, correct-vs-attempted, recent trend, streak and an optional chat support signal into one of five categories, plus focus topics, strengths and next steps. |
| Sentiment / learning-signal analysis | `services/sentiment.py` uses readable keyword and phrase rules to label messages as positive, neutral or negative and to detect topic keywords. It is described honestly as rule-based, not machine learning. |
| Learning assistant | A curated, class-aware knowledge base (`assistant_kb.py`) explains concepts, gives worked examples and refuses to reveal quiz answers. |
| Optional camera focus check | MediaPipe detects face presence, rough centring and head orientation. Only aggregate counts are saved; no images, video, identity or emotion data. The app works fully without a camera and offers a manual check-in. |
| Teacher and admin dashboards | All figures are computed from MongoDB collections (`learning_results`, `quiz_sessions`, `adaptive_feedback`, `class_messages`, `focus_sessions`, `teacher_notes`). No fabricated analytics. |
| Classes 1–10 coverage | 35 topics across Primary and Secondary English and Mathematics, with class-specific tips and difficulty scaling. |
| Privacy | Passwords hashed, JWT bearer tokens, class-scoped chat, staff-only reports, no public leaderboard, no camera recording or upload. |
| Accessibility and themes | Semantic colour tokens, complete dark mode persisted in `localStorage`, visible focus rings, labelled icon buttons and responsive layouts. |

---

## D. Technology

| Layer | Tools |
| --- | --- |
| Frontend | React 18, Vite 6, React Router 6, Tailwind CSS 3, Recharts, lucide-react |
| Backend | Python 3, Flask 3, PyJWT, flask-cors, PyMongo |
| Database | MongoDB |
| Optional camera check | MediaPipe Tasks Vision (loaded only on the focus page) |
| Testing | Python `unittest` end-to-end API suite, plus a PowerShell API check script |
| Deployment | Vercel (frontend), Render/Railway (backend), `Procfile`, `railway.json`, `render.yaml`, `vercel.json` |

`npm run build` writes the compiled frontend to `frontend/dist` (Vercel). `npm run build:backend` writes it to `backend/static` so Flask can serve the SPA and API from one port.

---

## E. Key files

### Backend
| File | Purpose |
| --- | --- |
| `backend/app.py` | Flask app factory, blueprint registration, SPA and deep-link serving |
| `backend/config.py` | Environment configuration |
| `backend/db.py` | MongoDB client and indexes |
| `backend/curriculum.py` | Subjects, 35 topics, question generators, adaptive difficulty |
| `backend/assistant_kb.py` | Class-aware assistant knowledge base and topic detection |
| `backend/auth_utils.py` | Password hashing, JWT, role guards, `public_user` |
| `backend/utils.py` | Serializers including `serialize_result` and `is_demo` |
| `backend/seed.py`, `backend/seed_data.py` | Idempotent demo accounts and fictional activity |
| `backend/routes/auth.py` | Register, login, profile, logout |
| `backend/routes/content.py` | Subjects, topics, lessons, curriculum |
| `backend/routes/quizzes.py` | Adaptive sessions, server-side grading, weak-topic persistence |
| `backend/routes/student.py` | Student dashboard, progress, results, continue-learning |
| `backend/routes/feedback.py` | Feedback retrieval and refresh |
| `backend/routes/assistant.py` | Assistant questions and suggestions |
| `backend/routes/chat.py` | Class chat and per-message analysis |
| `backend/routes/engagement.py` | Focus-check save and latest |
| `backend/routes/teacher.py` | Teacher dashboard, students, reports, notes |
| `backend/routes/admin.py` | School overview, users, curriculum |
| `backend/routes/meta.py` | Health and metadata |
| `backend/services/feedback_engine.py` | Snapshots, categories, recommendations |
| `backend/services/analytics.py` | Teacher rows, activity, feedback mix, distributions |
| `backend/services/sentiment.py` | Rule-based sentiment and topic keywords |
| `backend/tests/test_api.py` | 15 end-to-end API tests |

### Frontend
| File | Purpose |
| --- | --- |
| `frontend/src/App.jsx` | Routes, role guards, legacy redirects |
| `frontend/src/components/ProtectedRoute.jsx` | Single-role and multi-role guards |
| `frontend/src/components/ui.jsx` | Shared cards, badges, `DemoBadge`, headings |
| `frontend/src/context/AuthContext.jsx` | Session and role state |
| `frontend/src/context/ThemeContext.jsx` | Light/dark theme with `localStorage` |
| `frontend/src/lib/api.js` | API client |
| `frontend/src/lib/constants.js` | Levels, subjects, styles |
| `frontend/src/pages/StudentDashboard.jsx` | Student overview and Continue learning |
| `frontend/src/pages/Subjects.jsx`, `TopicDetail.jsx` | Curriculum browsing and lessons |
| `frontend/src/pages/AdaptiveQuiz.jsx`, `ResultReview.jsx` | Adaptive quiz and answer review |
| `frontend/src/pages/Progress.jsx`, `Feedback.jsx` | Progress and personalised feedback |
| `frontend/src/pages/Assistant.jsx`, `Chat.jsx` | Learning assistant and class chat |
| `frontend/src/pages/CameraPage.jsx` | Optional focus check |
| `frontend/src/pages/TeacherDashboard.jsx`, `TeacherStudents.jsx`, `TeacherStudentDetail.jsx`, `TeacherClasses.jsx` | Teacher analytics |
| `frontend/src/pages/AdminDashboard.jsx`, `AdminUsers.jsx`, `AdminClassesSubjects.jsx` | Administration |

### Root and deployment
`README.md`, `REPORT.md`, `run-dev.ps1`, `run-production.ps1`, `start-backend.ps1`, `start-frontend.ps1`, `DEPLOYMENT.md`, `Procfile`, `railway.json`, `render.yaml`, `vercel.json`.

---

## F. Testing — what was actually run

All of the following were executed against the current code. Results are reported exactly as observed.

| Check | Command | Result |
| --- | --- | --- |
| Backend end-to-end suite | `python -m unittest discover -s tests -v` (from `backend`) | **15 / 15 passed** |
| Live API checks | PowerShell script against `http://127.0.0.1:5000/api` | **46 / 46 checks passed, 0 failures** |
| Frontend production build | `npm run build` | **Succeeded** |
| Flask-served build | `npm run build:backend` | **Succeeded** |
| Question-generator stress test | 3 new topics × 10 classes × 3 difficulties × 200 questions | **18,000 generated, 0 malformed** (all had 4 unique options and a valid correct index) |

The 15 backend tests cover:

1. Health and metadata
2. Register, login, profile and logout
3. Role-based access
4. Teacher invite codes
5. Class-aware subjects, topics and lessons
6. Adaptive quiz grading and review
7. Feedback categories
8. Feedback generated from real quiz data
9. Chat scoping and sentiment analysis
10. Focus-check validation and privacy
11. Teacher dashboard and student report
12. Admin dashboard, users and structure
13. Assistant class-awareness and answer privacy
14. Result privacy
15. Quiz summary and weak-topic persistence

The suite uses a separate `iafs_test` database and drops it afterwards, so demo data is untouched.

### Live smoke checks (verified after the final restart)
- `GET /api/health` returned `status: ok` and a live MongoDB connection.
- Class 4 could open `Measurement` but received **403** for `Mensuration` (correct level restriction).
- Class 8 could open `Mensuration` with practice questions.
- Student dashboard returned a populated `continue_learning` object.
- Teacher `feedback_categories` summed exactly to the student count.
- Demo flags were present on student, teacher and admin payloads.
- Assistant routed "metres to centimetres", "volume of a cuboid" and "change from 100 rupees" to Measurement, Mensuration and Time and Money respectively.
- A started quiz did **not** expose `correct_index` in the question payload.
- SPA deep links (`/`, `/topics/measurement`, `/teacher/dashboard`, `/results/abc`) all returned HTTP 200 with the React root.

---

## G. How to run

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB running locally, or a MongoDB URI

### Backend
```powershell
cd backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env      # first run only
python seed.py                   # safe to re-run; adds only missing demo records
python app.py
```
API: `http://127.0.0.1:5000` — health: `http://127.0.0.1:5000/api/health`

### Frontend (development)
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`. Vite proxies `/api` to Flask.

### Single-server (production-style)
```powershell
cd frontend
npm run build:backend
cd ..\backend
python app.py
```
Open `http://127.0.0.1:5000`.

### Windows shortcuts
```powershell
.\run-dev.ps1          # backend + Vite
.\run-production.ps1   # build and serve from Flask
```

### Tests
```powershell
cd backend
python -m unittest discover -s tests -v
```

### Environment (`backend/.env`)
```
MONGO_URI=mongodb://127.0.0.1:27017
DB_NAME=iafs
JWT_SECRET=change-this-to-a-long-random-string
JWT_EXPIRES_HOURS=12
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
TEACHER_INVITE_CODE=IAFS2026
```

---

## H. Suggested demo flow

1. **Start** the backend (`python app.py`) and the frontend (`npm run dev`), or use the single-server build.
2. **Sign in as a student** — `aarav@iafs.school` / `Student@123` (Class 4).
   - Show the dashboard: real averages, Continue learning card, subject progress and recommendations.
   - Open **Subjects → Mathematics → Measurement**, read the explanation, examples and class tips.
   - Start the adaptive quiz. Answer one question wrongly and show the simpler explanation; answer correctly and show the next question getting harder.
   - Finish the quiz and show the summary: score, category, weak topics and suggestions.
   - Open the result review to show every answer and explanation.
3. **Open the assistant** and ask "How do I convert metres to centimetres?" to show a class-appropriate answer.
4. **Open the focus check** and show that the camera is requested only after an explicit click, then stop it and confirm cleanup. Mention that the app is fully usable without it.
5. **Sign in as a teacher** — `teacher@iafs.school` / `Teacher@123`.
   - Show the overview, feedback mix, weak topics and score distribution.
   - Filter students and open a student report; show topic breakdown, feedback, focus checks and notes.
   - Open a student's result from the report to confirm staff can review it.
6. **Sign in as an admin** — `admin@iafs.school` / `Admin@123`.
   - Show school totals and the curriculum catalogue with all 35 topics.
   - Show the user directory and the demo badges.
7. **Toggle dark mode** on several pages to show persisted theme and readable contrast.
8. **Resize** the window to phone width to show the drawer navigation and responsive cards.

Demo accounts use fictional data only. Seeded records display a small **Demo** badge so no one mistakes them for real learners.

---

## I. Limitations (stated honestly)

- **Rule-based, not machine learning.** The adaptive engine, feedback categories and sentiment analysis are transparent Python rules. They are not a trained model and are described that way in the UI and README.
- **Curated assistant.** The assistant is a class-aware knowledge base, not a hosted large language model. It is deterministic and free to run, but it does not handle arbitrary open-ended conversation.
- **Camera is a proxy.** The focus check estimates face presence and rough centring only. It does not measure real attention, understanding or emotion, and it never affects grades.
- **Camera dependency.** The focus check needs a modern browser with WebAssembly and camera permission; it degrades to a manual check-in.
- **MongoDB required.** The backend needs a reachable MongoDB; `/api/health` reports `degraded` if it cannot connect.
- **Bundle size.** The optional MediaPipe bundle is large, so the build emits a chunk-size warning; it is loaded only on the focus page.
- **No public sharing.** There is intentionally no leaderboard, public profile or social feature.
- **Manual verification.** Frontend verification was done through production builds and live API/SPA smoke checks; there is no automated browser test suite yet.

---

## J. Next improvements

1. **Spaced repetition** — schedule topic reviews based on past accuracy and time since last attempt.
2. **Richer language analysis** — move from keyword rules to a small, well-documented classifier, keeping explanations visible to teachers.
3. **Teacher assignments** — let teachers set a topic or quiz for a class and track completion.
4. **Automated frontend tests** — add Playwright or Vitest coverage for routing, role guards and quiz flow.
5. **Accessibility audit** — run a full WCAG pass with screen-reader and keyboard-only testing.
6. **Offline-first lessons** — cache lesson content so students on weak connections can read without the API.
7. **Exportable reports** — PDF/CSV export for teacher and admin reporting.
8. **Configurable quiz length** — allow 5, 8 or 12 questions per session.
9. **More curriculum topics** — extend each subject/level with additional practice sets and worked solutions.
10. **Commit and deploy** — the current changes are uncommitted; commit them and run the existing Vercel/Render/Railway configuration for a live demo.

---

## Repository status

- Git branch: `main`, last commit `51105ff Update project`.
- All changes described here are currently **uncommitted** (20 modified files plus this report).
- `frontend/dist` and `backend/static` are generated and git-ignored.
- Verified state: backend running on `http://127.0.0.1:5000`, 15/15 backend tests passing, 46/46 live API checks passing, both frontend builds succeeding.
