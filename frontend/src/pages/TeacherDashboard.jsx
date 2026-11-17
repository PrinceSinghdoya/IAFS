import { Link } from "react-router-dom";
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  BookOpen,
  GraduationCap,
  TrendingUp,
  Users,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import Alert from "../components/Alert";
import { SectionLoader } from "../components/Loading";
import {
  Avatar,
  CategoryBadge,
  EmptyState,
  PageHeader,
  ProgressBar,
  SectionHeading,
  StatCard,
  StatusBadge,
} from "../components/ui";
import { classLevelLabel, subjectStyle } from "../lib/constants";
import { formatDate, percent, relativeTime } from "../lib/format";
import { useApi, useDocumentTitle } from "../lib/useApi";

const PIE_COLOURS = ["#f43f5e", "#f59e0b", "#3b82f6", "#10b981"];

function StudentRow({ student }) {
  return (
    <Link
      to={`/teacher/students/${student.id}`}
      className="flex items-center gap-2.5 rounded-xl border border-line px-3 py-2.5 transition hover:bg-surface-2/60"
    >
      <Avatar name={student.name} size="sm" />
      <div className="min-w-0 flex-1">
        <p className="truncate text-xs font-bold text-ink">{student.name}</p>
        <p className="text-[10px] text-muted">
          {classLevelLabel(student.class_level)} · {student.attempts} quiz
          {student.attempts === 1 ? "" : "zes"}
        </p>
      </div>
      <span className="text-xs font-extrabold text-ink">{percent(student.average)}</span>
    </Link>
  );
}

