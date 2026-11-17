import { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Award,
  BarChart3,
  BookOpen,
  Flame,
  Target,
  TrendingUp,
} from "lucide-react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import Alert from "../components/Alert";
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
import { classLevelLabel, subjectStyle } from "../lib/constants";
import { formatDate, percent } from "../lib/format";
import { useApi, useDocumentTitle } from "../lib/useApi";

function TrendChart({ results }) {
  const data = useMemo(
    () =>
      [...results]
        .reverse()
        .slice(-12)
        .map((result, index) => ({
          name: `#${index + 1}`,
          score: result.percentage ?? 0,
          topic: result.topic,
        })),
    [results]
  );

  if (data.length < 2) {
    return (
      <div className="flex h-56 items-center justify-center rounded-xl border border-dashed border-line bg-surface-2/40 px-4 text-center">
        <p className="text-xs leading-relaxed text-muted">
          Complete at least two quizzes to see your score trend here.
        </p>
      </div>
    );
  }

  return (
    <div className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--line))" vertical={false} />
          <XAxis dataKey="name" tick={{ fontSize: 10, fill: "rgb(var(--muted))" }} tickLine={false} axisLine={false} />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 10, fill: "rgb(var(--muted))" }}
            tickLine={false}
            axisLine={false}
            width={40}
          />
          <Tooltip
            formatter={(value) => [`${value}%`, "Score"]}
            labelFormatter={(label, payload) => payload?.[0]?.payload?.topic || label}
            contentStyle={{
              borderRadius: 12,
              border: "1px solid rgb(var(--line))",
              background: "rgb(var(--surface))",
              color: "rgb(var(--ink))",
              fontSize: 12,
            }}
          />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#6366f1"
            strokeWidth={2.5}
            dot={{ r: 3, fill: "#6366f1" }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function Progress() {
  const { data, loading, error } = useApi("/student/progress");
  useDocumentTitle("My progress");

  if (loading && !data) return <SectionLoader label="Calculating your progress..." />;
  if (error) return <Alert tone="error">{error}</Alert>;
  if (!data) return null;

  const { summary, subjects, topics, strengths, focus_topics, results } = data;

  return (
    <div className="animate-fade-in space-y-6">
      <PageHeader
        eyebrow={`${classLevelLabel(data.class_level)} · English and Mathematics`}
        title="My progress"
        subtitle="Every number here comes from your own completed quizzes. Nothing is estimated or randomised."
        actions={
          <Link to="/quiz/start" className="btn-primary">
            <Target className="h-4 w-4" /> Take a quiz
          </Link>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Average" value={percent(summary.average)} icon={TrendingUp} tone="blue" />
        <StatCard label="Best" value={percent(summary.best)} icon={Award} tone="emerald" />
        <StatCard
          label="Quizzes completed"
          value={summary.attempts}
          icon={BarChart3}
          tone="violet"
          helper={`${summary.topics_started}/${summary.topics_total} topics started`}
        />
        <StatCard
          label="Streak"
          value={summary.streak_days ?? 0}
          suffix=" days"
          icon={Flame}
          tone="sun"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <section className="card p-5 lg:col-span-2">
          <SectionHeading
            title="Score trend"
            subtitle="Your last 12 quiz results, oldest to newest."
            icon={BarChart3}
          />
          <TrendChart results={results} />
        </section>

        <section className="card p-5">
          <SectionHeading title="Subject averages" subtitle="Across attempted topics" />
          <div className="space-y-4">
            {subjects.map((subject) => {
              const style = subjectStyle(subject.subject);
              const Icon = style.icon;
              const coverage = subject.topics_total
                ? (subject.topics_started / subject.topics_total) * 100
                : 0;
              return (
                <div key={subject.subject}>
                  <div className="flex items-center gap-2">
                    <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${style.soft}`}>
                      <Icon className="h-4 w-4" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-bold text-ink">{subject.subject}</p>
                      <p className="text-[10px] text-muted">
                        {subject.topics_started}/{subject.topics_total} topics · {subject.topics_strong} strong
                      </p>
                    </div>
                    <span className="text-sm font-extrabold text-ink">
                      {percent(subject.average)}
                    </span>
                  </div>
                  <div className="mt-2">
                    <ProgressBar value={coverage} tone={style.bar} />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-5 border-t border-line pt-4">
            <p className="text-[10px] font-bold uppercase tracking-wide text-muted">
              Needs a little practice
            </p>
            {focus_topics.length === 0 ? (
              <p className="mt-1.5 text-xs text-muted">
                Nothing flagged right now. Keep practising to stay sharp.
              </p>
            ) : (
              <div className="mt-2 space-y-1.5">
                {focus_topics.map((topic) => (
                  <Link
                    key={topic.slug}
                    to={`/topics/${topic.slug}`}
                    className="flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-xs transition hover:bg-surface-2"
                  >
                    <span className="truncate font-medium text-ink">{topic.title}</span>
                    <span className="shrink-0 font-semibold text-amber-600 dark:text-amber-300">
                      {percent(topic.average)}
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>

      <section>
        <SectionHeading
          title="Topic progress"
          subtitle="A best score of 80% or more marks a topic as strong."
          icon={BookOpen}
        />
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-line">
              <thead className="bg-surface-2/60">
                <tr>
                  <th className="table-th">Topic</th>
                  <th className="table-th">Subject</th>
                  <th className="table-th">Attempts</th>
                  <th className="table-th">Best</th>
                  <th className="table-th">Average</th>
                  <th className="table-th">Status</th>
                  <th className="table-th" />
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {topics.map((topic) => (
                  <tr key={topic.slug} className="transition hover:bg-surface-2/40">
                    <td className="table-td">
                      <span className="font-semibold text-ink">
                        {topic.emoji} {topic.title}
                      </span>
                    </td>
                    <td className="table-td text-muted">{topic.subject}</td>
                    <td className="table-td text-muted">{topic.attempts}</td>
                    <td className="table-td font-semibold">{percent(topic.best)}</td>
                    <td className="table-td">{percent(topic.average)}</td>
                    <td className="table-td">
                      <StatusBadge status={topic.status} />
                    </td>
                    <td className="table-td text-right">
                      <Link
                        to={`/topics/${topic.slug}`}
                        className="link inline-flex items-center gap-1 text-xs"
                      >
                        Open <ArrowRight className="h-3 w-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="card p-5">
          <SectionHeading title="Strengths" subtitle="Topics where you are doing well" icon={Award} />
          {strengths.length === 0 ? (
            <EmptyState
              icon={Award}
              title="No strengths yet"
              description="Complete a quiz and topics with a high average will appear here."
            />
          ) : (
            <div className="space-y-2">
              {strengths.map((topic) => (
                <Link
                  key={topic.slug}
                  to={`/topics/${topic.slug}`}
                  className="flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50/50 px-3 py-2.5 transition hover:bg-emerald-50 dark:border-emerald-400/20 dark:bg-emerald-500/10 dark:hover:bg-emerald-500/15"
                >
                  <span className="text-lg">{topic.emoji}</span>
                  <span className="min-w-0 flex-1 truncate text-sm font-semibold text-ink">
                    {topic.title}
                  </span>
                  <span className="text-xs font-bold text-emerald-600 dark:text-emerald-300">
                    {percent(topic.average)}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="card p-5">
          <SectionHeading title="Recent results" subtitle="Open any result for a full review" />
          {results.length === 0 ? (
            <EmptyState
              icon={Target}
              title="No quiz results yet"
              description="Your results will appear here as soon as you finish a quiz."
              action={
                <Link to="/quiz/start" className="btn-primary">
                  Start a quiz
                </Link>
              }
            />
          ) : (
            <div className="max-h-80 space-y-1.5 overflow-y-auto pr-1">
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
                      {result.subject} · {formatDate(result.created_at)}
                    </p>
                  </div>
                  <CategoryBadge category={result.category} />
                </Link>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
