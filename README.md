# IAFS — School Learning for Classes 1–10

IAFS is a full-stack learning platform for primary and secondary school English and Mathematics. Students read short, illustrated lessons, take adaptive multiple-choice quizzes, get feedback built from their real results, and ask a class-aware learning assistant for help. Teachers and administrators get live, database-backed dashboards for classes, students, topics and progress.

The project is intentionally easy to explain: every score, category and recommendation can be traced to saved MongoDB records and readable Python rules. All demo data is fictional — no real children's information, photos or videos are stored. Seeded records carry an `is_demo` flag and appear with a small **Demo** badge in the interface.

---

## 1. What each role can do

### Student
- Register or sign in; choose a class from 1 to 10.
- Dashboard with real averages, best score, topics started, streak, subject progress, a **Continue learning** card, recent results and the next recommended step.
- Browse **English** and **Mathematics** topics for the Primary (Classes 1–5) or Secondary (Classes 6–10) curriculum.
- Every topic has an explanation, worked examples, key points, class-specific tips, illustrations, practice questions, answers and explanations.
- Take an **adaptive quiz**: 8 MCQs, four options each, instant feedback after every answer, a simpler retry after mistakes and a harder question after success.
- End-of-quiz summary with score, percentage, category, topics that need practice and personalised suggestions.
- Review every question and answer afterwards.
- Personal **progress** and **feedback** pages generated from saved quiz results.
- Class chat, plus an optional focus check with a privacy-safe attention estimate that uses the camera only when explicitly allowed.
- Light/dark theme, responsive layout and keyboard-friendly controls.

### Teacher
- Overview of students, activity, averages, weak topics, feedback mix, score distribution and students needing support.
- Filterable student list by class, subject and search term.
- Individual student report: performance, subject/topic breakdown, strengths, focus topics, result history, feedback, focus checks, class messages and private teacher notes.
- Class and subject performance pages.
- Access to the learning assistant for planning explanations.

### Administrator
- School overview: account totals, active accounts, curriculum size, school average and weekly activity.
- User directory: create accounts, correct names/roles/classes, reset passwords and deactivate access.
- Classes and subjects catalogue with all 35 topics, level filters and search.
- Full access to the teacher analytics pages.

---

## 2. Curriculum

Two subjects, two levels and **35 topics** in total: 8 Primary English, 10 Primary Mathematics, 8 Secondary English and 9 Secondary Mathematics.

| Level | Classes | English | Mathematics |
| --- | --- | --- | --- |
| Primary | 1–5 | Alphabet Recognition, Basic Vocabulary, Naming Words, Articles, Simple Sentences, Basic Grammar, Reading Comprehension, Spelling Practice | Counting, Addition, Subtraction, Multiplication, Division, Number Patterns, Basic Shapes, Fractions, Measurement, Time and Money |
| Secondary | 6–10 | Parts of Speech, Tenses, Active and Passive Voice, Direct and Indirect Speech, Vocabulary Building, Sentence Correction, Reading Comprehension, Basic Writing Skills | Integers, Fractions and Decimals, Percentages, Ratio and Proportion, Algebra, Geometry, Linear Equations, Basic Statistics, Mensuration |

A student only sees topics for their own level. Quiz difficulty starts easier for younger classes and adapts from there.

---

## 3. How the adaptive quiz works

1. The student starts a quiz for a topic (or lets the app pick the weakest topic for a subject).
2. The server stores a session and sends one question at a time — the correct answer never leaves the server.
3. Each answer is graded server-side. The response contains:
   - whether the answer was correct and which option was correct,
   - an explanation and a simpler example,
   - the running score and progress,
   - the next question at an easier or harder level.
4. After 8 questions the session is finalized:
   - the result is saved to `learning_results`,
   - the student's feedback is regenerated immediately,
   - weak topics are recomputed from all saved results.
5. The summary shows the score, percentage, category, topics to practise and suggestions. The result review page shows every question, the chosen answer, the correct answer and the explanation.

---

## 4. Personalised feedback

Feedback is produced by a transparent rule engine (`backend/services/feedback_engine.py`) using real evidence:

- quiz percentages and best score,
- number of topics started versus available,
- correct answers versus questions attempted,
- recent score trend,
- learning streak,
- optional class-chat help signal (supporting only — never emotion or ability detection).

The five categories are:

1. Getting Started
2. Needs Improvement
3. Needs Practice
4. Good Progress
5. Excellent Performance

Each feedback record includes a headline, message, metrics, focus topics, strengths and next-step suggestions. The same data powers the student dashboard, the feedback page and teacher reports.

---

## 5. Learning assistant

`/assistant` is available to every signed-in role.

- Answers are class-aware: explanations use the vocabulary and depth of the student's class.
- The assistant explains concepts and gives examples.
- It is explicitly instructed **not** to reveal quiz answers; it teaches the method instead.
- Teachers and administrators can choose a class level to preview explanations.
- Prompt chips and topic suggestions come from the curriculum API.

