import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  CalendarDays,
  RotateCcw,
  Sparkles,
  Target,
  Users,
} from "lucide-react";

import Alert from "../components/Alert";
import AnswerReview from "../components/AnswerReview";
import { SectionLoader } from "../components/Loading";
import ScoreRing from "../components/ScoreRing";
import {
  CategoryBadge,
  DemoBadge,
  DifficultyPill,
  PageHeader,
  SectionHeading,
} from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { categoryStyle } from "../lib/constants";
import { formatDate, percent } from "../lib/format";
import { useApi, useDocumentTitle } from "../lib/useApi";

export default function ResultReview() {
  const { id } = useParams();
  const { user } = useAuth();
  const isStaff = user?.role === "teacher" || user?.role === "admin";
  const { data, loading, error } = useApi(`/student/results/${id}`);
  useDocumentTitle("Quiz result");

  if (loading && !data) return <SectionLoader label="Loading the quiz result..." />;

  const result = data?.result;
  const backTo = isStaff
    ? result?.student_id
      ? `/teacher/students/${result.student_id}`
      : "/teacher/students"
    : "/progress";
  const backLabel = isStaff ? "Back to student report" : "Back to my progress";

  if (error) {
    return (
      <div className="space-y-4">
        <Alert tone="error">{error}</Alert>
        <Link to={backTo} className="btn-secondary">
          <ArrowLeft className="h-4 w-4" /> {backLabel}
        </Link>
      </div>
    );
  }

  if (!result) return null;

  const style = categoryStyle(result.category);
  const answers = result.answers || [];
  const difficultyPath = result.difficulty_path || [];

  return (
    <div className="animate-fade-in space-y-6">
      <Link
        to={backTo}
        className="inline-flex items-center gap-1.5 text-sm font-semibold text-muted transition hover:text-ink"
      >
        <ArrowLeft className="h-4 w-4" /> {backLabel}
      </Link>

      <PageHeader
        eyebrow={`${result.subject} · Class ${result.class_level}${
          isStaff && result.student_name ? ` · ${result.student_name}` : ""
        }`}
        title={result.topic}
        subtitle={`Completed ${formatDate(result.created_at, { withTime: true })} · adaptive quiz with ${answers.length} questions`}
        actions={
          isStaff ? (
            <Link to={backTo} className="btn-secondary">
              <Users className="h-4 w-4" /> Student report
            </Link>
          ) : (
            <>
              <Link
                to={`/quiz/start?topic=${encodeURIComponent(result.topic_slug)}`}
                className="btn-primary"
              >
                <RotateCcw className="h-4 w-4" /> Try again
              </Link>
              <Link to={`/topics/${result.topic_slug}`} className="btn-secondary">
                Read the lesson
              </Link>
            </>
          )
        }
      />

      <div className={`card overflow-hidden border ${style.soft}`}>
        <div className="grid gap-5 p-5 sm:grid-cols-[auto_1fr] sm:items-center sm:p-6">
          <div className="flex justify-center">
            <ScoreRing value={result.percentage} label="Score" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <CategoryBadge category={result.category} />
              {result.is_demo && <DemoBadge />}
            </div>
            <h2 className="mt-2 text-xl font-extrabold text-ink">
              {result.score} of {result.total} correct
            </h2>
            <p className="mt-1 text-sm leading-relaxed text-ink/80">
              {isStaff ? `${result.student_name || "The student"} scored ` : "You scored "}
              {percent(result.percentage)} on {result.topic}. Read the explanations below to
              see how each answer was marked.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="chip bg-surface/70 text-ink">
                <CalendarDays className="h-3.5 w-3.5" />
                {formatDate(result.created_at)}
              </span>
              <span className="chip bg-surface/70 text-ink">
                <Target className="h-3.5 w-3.5" />
                {answers.filter((answer) => answer.is_correct).length} correct
              </span>
              {difficultyPath.length > 0 && (
                <span className="chip bg-surface/70 capitalize text-ink">
                  Path: {[...new Set(difficultyPath)].join(" → ")}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <SectionHeading
            title="Answer review"
            subtitle="The correct answer, your choice and a simpler example when you need one."
          />
          <AnswerReview answers={answers} />
        </div>

        <div className="space-y-6">
          <section className="card p-5">
            <SectionHeading
              title={isStaff ? "Suggestions from the quiz" : "Suggestions for you"}
              icon={Sparkles}
            />
            <ul className="space-y-2.5">
              {(result.suggestions || []).map((suggestion, index) => (
                <li key={index} className="flex gap-2 text-sm leading-relaxed text-ink/80">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary-500" />
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </section>

          <section className="card p-5">
            <SectionHeading title="Difficulty path" subtitle="How the quiz adapted to you" />
            <ol className="space-y-2">
              {difficultyPath.map((level, index) => (
                <li key={`${level}-${index}`} className="flex items-center gap-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-surface-2 text-[10px] font-bold text-muted">
                    {index + 1}
                  </span>
                  <DifficultyPill difficulty={level} label="Level" />
                </li>
              ))}
            </ol>
          </section>

          <section className="card p-5">
            <SectionHeading title="Keep going" icon={ArrowRight} />
            <div className="space-y-2">
              {isStaff ? (
                <Link to={backTo} className="btn-secondary w-full">
                  <Users className="h-4 w-4" /> Back to the student report
                </Link>
              ) : (
                <Link to="/feedback" className="btn-secondary w-full">
                  See adaptive feedback
                </Link>
              )}
              <Link to="/assistant" className="btn-ghost w-full">
                <Sparkles className="h-4 w-4" /> Ask about a tricky step
              </Link>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
