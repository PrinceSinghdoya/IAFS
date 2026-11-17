import { useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Award,
  BarChart3,
  CheckCircle2,
  Info,
  RefreshCw,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";

import Alert from "../components/Alert";
import { SectionLoader, Spinner } from "../components/Loading";
import {
  CategoryBadge,
  PageHeader,
  ProgressBar,
  SectionHeading,
} from "../components/ui";
import { api } from "../lib/api";
import { categoryStyle } from "../lib/constants";
import { formatDate, percent } from "../lib/format";
import { useApi, useDocumentTitle } from "../lib/useApi";

const TREND_TEXT = {
  improving: "Your recent scores are moving up.",
  steady: "Your scores are steady.",
  slipping: "Your recent scores dipped a little — review the last explanations.",
};

export default function Feedback() {
  const { data, loading, error, reload, setData } = useApi("/feedback");
  const [refreshing, setRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState("");
  useDocumentTitle("Adaptive feedback");

  async function refresh() {
    setRefreshing(true);
    setRefreshError("");
    try {
      const response = await api.post("/feedback/refresh");
      setData((current) => ({
        ...(current || {}),
        latest: response.latest,
        history: [response.latest, ...((current?.history || []).slice(0, 19))],
      }));
    } catch (err) {
      setRefreshError(err.message || "Could not refresh feedback.");
    } finally {
      setRefreshing(false);
    }
  }

  if (loading && !data) return <SectionLoader label="Building your feedback..." />;
  if (error) return <Alert tone="error">{error}</Alert>;
  if (!data?.latest) return null;

  const { latest, history, categories, explanation } = data;
  const metrics = latest.metrics || {};
  const style = categoryStyle(latest.category);

  const metricCards = [
    { label: "Average", value: percent(metrics.average_percentage), icon: TrendingUp },
    { label: "Best score", value: percent(metrics.best_percentage), icon: Award },
    { label: "Quizzes", value: metrics.attempts ?? 0, icon: BarChart3 },
    {
      label: "Correct answers",
      value: `${metrics.total_correct ?? 0}/${metrics.total_questions ?? 0}`,
      icon: CheckCircle2,
    },
    {
      label: "Topics started",
      value: `${metrics.topics_started ?? 0}/${metrics.topics_total ?? 0}`,
      icon: Target,
    },
    { label: "Streak", value: `${metrics.streak_days ?? 0} days`, icon: Sparkles },
  ];

  return (
    <div className="animate-fade-in space-y-6">
      <PageHeader
        eyebrow="Personalised, explainable feedback"
        title="Adaptive feedback"
        subtitle="Built from your quiz scores, topic coverage and answer accuracy. No random text and no camera judgement."
        actions={
          <button type="button" onClick={refresh} disabled={refreshing} className="btn-secondary">
            {refreshing ? <Spinner className="h-4 w-4" /> : <RefreshCw className="h-4 w-4" />}
            {refreshing ? "Refreshing..." : "Refresh"}
          </button>
        }
      />

      {refreshError && <Alert tone="error">{refreshError}</Alert>}

      <div className={`card overflow-hidden border ${style.soft}`}>
        <div className="p-5 sm:p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <CategoryBadge category={latest.category} />
              <h2 className="mt-2 text-xl font-extrabold tracking-tight text-ink sm:text-2xl">
                {latest.headline}
              </h2>
              <p className="mt-2 max-w-3xl text-sm leading-relaxed text-ink/80">
                {latest.message}
              </p>
            </div>
            <span className="text-[11px] font-medium text-muted">
              {formatDate(latest.created_at, { withTime: true })}
            </span>
          </div>

          <div className="mt-5 grid gap-2.5 sm:grid-cols-3 lg:grid-cols-6">
            {metricCards.map((metric) => {
              const Icon = metric.icon;
              return (
                <div key={metric.label} className="rounded-xl bg-surface/75 px-3 py-2.5">
                  <Icon className="h-3.5 w-3.5 text-muted" />
                  <p className="mt-1 text-[10px] font-semibold uppercase tracking-wide text-muted">
                    {metric.label}
                  </p>
                  <p className="mt-0.5 text-sm font-extrabold text-ink">{metric.value}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <section className="card p-5">
            <SectionHeading
              title="What to do next"
              subtitle="Suggestions are chosen from your real weak topics and progress."
              icon={Sparkles}
            />
            <ol className="space-y-2.5">
              {(latest.suggestions || []).map((suggestion, index) => (
                <li key={index} className="flex gap-2.5 rounded-xl border border-line bg-surface-2/40 px-3 py-2.5">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-600 text-[10px] font-bold text-white">
                    {index + 1}
                  </span>
                  <span className="text-sm leading-relaxed text-ink/80">{suggestion}</span>
                </li>
              ))}
            </ol>
          </section>

          <section className="card p-5">
            <SectionHeading
              title="Your category scale"
              subtitle="The same five rules are used for every student."
              icon={Info}
            />
            <div className="space-y-2">
              {(categories || []).map((category) => {
                const categoryColour = categoryStyle(category);
                const active = category === latest.category;
                return (
                  <div
                    key={category}
                    className={`flex items-center gap-2.5 rounded-xl border px-3 py-2 ${
                      active
                        ? `${categoryColour.soft} border-line`
                        : "border-line bg-surface-2/30"
                    }`}
                  >
                    <span className={`h-2 w-2 rounded-full ${categoryColour.bar}`} />
                    <span className={`text-xs font-semibold ${active ? "text-ink" : "text-muted"}`}>
                      {category}
                    </span>
                    {active && (
                      <span className="ml-auto text-[10px] font-bold uppercase tracking-wide text-ink/70">
                        You are here
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
            <p className="mt-3 text-[11px] leading-relaxed text-muted">{explanation}</p>
          </section>

          <section className="card p-5">
            <SectionHeading title="Feedback history" subtitle="Only generated when your evidence changes" />
            <div className="space-y-2">
              {history.map((record) => {
                const recordStyle = categoryStyle(record.category);
                return (
                  <div
                    key={record.id}
                    className="flex flex-wrap items-center gap-2 rounded-xl border border-line px-3 py-2.5"
                  >
                    <span className={`h-2 w-2 shrink-0 rounded-full ${recordStyle.bar}`} />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs font-semibold text-ink">{record.headline}</p>
                      <p className="text-[10px] text-muted">
                        {formatDate(record.created_at, { withTime: true })} ·{" "}
                        {record.metrics?.attempts ?? 0} quizzes ·{" "}
                        {percent(record.metrics?.average_percentage)}
                      </p>
                    </div>
                    <CategoryBadge category={record.category} />
                  </div>
                );
              })}
            </div>
          </section>
        </div>

        <div className="space-y-6">
          <section className="card p-5">
            <SectionHeading title="Focus topics" subtitle="Lowest averages first" icon={Target} />
            {(latest.focus_topics || []).length === 0 ? (
              <p className="text-xs leading-relaxed text-muted">
                No weak topic right now. Try a harder quiz or start a new topic.
              </p>
            ) : (
              <div className="space-y-3">
                {latest.focus_topics.map((topic) => (
                  <div key={topic.slug}>
                    <div className="flex items-center justify-between gap-2 text-xs">
                      <span className="truncate font-semibold text-ink">{topic.title}</span>
                      <span className="font-semibold text-amber-600 dark:text-amber-300">
                        {percent(topic.percentage)}
                      </span>
                    </div>
                    <div className="mt-1">
                      <ProgressBar value={topic.percentage || 0} tone="bg-amber-500" />
                    </div>
                    <div className="mt-1.5 flex gap-2">
                      <Link to={`/topics/${topic.slug}`} className="text-[11px] font-semibold text-primary-600 dark:text-primary-300">
                        Lesson
                      </Link>
                      <Link
                        to={`/quiz/start?topic=${encodeURIComponent(topic.slug)}`}
                        className="text-[11px] font-semibold text-primary-600 dark:text-primary-300"
                      >
                        Quiz
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="card p-5">
            <SectionHeading title="Strengths" subtitle="Keep these sharp" icon={Award} />
            {(latest.strengths || []).length === 0 ? (
              <p className="text-xs leading-relaxed text-muted">
                Your strengths will appear once a topic average reaches 80%.
              </p>
            ) : (
              <div className="space-y-2">
                {latest.strengths.map((topic) => (
                  <div key={topic.slug} className="flex items-center justify-between gap-2 text-xs">
                    <span className="truncate font-medium text-ink">{topic.title}</span>
                    <span className="font-semibold text-emerald-600 dark:text-emerald-300">
                      {percent(topic.percentage)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="card p-5">
            <SectionHeading title="Subject averages" />
            <div className="space-y-2">
              {Object.entries(metrics.subject_averages || {}).map(([subject, average]) => (
                <div key={subject} className="flex items-center justify-between text-xs">
                  <span className="font-medium text-ink">{subject}</span>
                  <span className="font-semibold text-muted">{percent(average)}</span>
                </div>
              ))}
            </div>
            {metrics.trend && (
              <p className="mt-3 rounded-lg bg-surface-2/60 px-3 py-2 text-[11px] leading-relaxed text-muted">
                {TREND_TEXT[metrics.trend] || "Keep going."}
              </p>
            )}
          </section>

          <Link to="/assistant" className="card card-hover flex items-center gap-3 p-4">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent-50 text-accent-600 dark:bg-accent-500/15 dark:text-accent-300">
              <Sparkles className="h-4 w-4" />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block text-sm font-bold text-ink">Need help with a step?</span>
              <span className="block text-[11px] text-muted">Ask the learning assistant</span>
            </span>
            <ArrowRight className="h-4 w-4 text-muted" />
          </Link>
        </div>
      </div>
    </div>
  );
}
