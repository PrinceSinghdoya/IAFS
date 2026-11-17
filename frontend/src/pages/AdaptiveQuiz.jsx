import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Lightbulb,
  RotateCcw,
  Sparkles,
  Target,
  XCircle,
} from "lucide-react";

import Alert from "../components/Alert";
import { SectionLoader, Spinner } from "../components/Loading";
import ScoreRing from "../components/ScoreRing";
import {
  CategoryBadge,
  DifficultyPill,
  PageHeader,
  ProgressBar,
  SectionHeading,
} from "../components/ui";
import { api } from "../lib/api";
import { categoryStyle, subjectStyle } from "../lib/constants";
import { percent } from "../lib/format";
import { useDocumentTitle } from "../lib/useApi";

export default function AdaptiveQuiz() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const topicSlug = searchParams.get("topic") || "";
  const subject = searchParams.get("subject") || "";

  const [quiz, setQuiz] = useState(null);
  const [question, setQuestion] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const startedRef = useRef(null);

  useDocumentTitle("Adaptive quiz");

  const startQuiz = useCallback(async () => {
    setLoading(true);
    setError("");
    setFeedback(null);
    setResult(null);
    setSelected(null);
    try {
      const body = {};
      if (topicSlug) body.topic_slug = topicSlug;
      else if (subject) body.subject = subject;
      const data = await api.post("/quizzes/start", body);
      setQuiz(data);
      setQuestion(data.question);
    } catch (err) {
      setError(err.message || "Could not start the quiz.");
    } finally {
      setLoading(false);
    }
  }, [topicSlug, subject]);

  useEffect(() => {
    const key = `${topicSlug}|${subject}`;
    if (startedRef.current === key) return;
    startedRef.current = key;
    startQuiz();
  }, [startQuiz, topicSlug, subject]);

  async function answer(index) {
    if (!quiz || !question || feedback || submitting) return;
    setSelected(index);
    setSubmitting(true);
    setError("");
    try {
      const data = await api.post(`/quizzes/${quiz.session_id}/answer`, {
        question_id: question.id,
        selected_index: index,
      });
      setFeedback(data);
      setQuiz((current) => ({
        ...current,
        answered: data.answered,
        score: data.score,
        difficulty: data.next_difficulty || data.difficulty,
      }));
      if (data.completed) {
        setResult(data.result);
      }
    } catch (err) {
      setSelected(null);
      setError(err.message || "Could not check that answer.");
    } finally {
      setSubmitting(false);
    }
  }

  function nextQuestion() {
    if (!feedback?.next_question) return;
    setQuestion(feedback.next_question);
    setFeedback(null);
    setSelected(null);
  }

  if (loading) return <SectionLoader label="Preparing your adaptive quiz..." />;

  if (error && !quiz) {
    return (
      <div className="space-y-4">
        <Alert tone="error">{error}</Alert>
        <Link to="/subjects" className="btn-secondary">
          <ArrowLeft className="h-4 w-4" /> Back to subjects
        </Link>
      </div>
    );
  }

  if (result) {
    const style = categoryStyle(result.category);
    const answeredTotal = result.total || quiz?.total_questions || 0;
    return (
      <div className="animate-fade-in mx-auto max-w-4xl space-y-6">
        <PageHeader
          eyebrow="Quiz complete"
          title={`${result.topic} result`}
          subtitle={`${result.subject} · ${result.score}/${answeredTotal} correct · adaptive difficulty throughout`}
          actions={
            <>
              <Link to="/subjects" className="btn-secondary">
                <ArrowLeft className="h-4 w-4" /> Subjects
              </Link>
              <button type="button" onClick={startQuiz} className="btn-primary">
                <RotateCcw className="h-4 w-4" /> Try again
              </button>
            </>
          }
        />

        <div className={`card overflow-hidden border ${style.soft}`}>
          <div className="grid gap-5 p-5 sm:grid-cols-[auto_1fr] sm:items-center sm:p-6">
            <div className="flex justify-center">
              <ScoreRing value={result.percentage} label="Your score" />
            </div>
            <div>
              <CategoryBadge category={result.category} />
              <h2 className="mt-2 text-xl font-extrabold text-ink">
                {result.percentage >= 60 ? "Nice work!" : "Good effort - let's practise."}
              </h2>
              <p className="mt-1 text-sm leading-relaxed text-ink/80">
                You answered {result.score} of {answeredTotal} questions correctly. The questions
                changed difficulty as you went, so this is a fair picture of your understanding.
              </p>
              <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-xl bg-surface/70 px-2 py-2">
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">Score</p>
                  <p className="text-sm font-bold text-ink">{result.score}/{answeredTotal}</p>
                </div>
                <div className="rounded-xl bg-surface/70 px-2 py-2">
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">Percent</p>
                  <p className="text-sm font-bold text-ink">{percent(result.percentage)}</p>
                </div>
                <div className="rounded-xl bg-surface/70 px-2 py-2">
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">Category</p>
                  <p className="truncate text-sm font-bold text-ink">{result.category}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <section className="card p-5">
            <SectionHeading title="Personalised suggestions" icon={Sparkles} />
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
            <SectionHeading
              title="Topics to practise"
              subtitle="Topics averaging below 60% across your saved quizzes."
              icon={BookOpen}
            />
            {(result.weak_topics || []).length === 0 ? (
              <p className="rounded-xl bg-emerald-50 px-3 py-2.5 text-sm leading-relaxed text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-200">
                No weak topics right now. Keep this up by revisiting a topic you found
                tricky last week.
              </p>
            ) : (
              <div className="space-y-2">
                {result.weak_topics.map((topic) => (
                  <Link
                    key={topic.slug}
                    to={`/topics/${topic.slug}`}
                    className="flex items-center gap-2.5 rounded-xl border border-line px-3 py-2.5 transition hover:bg-surface-2/60"
                  >
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-50 text-xs font-bold text-amber-700 dark:bg-amber-500/15 dark:text-amber-200">
                      {percent(topic.average)}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs font-semibold text-ink">{topic.title}</p>
                      <p className="text-[10px] text-muted">{topic.subject}</p>
                    </div>
                    <ArrowRight className="h-4 w-4 shrink-0 text-muted" />
                  </Link>
                ))}
              </div>
            )}
          </section>
        </div>

        <section className="card p-5">
          <SectionHeading title="What next?" icon={Target} />
          <div className="grid gap-2 sm:grid-cols-3">
            <Link to={`/results/${result.id}`} className="btn-primary w-full">
              Review every answer <ArrowRight className="h-4 w-4" />
            </Link>
            <Link to={`/topics/${result.topic_slug}`} className="btn-secondary w-full">
              Read the {result.topic} lesson
            </Link>
            <Link to="/assistant" className="btn-ghost w-full">
              <Sparkles className="h-4 w-4" /> Ask the assistant
            </Link>
          </div>
          <p className="mt-3 text-[11px] leading-relaxed text-muted">
            Your feedback page has already been refreshed with this result.
          </p>
        </section>
      </div>
    );
  }

  if (!quiz || !question) return null;

  const style = subjectStyle(quiz.subject);
  const answered = feedback ? feedback.answered : quiz.answered;
  const total = quiz.total_questions || feedback?.total || 8;
  const progress = total ? (answered / total) * 100 : 0;

  return (
    <div className="animate-fade-in mx-auto max-w-3xl space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <Link
          to={`/topics/${quiz.topic.slug}`}
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-muted transition hover:text-ink"
        >
          <ArrowLeft className="h-4 w-4" /> Back to the lesson
        </Link>
        <div className="flex items-center gap-2">
          <span className="chip bg-surface-2 text-muted">
            Question {Math.min(answered + 1, total)} of {total}
          </span>
          <DifficultyPill difficulty={question.difficulty} />
        </div>
      </div>

      <div className={`card overflow-hidden border ${style.border}`}>
        <div className={`flex flex-wrap items-center justify-between gap-3 px-5 py-4 ${style.soft}`}>
          <div className="flex items-center gap-3">
            <span className="sticker h-10 w-10 bg-surface text-xl shadow-sm">
              {quiz.topic.emoji || "📘"}
            </span>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.14em]">
                {quiz.subject} · Class {quiz.class_level}
              </p>
              <h1 className="text-lg font-extrabold text-ink">{quiz.topic.title}</h1>
            </div>
          </div>
          <div className="text-right">
            <p className="text-[10px] font-bold uppercase tracking-wide text-muted">Score</p>
            <p className="text-lg font-extrabold text-ink">
              {quiz.score}
              <span className="text-sm text-muted">/{total}</span>
            </p>
          </div>
        </div>

        <div className="px-5 pt-4">
          <ProgressBar value={progress} tone={style.bar} />
          <p className="mt-1.5 text-[11px] text-muted">
            {answered} answered · difficulty adapts after every question
          </p>
        </div>

        <div className="p-5 sm:p-6">
          <p className="text-lg font-bold leading-snug text-ink sm:text-xl">{question.question}</p>

          <div className="mt-4 grid gap-2.5">
            {question.options.map((option, index) => {
              const isChosen = selected === index;
              const isCorrect = feedback && index === feedback.correct_index;
              const isWrongChoice = feedback && isChosen && !feedback.correct;
              return (
                <button
                  key={index}
                  type="button"
                  disabled={Boolean(feedback) || submitting}
                  onClick={() => answer(index)}
                  className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-left text-sm font-medium transition ${
                    isCorrect
                      ? "border-emerald-300 bg-emerald-50 text-emerald-900 dark:border-emerald-400/40 dark:bg-emerald-500/15 dark:text-emerald-100"
                      : isWrongChoice
                        ? "border-rose-300 bg-rose-50 text-rose-900 dark:border-rose-400/40 dark:bg-rose-500/15 dark:text-rose-100"
                        : isChosen && submitting
                          ? "border-primary-300 bg-primary-50 text-primary-900 dark:border-primary-400/40 dark:bg-primary-500/15 dark:text-primary-100"
                          : "border-line bg-surface-2/40 text-ink hover:border-primary-300 hover:bg-surface-2 disabled:hover:border-line disabled:hover:bg-surface-2/40"
                  }`}
                >
                  <span
                    className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-[11px] font-bold ${
                      isCorrect
                        ? "bg-emerald-500 text-white"
                        : isWrongChoice
                          ? "bg-rose-500 text-white"
                          : "bg-surface text-muted"
                    }`}
                  >
                    {String.fromCharCode(65 + index)}
                  </span>
                  <span className="flex-1">{option}</span>
                  {isCorrect && <CheckCircle2 className="h-4 w-4 shrink-0" />}
                  {isWrongChoice && <XCircle className="h-4 w-4 shrink-0" />}
                </button>
              );
            })}
          </div>

          {submitting && !feedback && (
            <p className="mt-3 inline-flex items-center gap-2 text-xs font-medium text-muted">
              <Spinner className="h-3.5 w-3.5" /> Checking your answer...
            </p>
          )}

          {error && (
            <div className="mt-3">
              <Alert tone="error">{error}</Alert>
            </div>
          )}

          {feedback && (
            <div className="mt-5 animate-fade-in rounded-2xl border border-line bg-surface-2/50 p-4">
              <p
                className={`inline-flex items-center gap-1.5 text-sm font-bold ${
                  feedback.correct
                    ? "text-emerald-600 dark:text-emerald-300"
                    : "text-rose-600 dark:text-rose-300"
                }`}
              >
                {feedback.correct ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  <XCircle className="h-4 w-4" />
                )}
                {feedback.correct ? "Correct!" : "Not quite."}
              </p>
              <p className="mt-2 text-sm leading-relaxed text-ink/85">{feedback.explanation}</p>
              {feedback.simpler_example && (
                <p className="mt-3 flex items-start gap-2 rounded-xl border border-sun-200 bg-sun-50/80 px-3 py-2.5 text-xs leading-relaxed text-amber-900 dark:border-sun-400/25 dark:bg-sun-500/10 dark:text-amber-100">
                  <Lightbulb className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                  <span>
                    <span className="font-semibold">Simpler example: </span>
                    {feedback.simpler_example}
                  </span>
                </p>
              )}
              {feedback.next_difficulty && (
                <p className="mt-2 text-[11px] text-muted">
                  Next question difficulty:{" "}
                  <span className="font-semibold capitalize text-ink">{feedback.next_difficulty}</span>
                </p>
              )}
              <button type="button" onClick={nextQuestion} className="btn-primary mt-4 w-full">
                Next question <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          )}

          {!feedback && !submitting && (
            <p className="mt-4 text-center text-[11px] text-muted">
              Choose one answer. You will see the explanation straight away.
            </p>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-2 text-[11px] text-muted">
        <span className="chip bg-surface-2 text-muted">Easy → Medium → Hard</span>
        <span className="chip bg-surface-2 text-muted">8 questions</span>
        <span className="chip bg-surface-2 text-muted">Answers explained</span>
        <button
          type="button"
          onClick={() => navigate("/subjects")}
          className="font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-300"
        >
          Leave quiz
        </button>
      </div>
    </div>
  );
}
