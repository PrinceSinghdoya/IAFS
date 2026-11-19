import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  Camera,
  CheckCircle2,
  MessageCircle,
  NotebookPen,
  Sparkles,
  Target,
} from "lucide-react";

import Alert from "../components/Alert";
import { SectionLoader, Spinner } from "../components/Loading";
import {
  Avatar,
  CategoryBadge,
  DemoBadge,
  EmptyState,
  PageHeader,
  ProgressBar,
  SectionHeading,
  StatCard,
  StatusBadge,
} from "../components/ui";
import { api } from "../lib/api";
import { TREND_LABELS, classLevelLabel, subjectStyle } from "../lib/constants";
import { formatDate, percent, relativeTime } from "../lib/format";
import { useApi, useDocumentTitle } from "../lib/useApi";

export default function TeacherStudentDetail() {
  const { id } = useParams();
  const { data, loading, error, reload } = useApi(`/teacher/students/${id}`);
  const [note, setNote] = useState("");
  const [savingNote, setSavingNote] = useState(false);
  const [noteError, setNoteError] = useState("");
  const [noteSaved, setNoteSaved] = useState(false);
  useDocumentTitle("Student report");

  async function addNote(event) {
    event.preventDefault();
    if (!note.trim()) return;
    setSavingNote(true);
    setNoteError("");
    setNoteSaved(false);
    try {
      await api.post("/teacher/notes", { student_id: id, note: note.trim() });
      setNote("");
      setNoteSaved(true);
      await reload();
    } catch (err) {
      setNoteError(err.message || "Could not save the note.");
    } finally {
      setSavingNote(false);
    }
  }

  if (loading && !data) return <SectionLoader label="Loading the student report..." />;
  if (error) {
    return (
      <div className="space-y-4">
        <Alert tone="error">{error}</Alert>
        <Link to="/teacher/students" className="btn-secondary">
          <ArrowLeft className="h-4 w-4" /> Back to students
        </Link>
      </div>
    );
  }

  const { student, summary, subjects, topics, strengths, focus_topics, results, feedback, notes, focus, messages } = data;
  const trend = TREND_LABELS[summary.trend] || TREND_LABELS.steady;

  return (
    <div className="animate-fade-in space-y-6">
      <Link
        to="/teacher/students"
        className="inline-flex items-center gap-1.5 text-sm font-semibold text-muted transition hover:text-ink"
      >
        <ArrowLeft className="h-4 w-4" /> Back to students
      </Link>

      <div className="card p-5">
        <div className="flex flex-wrap items-start gap-4">
          <Avatar name={student.name} size="lg" />
          <div className="min-w-0 flex-1">
            <p className="text-[11px] font-bold uppercase tracking-[0.14em] text-primary-600 dark:text-primary-300">
              Student report
            </p>
            <h1 className="mt-1 text-2xl font-extrabold tracking-tight text-ink">{student.name}</h1>
            <p className="text-sm text-muted">
              {student.email} · {classLevelLabel(student.class_level)}
              {student.section ? `-${student.section}` : ""}
              {student.roll_no ? ` · Roll ${student.roll_no}` : ""}
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              <CategoryBadge category={summary.category} />
              {student.is_demo && <DemoBadge />}
              <span className={`chip bg-surface-2 ${trend.tone}`}>{trend.label}</span>
              <span className="chip bg-surface-2 text-muted">
                Last activity: {summary.last_activity ? formatDate(summary.last_activity) : "None"}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Average" value={percent(summary.average)} icon={Target} tone="blue" />
        <StatCard label="Best" value={percent(summary.best)} icon={CheckCircle2} tone="emerald" />
        <StatCard
          label="Quizzes"
          value={summary.attempts}
          icon={Sparkles}
          tone="violet"
          helper={`${summary.topics_started}/${summary.topics_total} topics started`}
        />
        <StatCard label="Streak" value={summary.streak_days ?? 0} suffix=" days" icon={Sparkles} tone="sun" />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <section className="card p-5">
            <SectionHeading title="Subject averages" />
            <div className="grid gap-4 sm:grid-cols-2">
              {subjects.map((subject) => {
                const style = subjectStyle(subject.subject);
                return (
                  <div key={subject.subject}>
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-ink">{subject.subject}</span>
                      <span className="font-semibold text-muted">{percent(subject.average)}</span>
                    </div>
                    <div className="mt-1.5">
                      <ProgressBar value={subject.average || 0} tone={style.bar} />
                    </div>
                    <p className="mt-1 text-[10px] text-muted">
                      {subject.topics_started}/{subject.topics_total} topics · {subject.topics_strong} strong
                    </p>
                  </div>
                );
              })}
            </div>
          </section>

          <section className="card overflow-hidden">
            <div className="border-b border-line px-5 py-4">
              <SectionHeading title="Topic performance" subtitle="One row per topic in the student's class" />
            </div>
            <div className="max-h-[26rem] overflow-auto">
              <table className="min-w-full divide-y divide-line">
                <thead className="sticky top-0 bg-surface-2">
                  <tr>
                    <th className="table-th">Topic</th>
                    <th className="table-th">Attempts</th>
                    <th className="table-th">Best</th>
                    <th className="table-th">Average</th>
                    <th className="table-th">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {topics.map((topic) => (
                    <tr key={topic.slug} className="hover:bg-surface-2/40">
                      <td className="table-td">
                        <span className="text-xs font-semibold text-ink">
                          {topic.emoji} {topic.title}
                        </span>
                        <p className="text-[10px] text-muted">{topic.subject}</p>
                      </td>
                      <td className="table-td text-muted">{topic.attempts}</td>
                      <td className="table-td">{percent(topic.best)}</td>
                      <td className="table-td">{percent(topic.average)}</td>
                      <td className="table-td">
                        <StatusBadge status={topic.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="card p-5">
            <SectionHeading title="Quiz history" subtitle="Most recent first" />
            {results.length === 0 ? (
              <EmptyState icon={Target} title="No quizzes completed" description="This student has not finished a quiz yet." />
            ) : (
              <div className="space-y-2">
                {results.map((result) => (
                  <Link
                    key={result.id}
                    to={`/results/${result.id}`}
                    className="flex items-center gap-2.5 rounded-xl border border-line px-3 py-2.5 transition hover:bg-surface-2/60"
                  >
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-surface-2 text-xs font-bold text-ink">
                      {Math.round(result.percentage ?? 0)}%
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs font-semibold text-ink">{result.topic}</p>
                      <p className="text-[10px] text-muted">
                        {result.subject} · {result.score}/{result.total} · {formatDate(result.created_at)}
                      </p>
                    </div>
                    <CategoryBadge category={result.category} />
                    {result.is_demo && <DemoBadge label="Demo" />}
                  </Link>
                ))}
              </div>
            )}
          </section>
        </div>

        <div className="space-y-6">
          {feedback && (
            <section className="card p-5">
              <SectionHeading title="Current feedback" icon={Sparkles} />
              <CategoryBadge category={feedback.category} />
              <p className="mt-2 text-sm font-bold text-ink">{feedback.headline}</p>
              <p className="mt-1 text-xs leading-relaxed text-muted">{feedback.message}</p>
              <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-lg bg-surface-2 px-2 py-1.5">
                  <p className="text-[9px] uppercase text-muted">Avg</p>
                  <p className="text-xs font-bold text-ink">{percent(feedback.metrics?.average_percentage)}</p>
                </div>
                <div className="rounded-lg bg-surface-2 px-2 py-1.5">
                  <p className="text-[9px] uppercase text-muted">Best</p>
                  <p className="text-xs font-bold text-ink">{percent(feedback.metrics?.best_percentage)}</p>
                </div>
                <div className="rounded-lg bg-surface-2 px-2 py-1.5">
                  <p className="text-[9px] uppercase text-muted">Correct</p>
                  <p className="text-xs font-bold text-ink">
                    {feedback.metrics?.total_correct ?? 0}/{feedback.metrics?.total_questions ?? 0}
                  </p>
                </div>
              </div>
            </section>
          )}

          <section className="card p-5">
            <SectionHeading title="Strengths and focus" />
            <p className="text-[10px] font-bold uppercase tracking-wide text-muted">Strengths</p>
            {strengths.length === 0 ? (
              <p className="mt-1 text-xs text-muted">None yet.</p>
            ) : (
              <div className="mt-1.5 space-y-1">
                {strengths.map((topic) => (
                  <div key={topic.slug} className="flex justify-between gap-2 text-xs">
                    <span className="truncate text-ink">{topic.title}</span>
                    <span className="font-semibold text-emerald-600 dark:text-emerald-300">
                      {percent(topic.average)}
                    </span>
                  </div>
                ))}
              </div>
            )}
            <p className="mt-3 text-[10px] font-bold uppercase tracking-wide text-muted">Focus topics</p>
            {focus_topics.length === 0 ? (
              <p className="mt-1 text-xs text-muted">No weak topics.</p>
            ) : (
              <div className="mt-1.5 space-y-1">
                {focus_topics.map((topic) => (
                  <div key={topic.slug} className="flex justify-between gap-2 text-xs">
                    <span className="truncate text-ink">{topic.title}</span>
                    <span className="font-semibold text-amber-600 dark:text-amber-300">
                      {percent(topic.average)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="card p-5">
            <SectionHeading title="Private teacher notes" icon={NotebookPen} />
            <form onSubmit={addNote} className="space-y-2">
              {noteError && <Alert tone="error">{noteError}</Alert>}
              {noteSaved && <Alert tone="success">Note saved.</Alert>}
              <textarea
                value={note}
                onChange={(event) => setNote(event.target.value)}
                rows={3}
                maxLength={1000}
                placeholder="Add a private observation, support plan or follow-up..."
                className="input resize-none"
              />
              <button type="submit" disabled={savingNote || !note.trim()} className="btn-primary w-full py-2 text-xs">
                {savingNote ? <Spinner className="h-3.5 w-3.5" /> : <NotebookPen className="h-3.5 w-3.5" />}
                Save note
              </button>
            </form>
            <div className="mt-3 max-h-48 space-y-2 overflow-y-auto">
              {notes.length === 0 ? (
                <p className="text-xs text-muted">No notes yet. Only staff can see these.</p>
              ) : (
                notes.map((item) => (
                  <div key={item.id} className="rounded-lg border border-line bg-surface-2/40 px-3 py-2">
                    <p className="text-[11px] leading-relaxed text-ink/85">{item.note}</p>
                    <p className="mt-1 text-[9px] text-muted">
                      {item.teacher_name} · {relativeTime(item.created_at)}
                    </p>
                  </div>
                ))
              )}
            </div>
          </section>

          <section className="card p-5">
            <SectionHeading title="Optional focus checks" icon={Camera} />
            {focus.sessions === 0 ? (
              <p className="text-xs leading-relaxed text-muted">
                No focus checks saved. They are optional and never affect grades.
              </p>
            ) : (
              <>
                <div className="grid grid-cols-2 gap-2 text-center sm:grid-cols-4">
                  <div className="rounded-lg bg-surface-2 px-2 py-1.5">
                    <p className="text-[9px] uppercase text-muted">Sessions</p>
                    <p className="text-xs font-bold text-ink">{focus.sessions}</p>
                  </div>
                  <div className="rounded-lg bg-primary-50/70 px-2 py-1.5 dark:bg-primary-500/10">
                    <p className="text-[9px] uppercase text-primary-700 dark:text-primary-200">
                      Attention
                    </p>
                    <p className="text-xs font-bold text-ink">{percent(focus.attention)}</p>
                  </div>
                  <div className="rounded-lg bg-surface-2 px-2 py-1.5">
                    <p className="text-[9px] uppercase text-muted">Face</p>
                    <p className="text-xs font-bold text-ink">{percent(focus.face_visible)}</p>
                  </div>
                  <div className="rounded-lg bg-surface-2 px-2 py-1.5">
                    <p className="text-[9px] uppercase text-muted">Centred</p>
                    <p className="text-xs font-bold text-ink">{percent(focus.head_centered)}</p>
                  </div>
                </div>
                <p className="mt-2 text-[10px] leading-relaxed text-muted">
                  Attention is an optional camera proxy, not a grade or a
                  judgement of understanding.
                </p>
              </>
            )}
          </section>

          <section className="card p-5">
            <SectionHeading title="Recent class messages" icon={MessageCircle} />
            {messages.length === 0 ? (
              <p className="text-xs text-muted">No class messages from this student.</p>
            ) : (
              <div className="space-y-2">
                {messages.map((message) => (
                  <div key={message.id} className="rounded-lg border border-line px-3 py-2">
                    <p className="text-[11px] leading-relaxed text-ink/85">{message.text}</p>
                    <p className="mt-1 text-[9px] text-muted">{relativeTime(message.created_at)}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>

      <div className="flex justify-end">
        <Link to="/teacher/students" className="btn-secondary">
          All students <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