export default function TeacherDashboard() {
  const { data, loading, error } = useApi("/teacher/dashboard");
  useDocumentTitle("Teacher overview");

  if (loading && !data) return <SectionLoader label="Loading class analytics..." />;
  if (error) return <Alert tone="error">{error}</Alert>;
  if (!data) return null;

  const { summary, classes, subjects, weak_topics, score_distribution, recent_activity, top_students, students_needing_support } = data;
  const classChart = classes.map((row) => ({
    name: `C${row.class_level}`,
    average: row.average ?? 0,
    attempts: row.attempts,
  }));
  const pieData = score_distribution.filter((bucket) => bucket.count > 0);

  return (
    <div className="animate-fade-in space-y-6">
      <PageHeader
        eyebrow="Teaching overview"
        title="How your school is learning"
        subtitle="Every number is calculated from saved quiz results, topic progress and class activity. Nothing is hardcoded."
        actions={
          <>
            <Link to="/teacher/students" className="btn-primary">
              <Users className="h-4 w-4" /> Students
            </Link>
            <Link to="/teacher/classes" className="btn-secondary">
              <GraduationCap className="h-4 w-4" /> Classes
            </Link>
          </>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Students"
          value={summary.students}
          icon={Users}
          tone="blue"
          helper={`${summary.students_active} active · ${summary.classes_with_students} classes`}
        />
        <StatCard
          label="Quizzes completed"
          value={summary.attempts}
          icon={BarChart3}
          tone="violet"
          helper="Across the whole school"
        />
        <StatCard
          label="School average"
          value={percent(summary.average)}
          icon={TrendingUp}
          tone="emerald"
          helper="Mean percentage of all results"
        />
        <StatCard
          label="Weak topics"
          value={summary.weak_topics}
          icon={AlertTriangle}
          tone="rose"
          helper="Topics averaging below 60%"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <section className="card p-5 lg:col-span-2">
          <SectionHeading
            title="Class averages"
            subtitle="Only classes with completed quizzes show a bar."
            icon={BarChart3}
          />
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={classChart} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--line))" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "rgb(var(--muted))" }} tickLine={false} axisLine={false} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "rgb(var(--muted))" }} tickLine={false} axisLine={false} width={40} />
                <Tooltip
                  formatter={(value) => [`${value}%`, "Average"]}
                  contentStyle={{
                    borderRadius: 12,
                    border: "1px solid rgb(var(--line))",
                    background: "rgb(var(--surface))",
                    color: "rgb(var(--ink))",
                    fontSize: 12,
                  }}
                />
                <Bar dataKey="average" radius={[6, 6, 0, 0]} fill="#6366f1" maxBarSize={42} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="card p-5">
          <SectionHeading title="Score distribution" subtitle="All completed quizzes" />
          {pieData.length === 0 ? (
            <EmptyState icon={BarChart3} title="No results yet" description="Distribution appears after the first quiz." />
          ) : (
            <>
              <div className="h-44 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} dataKey="count" nameKey="label" innerRadius={44} outerRadius={70} paddingAngle={2}>
                      {pieData.map((entry, index) => (
                        <Cell key={entry.label} fill={PIE_COLOURS[index % PIE_COLOURS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value, name) => [`${value} quizzes`, name]}
                      contentStyle={{
                        borderRadius: 12,
                        border: "1px solid rgb(var(--line))",
                        background: "rgb(var(--surface))",
                        color: "rgb(var(--ink))",
                        fontSize: 12,
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-2 space-y-1.5">
                {score_distribution.map((bucket, index) => (
                  <div key={bucket.label} className="flex items-center gap-2 text-[11px]">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{ backgroundColor: PIE_COLOURS[index % PIE_COLOURS.length] }}
                    />
                    <span className="flex-1 text-muted">{bucket.label}</span>
                    <span className="font-semibold text-ink">{bucket.count}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </section>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="card p-5">
          <SectionHeading title="Subject performance" icon={BookOpen} />
          <div className="space-y-4">
            {subjects.map((subject) => {
              const style = subjectStyle(subject.subject);
              const Icon = style.icon;
              return (
                <div key={subject.subject}>
                  <div className="flex items-center gap-2">
                    <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${style.soft}`}>
                      <Icon className="h-4 w-4" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-bold text-ink">{subject.subject}</p>
                      <p className="text-[10px] text-muted">
                        {subject.attempts} quizzes · {subject.students} students · {subject.topics} topics
                      </p>
                    </div>
                    <span className="text-sm font-extrabold text-ink">{percent(subject.average)}</span>
                  </div>
                  <div className="mt-2">
                    <ProgressBar value={subject.average || 0} tone={style.bar} />
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section className="card p-5">
          <SectionHeading
            title="Weak topics"
            subtitle="Lowest class averages across the school."
            action={
              <Link to="/teacher/classes" className="link text-xs">
                All classes
              </Link>
            }
          />
          {weak_topics.length === 0 ? (
            <EmptyState icon={AlertTriangle} title="No weak topics" description="Every attempted topic is averaging 60% or more." />
          ) : (
            <div className="space-y-2">
              {weak_topics.map((topic) => (
                <div key={topic.slug} className="flex items-center gap-2 rounded-xl border border-line px-3 py-2.5">
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-xs font-bold text-ink">{topic.title}</p>
                    <p className="text-[10px] text-muted">
                      {topic.subject} · {topic.level} · {topic.students} students
                    </p>
                  </div>
                  <div className="w-20">
                    <ProgressBar value={topic.average || 0} tone="bg-rose-500" />
                  </div>
                  <span className="w-10 text-right text-xs font-bold text-rose-600 dark:text-rose-300">
                    {percent(topic.average)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <section className="card p-5">
          <SectionHeading title="Top students" subtitle="Highest averages" />
          <div className="space-y-2">
            {top_students.length === 0 ? (
              <p className="text-xs text-muted">No student has completed a quiz yet.</p>
            ) : (
              top_students.map((student) => <StudentRow key={student.id} student={student} />)
            )}
          </div>
        </section>

        <section className="card p-5">
          <SectionHeading title="Needs support" subtitle="Lowest averages" />
          <div className="space-y-2">
            {students_needing_support.length === 0 ? (
              <p className="text-xs text-muted">No students need extra support right now.</p>
            ) : (
              students_needing_support.map((student) => <StudentRow key={student.id} student={student} />)
            )}
          </div>
        </section>

        <section className="card p-5">
          <SectionHeading title="Recent activity" subtitle="Quizzes, chat and focus checks" />
          <div className="max-h-72 space-y-2 overflow-y-auto pr-1">
            {recent_activity.map((item, index) => (
              <div key={`${item.type}-${index}`} className="rounded-xl border border-line px-3 py-2">
                <p className="text-[11px] font-semibold text-ink">{item.title}</p>
                <p className="text-[10px] text-muted">{item.detail}</p>
                <p className="mt-0.5 text-[9px] text-muted">
                  {classLevelLabel(item.class_level)} · {relativeTime(item.created_at)}
                </p>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="card p-5">
        <SectionHeading title="Class overview" subtitle="Students, activity and averages" icon={GraduationCap} />
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
                <tr key={row.class_level} className="hover:bg-surface-2/40">
                  <td className="table-td font-semibold">{classLevelLabel(row.class_level)}</td>
                  <td className="table-td text-muted">{row.level}</td>
                  <td className="table-td">{row.students}</td>
                  <td className="table-td">{row.active_students}</td>
                  <td className="table-td">{row.attempts}</td>
                  <td className="table-td font-semibold">{percent(row.average)}</td>
                  <td className="table-td">{percent(row.best)}</td>
                  <td className="table-td text-right">
                    <Link
                      to={`/teacher/students?class_level=${row.class_level}`}
                      className="link inline-flex items-center gap-1 text-xs"
                    >
                      View <ArrowRight className="h-3 w-3" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