---

## 6. Privacy and the optional camera

- No camera access happens by default. The browser asks for permission only when the student presses the start button on `/camera`.
- The focus check detects **face presence, rough centring and head orientation only**. Its **attention estimate** is the share of sampled frames where the face was visible and roughly turned toward the camera. It does not recognise identity, read emotions, estimate ability or store images or video.
- Only aggregate counts are saved (session length, samples with a face, samples roughly centred, attentive samples and the resulting attention estimate). The estimate is a proxy, not a judgement of real attention or understanding, and it never affects grades.
- The app works fully without the camera; a manual check-in is offered as an alternative.
- Student performance is visible to the student and to signed-in staff only. There is no public leaderboard or shareable performance page.
- Passwords are stored only as hashes; sessions use signed JWT bearer tokens.

---

## 7. Interface and themes

- Palette: blue, purple and warm yellow, with rounded cards and friendly but age-neutral typography.
- Complete light/dark theme:
  - toggle in the top navigation on every page, with sun and moon icons,
  - choice saved in `localStorage`,
  - colours driven by semantic CSS variables (`canvas`, `surface`, `surface-2`, `ink`, `muted`, `line`) so every page has readable contrast.
- Responsive from small phones to wide desktops: fixed sidebar on desktop, slide-over drawer on mobile, horizontally scrollable tables.
- Accessible labels on icon buttons, visible focus rings and reduced reliance on colour alone.

---

## 8. Technology

| Layer | Tools |
| --- | --- |
| Frontend | React 18, Vite 6, React Router 6, Tailwind CSS 3, Recharts, lucide-react |
| Backend | Python 3, Flask 3, PyJWT, flask-cors, PyMongo |
| Database | MongoDB |
| Optional camera check | MediaPipe Tasks Vision (loaded only on the focus page) |

The frontend lives in `frontend/`, the API in `backend/`. `npm run build` writes the compiled app into `frontend/dist` (used by Vercel); `npm run build:backend` writes it into `backend/static`, so Flask can serve the SPA and the API from one port.

---

## 9. Repository layout

```
iafs/
├─ backend/
│  ├─ app.py                 # Flask app factory, API registration, SPA serving
│  ├─ config.py              # environment configuration
│  ├─ db.py                  # MongoDB client and indexes
│  ├─ curriculum.py          # subjects, 35 topics, question generator
│  ├─ seed.py / seed_data.py # demo accounts and fictional activity
│  ├─ auth_utils.py          # hashing, JWT, role guards
│  ├─ assistant_kb.py        # class-aware assistant knowledge base
│  ├─ routes/                # auth, content, quizzes, student, feedback,
│  │                         # chat, engagement, teacher, admin, assistant, meta
│  ├─ services/              # feedback engine, analytics, sentiment
│  ├─ tests/test_api.py      # 15 end-to-end API tests
│  └─ static/                # built frontend (generated)
├─ frontend/
│  ├─ src/App.jsx            # routes and role guards
│  ├─ src/pages/             # student, teacher and admin pages
│  ├─ src/components/        # layout, cards, badges, theme toggle, loaders
│  ├─ src/context/           # auth and theme providers
│  └─ src/lib/               # API client, constants, formatting, hooks
├─ run-dev.ps1               # start backend and Vite in separate windows
├─ run-production.ps1        # build frontend and serve everything from Flask
└─ start-backend.ps1 / start-frontend.ps1
```

---

## 10. Getting started

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB running locally (or a MongoDB URI)

### 1. Backend
```powershell
cd backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env      # first run only
python seed.py                   # safe to run again; creates demo data
python app.py
```
The API runs at `http://127.0.0.1:5000`. Health check: `http://127.0.0.1:5000/api/health`.

### 2. Frontend (development)
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`. Vite proxies API calls to the Flask server.

### 3. Single-server mode (production-style)
```powershell
cd frontend
npm run build:backend
cd ..\backend
python app.py
```
Open `http://127.0.0.1:5000`. Flask serves the built SPA, deep links and the API.

On Windows, `.\run-dev.ps1` and `.\run-production.ps1` wrap the steps above.

### Environment variables (`backend/.env`)
```
MONGO_URI=mongodb://127.0.0.1:27017
DB_NAME=iafs
JWT_SECRET=change-this-to-a-long-random-string
JWT_EXPIRES_HOURS=12
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
TEACHER_INVITE_CODE=IAFS2026
```

---

## 11. Demo accounts

All accounts use fictional names and data.

| Role | Email | Password | Notes |
| --- | --- | --- | --- |
| Administrator | `admin@iafs.school` | `Admin@123` | Full access, user management |
| Teacher | `teacher@iafs.school` | `Teacher@123` | Analytics, reports and notes |
| Student | `aarav@iafs.school` | `Student@123` | Class 4 |
| Student | `sara@iafs.school` | `Student@123` | Class 2 |
| Student | `priya@iafs.school` | `Student@123` | Class 8 |
| Student | `arjun@iafs.school` | `Student@123` | Class 9 |

