import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ArrowRight, Search, Users } from "lucide-react";

import Alert from "../components/Alert";
import { SectionLoader } from "../components/Loading";
import {
  Avatar,
  CategoryBadge,
  EmptyState,
  PageHeader,
  StatusBadge,
} from "../components/ui";
import { CLASS_LEVELS, TREND_LABELS, classLevelLabel } from "../lib/constants";
import { formatDate, percent } from "../lib/format";
import { useApi, useDocumentTitle } from "../lib/useApi";

export default function TeacherStudents() {
  const [searchParams, setSearchParams] = useSearchParams();
  const classLevel = searchParams.get("class_level") || "";
  const subject = searchParams.get("subject") || "";
  const [search, setSearch] = useState(searchParams.get("search") || "");
  const [appliedSearch, setAppliedSearch] = useState(searchParams.get("search") || "");

  const query = new URLSearchParams();
  if (classLevel) query.set("class_level", classLevel);
  if (subject) query.set("subject", subject);
  if (appliedSearch) query.set("search", appliedSearch);
  const { data, loading, error } = useApi(`/teacher/students${query.toString() ? `?${query}` : ""}`);
  useDocumentTitle("Students");

  function updateFilter(key, value) {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    setSearchParams(next);
  }

  function applySearch(event) {
    event.preventDefault();
    setAppliedSearch(search.trim());
    updateFilter("search", search.trim());
  }

  const students = data?.students || [];

  return (
    <div className="animate-fade-in space-y-6">
      <PageHeader
        eyebrow="Student directory"
        title="Students"
        subtitle="Real averages, topic coverage and support flags for every student. Open a student for a full private report."
        actions={
          <span className="chip bg-surface-2 text-muted">
            <Users className="h-3.5 w-3.5" />
            {data?.total ?? 0} students
          </span>
        }
      />

      {error && <Alert tone="error">{error}</Alert>}

      <div className="card flex flex-col gap-3 p-4 lg:flex-row lg:items-center">
        <select
          value={classLevel}
          onChange={(event) => updateFilter("class_level", event.target.value)}
          className="input lg:w-40"
          aria-label="Filter by class"
        >
          <option value="">All classes</option>
          {CLASS_LEVELS.map((level) => (
            <option key={level} value={level}>
              Class {level}
            </option>
          ))}
        </select>

        <select
          value={subject}
          onChange={(event) => updateFilter("subject", event.target.value)}
          className="input lg:w-44"
          aria-label="Filter by subject"
        >
          <option value="">All subjects</option>
          <option value="English">English</option>
          <option value="Mathematics">Mathematics</option>
        </select>

        <form onSubmit={applySearch} className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by name or email..."
            className="input pl-9"
          />
        </form>

        <button type="submit" onClick={applySearch} className="btn-secondary">
          Apply
        </button>
      </div>

      {loading && !data ? (
        <SectionLoader label="Loading students..." />
      ) : students.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No students match these filters"
          description="Try another class, subject or search term."
        />
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-line">
              <thead className="bg-surface-2/60">
                <tr>
                  <th className="table-th">Student</th>
                  <th className="table-th">Class</th>
                  <th className="table-th">Quizzes</th>
                  <th className="table-th">Average</th>
                  <th className="table-th">Best</th>
                  <th className="table-th">Category</th>
                  <th className="table-th">Focus topic</th>
                  <th className="table-th">Last activity</th>
                  <th className="table-th" />
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {students.map((student) => {
                  const trend = TREND_LABELS[student.trend] || TREND_LABELS.steady;
                  return (
                    <tr key={student.id} className="transition hover:bg-surface-2/40">
                      <td className="table-td">
                        <div className="flex items-center gap-2.5">
                          <Avatar name={student.name} size="sm" />
                          <div className="min-w-0">
                            <p className="truncate font-semibold text-ink">{student.name}</p>
                            <p className="truncate text-[10px] text-muted">{student.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="table-td">
                        <span className="text-xs text-muted">
                          {classLevelLabel(student.class_level)}
                          {student.section ? `-${student.section}` : ""}
                        </span>
                      </td>
                      <td className="table-td text-muted">{student.attempts}</td>
                      <td className="table-td">
                        <span className="font-semibold text-ink">{percent(student.average)}</span>
                        <span className={`ml-1.5 text-[10px] font-semibold ${trend.tone}`}>
                          {trend.label}
                        </span>
                      </td>
                      <td className="table-td">{percent(student.best)}</td>
                      <td className="table-td">
                        <CategoryBadge category={student.category} />
                      </td>
                      <td className="table-td">
                        {student.focus_topic ? (
                          <div>
                            <p className="max-w-[12rem] truncate text-xs text-ink">{student.focus_topic}</p>
                            <p className="text-[10px] text-muted">{percent(student.focus_percentage)}</p>
                          </div>
                        ) : (
                          <StatusBadge status="On track" />
                        )}
                      </td>
                      <td className="table-td text-[11px] text-muted">
                        {student.last_activity ? formatDate(student.last_activity) : "No activity"}
                      </td>
                      <td className="table-td text-right">
                        <Link
                          to={`/teacher/students/${student.id}`}
                          className="link inline-flex items-center gap-1 text-xs"
                        >
                          Report <ArrowRight className="h-3 w-3" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
