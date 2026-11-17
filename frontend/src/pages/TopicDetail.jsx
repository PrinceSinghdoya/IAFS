import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  Lightbulb,
  Play,
  Sparkles,
  Target,
  XCircle,
} from "lucide-react";

import Alert from "../components/Alert";
import { SectionLoader } from "../components/Loading";
import {
  CategoryBadge,
  EmptyState,
  PageHeader,
  ProgressBar,
  SectionHeading,
  StatusBadge,
} from "../components/ui";
import { classLevelLabel, subjectStyle, topicIcon } from "../lib/constants";
import { formatDate, percent } from "../lib/format";
import { useApi, useDocumentTitle } from "../lib/useApi";

function PracticeQuestion({ question, index }) {
  const [selected, setSelected] = useState(null);
  const answered = selected !== null;
  const isCorrect = answered && selected === question.correct_index;

  return (
    <div className="rounded-2xl border border-line bg-surface p-4">
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-surface-2 text-xs font-bold text-ink">
          {index + 1}
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold leading-relaxed text-ink">{question.question}</p>
          <div className="mt-3 grid gap-1.5 sm:grid-cols-2">
            {question.options.map((option, optionIndex) => {
              const isChosen = selected === optionIndex;
              const correct = answered && optionIndex === question.correct_index;
              return (
                <button
                  key={optionIndex}
                  type="button"
                  disabled={answered}
                  onClick={() => setSelected(optionIndex)}
                  className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-left text-xs transition ${
                    correct
                      ? "border-emerald-300 bg-emerald-50 text-emerald-900 dark:border-emerald-400/30 dark:bg-emerald-500/10 dark:text-emerald-100"
                      : isChosen
                        ? "border-rose-300 bg-rose-50 text-rose-900 dark:border-rose-400/30 dark:bg-rose-500/10 dark:text-rose-100"
                        : "border-line bg-surface-2/40 text-ink hover:border-primary-300"
                  } ${answered ? "cursor-default" : ""}`}
                >
                  <span className="text-[10px] font-bold uppercase text-muted">
                    {String.fromCharCode(65 + optionIndex)}
                  </span>
                  <span className="flex-1">{option}</span>
                  {correct && <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />}
                  {isChosen && !correct && <XCircle className="h-3.5 w-3.5 shrink-0" />}
                </button>
              );
            })}
          </div>
          {answered && (
            <div className="mt-3 space-y-2">
              <p
                className={`text-xs font-semibold ${
                  isCorrect
                    ? "text-emerald-600 dark:text-emerald-300"
                    : "text-rose-600 dark:text-rose-300"
                }`}
              >
                {isCorrect ? "Correct!" : "Not quite - check the explanation below."}
              </p>
              <p className="rounded-lg bg-surface-2/70 px-3 py-2 text-xs leading-relaxed text-ink/80">
                <span className="font-semibold text-ink">Explanation: </span>
                {question.explanation}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function TopicDetail() {
  const { slug } = useParams();
  const { data, loading, error } = useApi(`/topics/${slug}`);
  useDocumentTitle(data?.topic?.title || "Topic lesson");

  if (loading && !data) return <SectionLoader label="Loading the lesson..." />;
  if (error) {
    return (
      <div className="space-y-4">
        <Alert tone="error">{error}</Alert>
        <Link to="/subjects" className="btn-secondary">
          <ArrowLeft className="h-4 w-4" /> Back to subjects
        </Link>
      </div>
    );
  }
  if (!data?.topic) return null;

  const topic = data.topic;
  const style = subjectStyle(topic.subject);
  const Icon = topicIcon(topic.icon);
  const progress = topic.progress || {};
  const paragraphs = (topic.explanation || "").split("\n\n").filter(Boolean);

  return (
    <div className="animate-fade-in space-y-6">
      <Link
        to={`/subjects?subject=${encodeURIComponent(topic.subject)}`}
        className="inline-flex items-center gap-1.5 text-sm font-semibold text-muted transition hover:text-ink"
      >
        <ArrowLeft className="h-4 w-4" /> Back to {topic.subject}
      </Link>

      <div className={`card overflow-hidden border ${style.border}`}>
        <div className={`bg-gradient-to-r px-5 py-6 ${style.soft}`}>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="flex items-start gap-4">
              <span className="sticker h-14 w-14 bg-surface text-2xl shadow-sm">
                {topic.emoji}
              </span>
              <div>
                <p className="text-[11px] font-bold uppercase tracking-[0.14em]">
                  {topic.subject} · {classLevelLabel(data.class_level)} · {topic.level}
                </p>
                <h1 className="mt-1 text-2xl font-extrabold tracking-tight text-ink sm:text-3xl">
                  {topic.title}
                </h1>
                <p className="mt-1.5 max-w-2xl text-sm leading-relaxed text-ink/75">
                  {topic.description}
                </p>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge status={progress.status || "Not started"} />
              <Link
                to={`/quiz/start?topic=${encodeURIComponent(topic.slug)}`}
                className="btn-primary"
              >
                <Play className="h-4 w-4" />
                Start quiz
              </Link>
            </div>
          </div>
        </div>

        <div className="grid gap-4 px-5 py-4 sm:grid-cols-3">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wide text-muted">Your best</p>
            <p className="mt-0.5 text-lg font-extrabold text-ink">{percent(progress.best)}</p>
          </div>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wide text-muted">Average</p>
            <p className="mt-0.5 text-lg font-extrabold text-ink">{percent(progress.average)}</p>
          </div>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wide text-muted">Attempts</p>
            <p className="mt-0.5 text-lg font-extrabold text-ink">{progress.attempts || 0}</p>
          </div>
        </div>
        <div className="px-5 pb-5">
          <ProgressBar value={progress.best || 0} tone={style.bar} />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <section className="card p-5 sm:p-6">
            <SectionHeading title="Simple explanation" icon={BookOpen} />
            <div className="lesson-body space-y-3">
              {paragraphs.map((paragraph, index) => (
                <p key={index}>{paragraph}</p>
              ))}
            </div>

            {topic.class_tip && (
              <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-sun-200 bg-sun-50/70 px-3.5 py-3 text-sm leading-relaxed text-amber-900 dark:border-sun-400/25 dark:bg-sun-500/10 dark:text-amber-100">
                <Lightbulb className="mt-0.5 h-4 w-4 shrink-0" />
                <p>
                  <span className="font-semibold">Tip for Class {data.class_level}: </span>
                  {topic.class_tip}
                </p>
              </div>
            )}
          </section>

          <section className="card p-5 sm:p-6">
            <SectionHeading
              title="Examples"
              subtitle="Look at one worked example before you try the quiz."
              icon={Sparkles}
            />
            <div className="grid gap-3 sm:grid-cols-2">
              {(topic.examples || []).map((example, index) => (
                <div
                  key={`${example.title}-${index}`}
                  className="rounded-2xl border border-line bg-surface-2/40 p-4"
                >
                  <span className="text-2xl">{example.emoji || "✨"}</span>
                  <p className="mt-2 text-sm font-bold text-ink">{example.title}</p>
                  <p className="mt-1 text-xs leading-relaxed text-ink/75">{example.body}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="card p-5 sm:p-6">
            <SectionHeading
              title="Practice questions"
              subtitle="Try these before the quiz. Answers are explained immediately."
              icon={Target}
            />
            <div className="space-y-3">
              {(topic.practice || []).map((question, index) => (
                <PracticeQuestion key={question.id || index} question={question} index={index} />
              ))}
            </div>
          </section>
        </div>

        <div className="space-y-6">
          <section className="card p-5">
            <SectionHeading title="Key points" icon={CheckCircle2} />
            <ul className="space-y-2">
              {(topic.key_points || []).map((point, index) => (
                <li key={index} className="flex gap-2 text-sm leading-relaxed text-ink/80">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary-500" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </section>

          <section className="card p-5">
            <SectionHeading title="Your recent results" icon={ArrowRight} />
            {(topic.recent_results || []).length === 0 ? (
              <EmptyState
                icon={Target}
                title="No results yet"
                description="Finish the quiz and your score will appear here."
              />
            ) : (
              <div className="space-y-2">
                {topic.recent_results.map((result) => (
                  <Link
                    key={result._id}
                    to={`/results/${result._id}`}
                    className="flex items-center gap-2.5 rounded-xl border border-line px-3 py-2.5 transition hover:bg-surface-2/60"
                  >
                    <span className="text-sm font-extrabold text-ink">
                      {Math.round(result.percentage || 0)}%
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-[11px] text-muted">
                        {result.score}/{result.total} · {formatDate(result.created_at)}
                      </p>
                    </div>
                    <CategoryBadge category={result.category} />
                  </Link>
                ))}
              </div>
            )}
          </section>

          <section className="card bg-gradient-to-br from-accent-50 to-primary-50 p-5 dark:from-accent-500/10 dark:to-primary-500/10">
            <SectionHeading title="Need a simpler explanation?" icon={Sparkles} />
            <p className="text-sm leading-relaxed text-ink/80">
              Ask the learning assistant about {topic.title}. It explains the method and gives a
              similar example, but never reveals live quiz answers.
            </p>
            <Link to={`/assistant?topic=${encodeURIComponent(topic.slug)}`} className="btn-secondary mt-3 w-full">
              <Sparkles className="h-4 w-4" />
              Ask about this topic
            </Link>
          </section>

          <button
            type="button"
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            className="btn-ghost w-full text-xs"
          >
            <ChevronDown className="h-4 w-4 rotate-180" /> Back to top
          </button>
        </div>
      </div>
    </div>
  );
}