Other seeded students: `kabir@iafs.school` (1), `diya@iafs.school` (3), `ishan@iafs.school` (5), `rohan@iafs.school` (6), `meera@iafs.school` (7), `nisha@iafs.school` (10) — same student password.

Teacher registration requires the invite code from `TEACHER_INVITE_CODE` (`IAFS2026` by default). Student registration is open and asks for a class from 1 to 10.

---

## 12. Main routes

### Student
| Path | Page |
| --- | --- |
| `/student` | Dashboard |
| `/subjects` | English and Mathematics subjects |
| `/topics/:slug` | Lesson, examples, practice questions |
| `/quiz/start?topic=...` | Adaptive quiz |
| `/results/:id` | Full answer review |
| `/progress` | Subject/topic progress and history |
| `/feedback` | Personalised feedback |
| `/assistant` | Learning assistant |
| `/chat` | Class chat |
| `/camera` | Optional focus check |

### Teacher and administrator
| Path | Page |
| --- | --- |
| `/teacher` | Teaching overview |
| `/teacher/students` | Student list with filters |
| `/teacher/students/:id` | Individual student report |
| `/teacher/classes` | Class and subject performance |
| `/assistant` | Class-aware assistant |

### Administrator only
| Path | Page |
| --- | --- |
| `/admin` | School overview |
| `/admin/users` | User directory and account actions |
| `/admin/classes-subjects` | Curriculum catalogue |

Legacy links are kept as redirects: `/materials` → `/subjects`, `/materials/:slug` → `/topics/:slug`, `/quizzes` → `/quiz/start`, `/quizzes/:slug` → `/quiz/start?topic=:slug`.

---

## 13. API overview

All endpoints are under `/api`. Protected endpoints expect `Authorization: Bearer <token>`.

| Area | Endpoints |
| --- | --- |
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `PATCH /auth/profile`, `POST /auth/logout` |
| Content | `GET /subjects`, `GET /topics`, `GET /topics/:slug`, `GET /curriculum` (staff) |
| Quizzes | `POST /quizzes/start`, `POST /quizzes/:session/answer`, `GET /quizzes/:session/result`, `GET /quizzes/history`, `GET /quizzes/summary` |
| Student | `GET /student/dashboard`, `/student/progress`, `/student/results`, `/student/results/:id`, `/student/topics/:slug` |
| Feedback | `GET /feedback`, `POST /feedback/refresh` |
| Assistant | `POST /assistant/ask`, `GET /assistant/suggestions` |
| Chat | `GET /chat/messages`, `POST /chat/messages`, `GET /chat/my-analysis` |
| Focus check | `POST /engagement`, `GET /engagement/latest` |
| Teacher | `GET /teacher/dashboard`, `/teacher/students`, `/teacher/students/:id`, `/teacher/classes`, `/teacher/topics`, `POST /teacher/notes` |
| Admin | `GET /admin/dashboard`, `/admin/users`, `/admin/classes-subjects`, `POST /admin/users`, `PATCH /admin/users/:id`, `POST /admin/users/:id/reset-password` |
| System | `GET /health`, `GET /meta` |

Quiz answers are graded on the server. Question payloads sent to the browser never include the correct option.

---

## 14. Tests

Run the backend suite from the `backend` folder:

```powershell
python -m unittest discover -s tests -v
```

The 15 tests cover registration/login/profile/logout, role-based access, teacher invite codes, class-aware subjects and lessons, adaptive quiz grading and review, feedback categories and real-data feedback, chat scoping and sentiment, focus-check validation and privacy, teacher dashboards and student reports, admin user/structure management, assistant behaviour, and result privacy.

The suite uses a separate `iafs_test` database and drops it afterwards, so demo data is untouched.

For a quick manual check after seeding:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/health
```

---

## 15. Data collections

| Collection | Purpose |
| --- | --- |
| `users` | Accounts, hashed passwords, role, class, section, roll number |
| `classes` / `subjects` | Reference rows for class and subject metadata |
| `learning_results` | Completed quiz results, answers, suggestions, weak topics |
| `quiz_sessions` | In-progress and completed adaptive sessions |
| `adaptive_feedback` | Feedback records generated from real evidence |
| `class_messages` | Class-scoped chat messages |
| `focus_sessions` | Optional aggregate focus-check counts only |
| `teacher_notes` | Private notes written by staff |

---

## 16. Notes and limitations

- The assistant is a curated, class-aware knowledge base, not a hosted large language model. This keeps the demo deterministic and free to run.
- The focus check needs a modern browser with WebAssembly and camera permission; it degrades gracefully to a manual check-in.
- MongoDB must be running before the backend starts. `/api/health` reports `degraded` if it cannot connect.
- The build emits a chunk-size warning because the optional MediaPipe bundle is large; it is only loaded on the focus page.
- There is no public sharing, leaderboard or social feature by design.
