import { Link } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  GraduationCap,
  Layers,
  ShieldCheck,
  TrendingUp,
  UserCog,
  Users,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
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
} from "../components/ui";
import { ROLE_LABELS, classLevelLabel, subjectStyle } from "../lib/constants";
import { formatDate, percent, relativeTime } from "../lib/format";
import { useApi, useDocumentTitle } from "../lib/useApi";

export default function AdminDashboard() {
  const { data, loading, error } = useApi("/admin/dashboard");
  useDocumentTitle("Administrator overview");

  if (loading && !data) return <SectionLoader label="Loading school overview..." />;
  if (error) return <Alert tone="error">{error}</Alert>;
  if (!data) return null;

  const { users, content, learning, class_counts, recent_users, recent_results, subjects } = data;
  const chartData = class_counts.map((row) => ({
    name: `C${row.class_level}`,
    students: row.students,
  }));

  return (
    <div className="animate-fade-in space-y-6">
      <PageHeader
        eyebrow="Administration"
        title="School overview"
        subtitle="Accounts, curriculum and learning activity for the whole school. Every figure is read from the database."
        actions={
          <>
            <Link to="/admin/users" className="btn-primary">
              <UserCog className="h-4 w-4" /> Manage users
            </Link>
            <Link to="/admin/classes-subjects" className="btn-secondary">
              <Layers className="h-4 w-4" /> Curriculum
            </Link>
          </>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total accounts"
          value={users.total}
          icon={Users}
          tone="blue"
          helper={`${users.students} students · ${users.teachers} teachers · ${users.admins} admins`}
        />
        <StatCard
          label="Active accounts"
          value={users.active}
          icon={ShieldCheck}
          tone="emerald"
          helper={`${users.total - users.active} deactivated`}
        />
        <StatCard
          label="Curriculum topics"
          value={content.topics}
          icon={BookOpen}
          tone="violet"
          helper={`${content.primary_topics} Primary · ${content.secondary_topics} Secondary`}
        />
        <StatCard
          label="School average"
          value={percent(learning.average)}
          icon={TrendingUp}
          tone="sun"
          helper={`${learning.attempts} quizzes · ${learning.attempts_this_week} this week`}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <section className="card p-5 lg:col-span-2">
          <SectionHeading
            title="Students per class"
            subtitle="Every class from 1 to 10, counted from active student accounts."
            icon={GraduationCap}
          />
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: -24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--line))" vertical={false} />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: "rgb(var(--muted))" }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  allowDecimals={false}
                  tick={{ fontSize: 10, fill: "rgb(var(--muted))" }}
                  tickLine={false}
                  axisLine={false}
                  width={32}
                />
                <Tooltip
                  formatter={(value) => [value, "Students"]}
                  contentStyle={{
                    borderRadius: 12,
                    border: "1px solid rgb(var(--line))",
                    background: "rgb(var(--surface))",
                    color: "rgb(var(--ink))",
                    fontSize: 12,
                  }}
                />
                <Bar dataKey="students" radius={[6, 6, 0, 0]} fill="#8b5cf6" maxBarSize={42} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="card p-5">
          <SectionHeading title="Learning activity" icon={BarChart3} />
          <div className="space-y-3">
            <div className="rounded-xl bg-surface-2/60 px-3 py-2.5">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">
                Quizzes completed
              </p>
              <p className="mt-0.5 text-xl font-extrabold text-ink">{learning.attempts}</p>
            </div>
            <div className="rounded-xl bg-surface-2/60 px-3 py-2.5">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">
                Active learners
              </p>
              <p className="mt-0.5 text-xl font-extrabold text-ink">{learning.active_students}</p>
            </div>
            <div className="rounded-xl bg-surface-2/60 px-3 py-2.5">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">
                This week
              </p>
              <p className="mt-0.5 text-xl font-extrabold text-ink">
                {learning.attempts_this_week}
              </p>
            </div>
          </div>
          <Link to="/teacher" className="btn-secondary mt-4 w-full">
            <GraduationCap className="h-4 w-4" /> Teacher overview
          </Link>
        </section>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {subjects.map((subject) => {
          const style = subjectStyle(subject.name);
          const Icon = style.icon;
          return (
            <div key={subject.name} className={`card border p-5 ${style.border}`}>
              <div className="flex items-center gap-3">
                <span className={`sticker ${style.soft}`}>
                  <Icon className="h-5 w-5" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-bold text-ink">
                    {subject.emoji} {subject.name}
                  </p>
                  <p className="truncate text-[11px] text-muted">{subject.tagline}</p>
                </div>
                <span className="text-sm font-extrabold text-ink">{subject.topics}</span>
              </div>
              <div className="mt-3">
                <ProgressBar
                  value={(subject.topics / (content.topics || 1)) * 100}
                  tone={style.bar}
                />
                <p className="mt-1.5 text-[11px] text-muted">
                  {subject.topics} of {content.topics} topics
                </p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="card p-5">
          <SectionHeading
            title="New accounts this week"
            subtitle="Most recent first"
            action={
              <Link to="/admin/users" className="link text-xs">
                All users
              </Link>
            }
          />
          {recent_users.length === 0 ? (
            <EmptyState
              icon={Users}
              title="No new accounts"
              description="Accounts created in the last seven days appear here."
            />
          ) : (
            <div className="space-y-2">
              {recent_users.map((user) => (
                <div
                  key={user.id}
                  className="flex items-center gap-2.5 rounded-xl border border-line px-3 py-2.5"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-xs font-bold text-ink">{user.name}</p>
                    <p className="truncate text-[10px] text-muted">{user.email}</p>
                  </div>
                  <span className="chip bg-surface-2 text-muted">
                    {ROLE_LABELS[user.role] || user.role}
                  </span>
                  <span className="hidden text-[10px] text-muted sm:block">
                    {relativeTime(user.created_at)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="card p-5">
          <SectionHeading title="Recent quiz results" subtitle="Latest across the school" />
          {recent_results.length === 0 ? (
            <EmptyState
              icon={BarChart3}
              title="No results yet"
              description="Completed quizzes will appear here."
            />
          ) : (
            <div className="max-h-80 space-y-2 overflow-y-auto pr-1">
              {recent_results.map((result) => {
                const content = (
                  <>
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-surface-2 text-xs font-bold text-ink">
                      {Math.round(result.percentage ?? 0)}%
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs font-semibold text-ink">{result.topic}</p>
                      <p className="text-[10px] text-muted">
                        {result.student_name} · {classLevelLabel(result.class_level)} ·{" "}
                        {formatDate(result.created_at)}
                      </p>
                    </div>
                    <CategoryBadge category={result.category} />
                  </>
                );
                const className =
                  "flex items-center gap-2.5 rounded-xl border border-line px-3 py-2.5 transition hover:bg-surface-2/60";
                return result.student_id ? (
                  <Link
                    key={result.id}
                    to={`/teacher/students/${result.student_id}`}
                    className={className}
                  >
                    {content}
                  </Link>
                ) : (
                  <div key={result.id} className={className}>
                    {content}
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </div>

      <div className="flex justify-end">
        <Link to="/admin/classes-subjects" className="btn-secondary">
          Browse the full curriculum <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
