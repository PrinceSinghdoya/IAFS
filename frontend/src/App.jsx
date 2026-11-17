import { Navigate, Route, Routes, useParams } from "react-router-dom";

import AppLayout from "./components/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import ScrollToTop from "./components/ScrollToTop";
import { FullPageLoader } from "./components/Loading";
import { homeForRole, useAuth } from "./context/AuthContext";

import Login from "./pages/Login";
import Register from "./pages/Register";
import StudentDashboard from "./pages/StudentDashboard";
import Subjects from "./pages/Subjects";
import TopicDetail from "./pages/TopicDetail";
import AdaptiveQuiz from "./pages/AdaptiveQuiz";
import ResultReview from "./pages/ResultReview";
import Assistant from "./pages/Assistant";
import Chat from "./pages/Chat";
import CameraPage from "./pages/CameraPage";
import Feedback from "./pages/Feedback";
import Progress from "./pages/Progress";
import TeacherDashboard from "./pages/TeacherDashboard";
import TeacherStudents from "./pages/TeacherStudents";
import TeacherStudentDetail from "./pages/TeacherStudentDetail";
import TeacherClasses from "./pages/TeacherClasses";
import AdminDashboard from "./pages/AdminDashboard";
import AdminUsers from "./pages/AdminUsers";
import AdminClassesSubjects from "./pages/AdminClassesSubjects";
import NotFound from "./pages/NotFound";

/** Sends visitors to their role dashboard, or to the login page. */
function HomeRedirect() {
  const { user, loading } = useAuth();

  if (loading) return <FullPageLoader label="Loading IAFS..." />;
  return <Navigate to={user ? homeForRole(user.role) : "/login"} replace />;
}

/** Keeps old lesson links working after the subject pages were rebuilt. */
function LegacyTopicRedirect() {
  const { slug } = useParams();
  return <Navigate to={`/topics/${slug}`} replace />;
}

/** Old quiz links opened a quiz for a topic slug. */
function LegacyQuizRedirect() {
  const { slug } = useParams();
  return <Navigate to={`/quiz/start?topic=${encodeURIComponent(slug)}`} replace />;
}

export default function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<HomeRedirect />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Student learning */}
        <Route element={<ProtectedRoute role="student" />}>
          <Route element={<AppLayout />}>
            <Route path="/student" element={<StudentDashboard />} />
            <Route path="/subjects" element={<Subjects />} />
            <Route path="/topics/:slug" element={<TopicDetail />} />
            <Route path="/quiz/start" element={<AdaptiveQuiz />} />
            <Route path="/progress" element={<Progress />} />
            <Route path="/feedback" element={<Feedback />} />
            <Route path="/camera" element={<CameraPage />} />
          </Route>
        </Route>

        {/* Shared by every signed-in role */}
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/assistant" element={<Assistant />} />
            <Route path="/chat" element={<Chat />} />
            {/* Staff open the same review page from a student report, so it
                cannot live inside the student-only group. */}
            <Route path="/results/:id" element={<ResultReview />} />
          </Route>
        </Route>

        {/* Teacher and administrator analytics */}
        <Route element={<ProtectedRoute role={["teacher", "admin"]} />}>
          <Route element={<AppLayout />}>
            <Route path="/teacher" element={<TeacherDashboard />} />
            <Route path="/teacher/students" element={<TeacherStudents />} />
            <Route path="/teacher/students/:id" element={<TeacherStudentDetail />} />
            <Route path="/teacher/classes" element={<TeacherClasses />} />
          </Route>
        </Route>

        {/* Administrator only */}
        <Route element={<ProtectedRoute role="admin" />}>
          <Route element={<AppLayout />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/users" element={<AdminUsers />} />
            <Route path="/admin/classes-subjects" element={<AdminClassesSubjects />} />
          </Route>
        </Route>

        {/* Legacy links kept as redirects */}
        <Route path="/materials" element={<Navigate to="/subjects" replace />} />
        <Route path="/materials/:slug" element={<LegacyTopicRedirect />} />
        <Route path="/quizzes" element={<Navigate to="/quiz/start" replace />} />
        <Route path="/quizzes/:slug" element={<LegacyQuizRedirect />} />
        <Route path="/dashboard" element={<HomeRedirect />} />

        {/* Anything else */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  );
}
