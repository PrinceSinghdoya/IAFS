import { Link } from "react-router-dom";
import {
  ArrowRight,
  BookOpen,
  GraduationCap,
  School,
  TrendingUp,
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
  EmptyState,
  PageHeader,
  ProgressBar,
  SectionHeading,
  StatCard,
} from "../components/ui";
import { classLevelLabel, subjectStyle } from "../lib/constants";
import { percent } from "../lib/format";
import { useApi, useDocumentTitle } from "../lib/useApi";

const CHART_TOOLTIP = {
  borderRadius: 12,
  border: "1px solid rgb(var(--line))",
  background: "rgb(var(--surface))",
  color: "rgb(var(--ink))",
  fontSize: 12,
};

export default function TeacherClasses() {
  const { data, loading, error } = useApi("/teacher/classes");
  useDocumentTitle("Classes");

  if (loading && !data) return <SectionLoader label="Loading class performance..." />;
  if (error) return <Alert tone="error">{error}</Alert>;
  if (!data) return null;

  const { classes = [], subjects = [] } = data;
  const withStudents = classes.filter((row) => row.students > 0);
  const totalStudents = classes.reduce((sum, row) => sum + row.students, 0);
  const totalAttempts = classes.reduce((sum, row) => sum + row.attempts, 0);
  const scored = classes.filter((row) => row.average !== null);
  const schoolAverage = scored.length
    ? Math.round((scored.reduce((sum, row) => sum + row.average, 0) / scored.length) * 10) / 10
    : null;

  const chartData = classes.map((row) => ({
    name: `C${row.class_level}`,
    average: row.average ?? 0,
  }));

  return (
    <div className="animate-fade-in space-y-6">
      <PageHeader
        eyebrow="Class overview"
        title="Classes and subjects"
        subtitle="Class sizes, activity and averages calculated from saved student results. Use a class to open its student list."
        actions={
          <Link to="/teacher/students" className="btn-primary">
            <Users className="h-4 w-4" /> All students
          </Link>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Students enrolled"
          value={totalStudents}
          icon={Users}
          tone="blue"
          helper={`${withStudents.length} of ${classes.length} classes have students`}
        />
        <StatCard
          label="Quizzes completed"
          value={totalAttempts}
          icon={BookOpen}
          tone="violet"
          helper="Across every class"
        />
        <StatCard
          label="Average of class averages"
          value={percent(schoolAverage)}
          icon={TrendingUp}
          tone="emerald"
          helper="Only classes with completed quizzes"
        />
        <StatCard
          label="Curriculum topics"
          value={subjects.reduce((sum, subject) => sum + (subject.topics || 0), 0)}
          icon={GraduationCap}
          tone="sun"
          helper="English and Mathematics, Primary and Secondary"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <section className="card p-5 lg:col-span-2">
          <SectionHeading
            title="Average score by class"
            subtitle="A class without completed quizzes stays at zero on this chart."
            icon={School}
          />
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--line))" vertical={false} />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: "rgb(var(--muted))" }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fontSize: 10, fill: "rgb(var(--muted))" }}
                  tickLine={false}
                  axisLine={false}
                  width={40}
                />
                <Tooltip
                  formatter={(value) => [`${value}%`, "Average"]}
                  contentStyle={CHART_TOOLTIP}
                />
                <Bar dataKey="average" radius={[6, 6, 0, 0]} fill="#6366f1" maxBarSize={42} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="card p-5">
          <SectionHeading title="Subject performance" subtitle="Whole school" />
          {subjects.length === 0 ? (
            <EmptyState icon={BookOpen} title="No subjects found" />
          ) : (
            <div className="space-y-4">
              {subjects.map((subject) => {
                const style = subjectStyle(subject.subject);
                const Icon = style.icon;
                return (
                  <div key={subject.subject}>
                    <div className="flex items-center gap-2">
                      <span
                        className={`flex h-8 w-8 items-center justify-center rounded-lg ${style.soft}`}
                      >
                        <Icon className="h-4 w-4" />
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="text-xs font-bold text-ink">{subject.subject}</p>
                        <p className="text-[10px] text-muted">
                          {subject.attempts} quizzes · {subject.students} students
                        </p>
                      </div>
                      <span className="text-sm font-extrabold text-ink">
                        {percent(subject.average)}
                      </span>
                    </div>
                    <div className="mt-2">
                      <ProgressBar value={subject.average || 0} tone={style.bar} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </div>

      <section>
        <SectionHeading
          title="Every class"
          subtitle="Class 1-5 follow the Primary curriculum, Class 6-10 the Secondary curriculum."
          icon={GraduationCap}
        />
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-line">
              <thead className="bg-surface-2/60">
                <tr>
                  <th className="table-th">Class</th>
                  <th className="table-th">Level</th>
                  <th className="table-th">Students</th>
                  <th className="table-th">Active</th>
                  <th className="table-th">Quizzes</th>
                  <th className="table-th">Average</th>
                  <th className="table-th">Best</th>
                  <th className="table-th" />
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {classes.map((row) => (
                  <tr key={row.class_level} className="transition hover:bg-surface-2/40">
                    <td className="table-td font-semibold text-ink">
                      {classLevelLabel(row.class_level)}
                    </td>
                    <td className="table-td text-muted">{row.level}</td>
                    <td className="table-td">{row.students}</td>
                    <td className="table-td text-muted">{row.active_students}</td>
                    <td className="table-td text-muted">{row.attempts}</td>
                    <td className="table-td font-semibold text-ink">{percent(row.average)}</td>
                    <td className="table-td text-muted">{percent(row.best)}</td>
                    <td className="table-td text-right">
                      <Link
                        to={`/teacher/students?class_level=${row.class_level}`}
                        className="link inline-flex items-center gap-1 text-xs"
                      >
                        Students <ArrowRight className="h-3 w-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2">
        {subjects.map((subject) => {
          const style = subjectStyle(subject.subject);
          const Icon = style.icon;
          return (
            <div key={subject.subject} className={`card border p-5 ${style.border}`}>
              <div className="flex items-center gap-3">
                <span className={`sticker ${style.soft}`}>
                  <Icon className="h-5 w-5" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-bold text-ink">
                    {style.emoji} {subject.subject}
                  </p>
                  <p className="truncate text-[11px] text-muted">
                    {subject.topics} topics · {subject.students} students
                  </p>
                </div>
                <span className="text-sm font-extrabold text-ink">
                  {percent(subject.average)}
                </span>
              </div>

              <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-lg bg-surface-2 px-2 py-1.5">
                  <p className="text-[9px] font-semibold uppercase tracking-wide text-muted">
                    Quizzes
                  </p>
                  <p className="text-sm font-extrabold text-ink">{subject.attempts}</p>
                </div>
                <div className="rounded-lg bg-surface-2 px-2 py-1.5">
                  <p className="text-[9px] font-semibold uppercase tracking-wide text-muted">
                    Average
                  </p>
                  <p className="text-sm font-extrabold text-ink">{percent(subject.average)}</p>
                </div>
                <div className="rounded-lg bg-surface-2 px-2 py-1.5">
                  <p className="text-[9px] font-semibold uppercase tracking-wide text-muted">
                    Best
                  </p>
                  <p className="text-sm font-extrabold text-ink">{percent(subject.best)}</p>
                </div>
              </div>

              <div className="mt-3">
                <ProgressBar value={subject.average || 0} tone={style.bar} />
              </div>
            </div>
          );
        })}
      </section>
    </div>
  );
}
