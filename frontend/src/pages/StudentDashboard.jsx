import { Link } from "react-router-dom";
import {
  ArrowRight,
  BookOpen,
  Brain,
  CheckCircle2,
  Flame,
  MessageCircle,
  Play,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";

import Alert from "../components/Alert";
import FeedbackCard from "../components/FeedbackCard";
import { SectionLoader } from "../components/Loading";
import {
  CategoryBadge,
  EmptyState,
  PageHeader,
  ProgressBar,
  SectionHeading,
  StatCard,
  StatusBadge,
} from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { classLevelLabel, subjectStyle, topicIcon } from "../lib/constants";
import { formatDate, greeting, percent } from "../lib/format";
import { useApi, useDocumentTitle } from "../lib/useApi";

export default function StudentDashboard() {
  const { user } = useAuth();
  const { data, loading, error } = useApi("/student/dashboard");
  useDocumentTitle("Dashboard");

  if (loading && !data) return <SectionLoader label="Loading your dashboard..." />;
  if (error) return <Alert tone="error">{error}</Alert>;
  if (!data) return null;

  const { summary, subjects, recent_results, recommendations, feedback, latest_message } = data;
  const firstName = (user?.name || data.user?.name || "Student").split(" ")[0];

  return (
    <div className="animate-fade-in space-y-6">
      <PageHeader
        eyebrow={`${greeting()}, ${firstName}`}
        title="Your learning today"
        subtitle={`${classLevelLabel(data.class_level)} · ${data.level} English and Mathematics. Small steps every day make a big difference.`}
        actions={
          <>
            <Link to="/subjects" className="btn-primary">
              <BookOpen className="h-4 w-4" />
              Start learning
            </Link>
            <Link to="/assistant" className="btn-secondary">
              <Sparkles className="h-4 w-4" />
              Ask the assistant
            </Link>
          </>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Average score"
          value={percent(summary.average)}
          icon={Target}
          tone="blue"
          helper={`${summary.attempts} quiz${summary.attempts === 1 ? "" : "zes"} completed`}
        />
        <StatCard
          label="Best score"
          value={percent(summary.best)}
          icon={TrendingUp}
          tone="emerald"
          helper="Your highest quiz result so far"
        />
        <StatCard
          label="Topics started"
          value={`${summary.topics_started}/${summary.topics_total}`}
          icon={BookOpen}
          tone="violet"
          helper={`${summary.strong_topics} strong · ${summary.focus_topics} to review`}
        />
        <StatCard
          label="Learning streak"
          value={summary.streak_days ?? 0}
          suffix=" days"
          icon={Flame}
          tone="sun"
          helper="Days in a row with a completed quiz"
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="space-y-6 xl:col-span-2">
          <section>
            <SectionHeading
              title="Your subjects"
              subtitle="Every topic has a lesson, examples and an adaptive quiz."
              action={
                <Link to="/subjects" className="link inline-flex items-center gap-1 text-sm">
                  View all <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              }
            />
            <div className="grid gap-4 sm:grid-cols-2">
              {subjects.map((subject) => {
                const style = subjectStyle(subject.subject);
                const Icon = style.icon;
                const coverage = subject.topics_total
                  ? Math.round((subject.topics_started / subject.topics_total) * 100)
                  : 0;
                return (
                  <div key={subject.subject} className="card card-hover p-5">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-[11px] font-bold uppercase tracking-wide text-muted">
                          {subject.subject}
                        </p>
                        <p className="mt-1 text-2xl font-extrabold text-ink">
                          {percent(subject.average)}
                        </p>
                        <p className="text-xs text-muted">
                          {subject.topics_started} of {subject.topics_total} topics started
                        </p>
                      </div>
                      <span className={`flex h-11 w-11 items-center justify-center rounded-2xl ${style.soft}`}>
                        <Icon className="h-5 w-5" />
                      </span>
                    </div>
                    <div className="mt-4">
                      <ProgressBar value={coverage} tone={style.bar} />
                      <p className="mt-1.5 text-[11px] text-muted">{coverage}% of topics started</p>
                    </div>
                    <div className="mt-4 flex gap-2">
                      <Link
                        to={`/subjects?subject=${encodeURIComponent(subject.subject)}`}
                        className="btn-secondary flex-1 py-2 text-xs"
                      >
                        Open lessons
                      </Link>
                      <Link
                        to={`/quiz/start?subject=${encodeURIComponent(subject.subject)}`}
                        className="btn-primary flex-1 py-2 text-xs"
                      >
                        <Play className="h-3.5 w-3.5" />
                        Quiz me
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          <section>
            <SectionHeading
              title="Recommended next steps"
              subtitle="Chosen from your weakest topics and topics you have not started."
              icon={Brain}
            />
            {recommendations.length === 0 ? (
              <EmptyState
                icon={Sparkles}
                title="You are all caught up"
                description="Start a new topic or try a harder quiz to keep learning."
                action={
                  <Link to="/subjects" className="btn-primary">
                    Browse topics
                  </Link>
                }
              />
            ) : (
              <div className="grid gap-3 sm:grid-cols-2">
                {recommendations.map((item) => {
                  const Icon = topicIcon(item.icon);
                  return (
                    <div key={`${item.slug}-${item.action}`} className="card p-4">
                      <div className="flex items-start gap-3">
                        <span className="sticker bg-surface-2 text-lg">{item.emoji || "📘"}</span>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-bold text-ink">{item.title}</p>
                          <p className="mt-0.5 text-[11px] font-semibold uppercase tracking-wide text-muted">
                            {item.subject}
                          </p>
                          <p className="mt-1.5 text-xs leading-relaxed text-muted">{item.reason}</p>
                          <div className="mt-3 flex flex-wrap gap-2">
                            <Link to={`/topics/${item.slug}`} className="btn-secondary py-1.5 text-xs">
                              <Icon className="h-3.5 w-3.5" />
                              Lesson
                            </Link>
                            <Link
                              to={`/quiz/start?topic=${encodeURIComponent(item.slug)}`}
                              className="btn-primary py-1.5 text-xs"
                            >
                              {item.action || "Try quiz"}
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          <section>
            <SectionHeading
              title="Recent quiz results"
              subtitle="Open any result to review every answer and explanation."
              action={
                <Link to="/progress" className="link inline-flex items-center gap-1 text-sm">
                  Full progress <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              }
            />
            {recent_results.length === 0 ? (
              <EmptyState
                icon={CheckCircle2}
                title="No quizzes yet"
                description="Your first quiz will appear here with a full answer review."
              />
            ) : (
              <div className="card divide-y divide-line">
                {recent_results.map((result) => (
                  <Link
                    key={result.id}
                    to={`/results/${result.id}`}
                    className="flex flex-wrap items-center gap-3 px-4 py-3.5 transition hover:bg-surface-2/60"
                  >
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-surface-2 text-sm font-bold text-ink">
                      {Math.round(result.percentage ?? 0)}%
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold text-ink">{result.topic}</p>
                      <p className="text-[11px] text-muted">
                        {result.subject} · {result.score}/{result.total} correct ·{" "}
                        {formatDate(result.created_at)}
                      </p>
                    </div>
                    <CategoryBadge category={result.category} />
                  </Link>
                ))}
              </div>
            )}
          </section>
        </div>

        <div className="space-y-6">
          <FeedbackCard feedback={feedback} />

          <div className="card p-5">
            <SectionHeading title="Quick actions" icon={Sparkles} />
            <div className="space-y-2">
              <Link
                to="/quiz/start"
                className="flex items-center gap-3 rounded-xl border border-line bg-surface-2/40 px-3 py-2.5 text-sm font-semibold text-ink transition hover:border-primary-300"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-50 text-primary-600 dark:bg-primary-500/15 dark:text-primary-300">
                  <Play className="h-4 w-4" />
                </span>
                Adaptive quiz
                <ArrowRight className="ml-auto h-4 w-4 text-muted" />
              </Link>
              <Link
                to="/assistant"
                className="flex items-center gap-3 rounded-xl border border-line bg-surface-2/40 px-3 py-2.5 text-sm font-semibold text-ink transition hover:border-primary-300"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-50 text-accent-600 dark:bg-accent-500/15 dark:text-accent-300">
                  <MessageCircle className="h-4 w-4" />
                </span>
                Learning assistant
                <ArrowRight className="ml-auto h-4 w-4 text-muted" />
              </Link>
              <Link
                to="/chat"
                className="flex items-center gap-3 rounded-xl border border-line bg-surface-2/40 px-3 py-2.5 text-sm font-semibold text-ink transition hover:border-primary-300"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-sun-100 text-sun-600 dark:bg-sun-500/15 dark:text-sun-300">
                  <BookOpen className="h-4 w-4" />
                </span>
                Class chat
                <ArrowRight className="ml-auto h-4 w-4 text-muted" />
              </Link>
            </div>
          </div>

          <div className="card p-5">
            <SectionHeading title="Topic status" subtitle="Your current class topics" />
            <div className="space-y-2.5">
              {feedback?.focus_topics?.length ? (
                feedback.focus_topics.map((topic) => (
                  <div key={topic.slug} className="flex items-center justify-between gap-2">
                    <span className="truncate text-xs font-medium text-ink">{topic.title}</span>
                    <StatusBadge status="Needs review" />
                  </div>
                ))
              ) : (
                <p className="text-xs text-muted">
                  Complete a quiz to see which topics need a little more practice.
                </p>
              )}
              {feedback?.strengths?.length ? (
                <div className="mt-3 border-t border-line pt-3">
                  <p className="mb-2 text-[10px] font-bold uppercase tracking-wide text-muted">
                    Strengths
                  </p>
                  {feedback.strengths.map((topic) => (
                    <div key={topic.slug} className="mb-1.5 flex items-center justify-between gap-2">
                      <span className="truncate text-xs font-medium text-ink">{topic.title}</span>
                      <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-300">
                        {percent(topic.percentage)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          </div>

          {latest_message && (
            <div className="card p-5">
              <SectionHeading title="Latest in class chat" icon={MessageCircle} />
              <p className="text-sm leading-relaxed text-ink/80">{latest_message.text}</p>
              <p className="mt-2 text-[11px] text-muted">
                {latest_message.student_name || "Class notice"} · {formatDate(latest_message.created_at, { withTime: true })}
              </p>
              <Link to="/chat" className="link mt-3 inline-flex items-center gap-1 text-sm">
                Open class chat <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
