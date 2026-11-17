import { useMemo, useState } from "react";
import { BookOpen, GraduationCap, Layers, Search, Users } from "lucide-react";

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
import { useApi, useDocumentTitle } from "../lib/useApi";

const LEVEL_FILTERS = ["All", "Primary", "Secondary"];

export default function AdminClassesSubjects() {
  const { data, loading, error } = useApi("/admin/classes-subjects");
  const [levelFilter, setLevelFilter] = useState("All");
  const [search, setSearch] = useState("");
  useDocumentTitle("Classes & subjects");

  const subjects = data?.subjects || [];
  const classes = data?.classes || [];

  const visibleSubjects = useMemo(() => {
    const text = search.trim().toLowerCase();
    return subjects
      .map((subject) => ({
        ...subject,
        topics: (subject.topics || []).filter((topic) => {
          if (levelFilter !== "All" && topic.level !== levelFilter) return false;
          if (!text) return true;
          return (
            topic.title.toLowerCase().includes(text) ||
            topic.slug.toLowerCase().includes(text)
          );
        }),
      }))
      .filter((subject) => subject.topics.length > 0);
  }, [subjects, levelFilter, search]);

  if (loading && !data) return <SectionLoader label="Loading the curriculum..." />;
  if (error) return <Alert tone="error">{error}</Alert>;
  if (!data) return null;

  const totalStudents = classes.reduce((sum, row) => sum + row.students, 0);
  const shownTopics = visibleSubjects.reduce((sum, subject) => sum + subject.topics.length, 0);

  return (
    <div className="animate-fade-in space-y-6">
      <PageHeader
        eyebrow="Curriculum"
        title="Classes and subjects"
        subtitle="The full English and Mathematics catalogue. Classes 1-5 use Primary topics, Classes 6-10 use Secondary topics."
        actions={
          <span className="chip bg-surface-2 text-muted">
            <Layers className="h-3.5 w-3.5" /> {data.total_topics} topics
          </span>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Classes"
          value={classes.length}
          icon={GraduationCap}
          tone="blue"
          helper="Classes 1 to 10"
        />
        <StatCard
          label="Subjects"
          value={subjects.length}
          icon={BookOpen}
          tone="violet"
          helper={subjects.map((subject) => subject.name).join(" · ")}
        />
        <StatCard
          label="Topics"
          value={data.total_topics}
          icon={Layers}
          tone="emerald"
          helper={`${subjects.reduce((sum, s) => sum + s.primary_topics, 0)} Primary · ${subjects.reduce(
            (sum, s) => sum + s.secondary_topics,
            0
          )} Secondary`}
        />
        <StatCard
          label="Students enrolled"
          value={totalStudents}
          icon={Users}
          tone="sun"
          helper="Active student accounts"
        />
      </div>

      <section>
        <SectionHeading
          title="Class structure"
          subtitle="Topic counts are per curriculum level, shared by every class in that level."
          icon={GraduationCap}
        />
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          {classes.map((row) => (
            <div key={row.class_level} className="card p-4">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-bold text-ink">{classLevelLabel(row.class_level)}</p>
                <span
                  className={`chip ${
                    row.level === "Primary"
                      ? "bg-blue-50 text-blue-700 dark:bg-blue-500/15 dark:text-blue-200"
                      : "bg-violet-50 text-violet-700 dark:bg-violet-500/15 dark:text-violet-200"
                  }`}
                >
                  {row.level}
                </span>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-2 text-center">
                <div className="rounded-lg bg-surface-2 px-2 py-1.5">
                  <p className="text-[9px] font-semibold uppercase tracking-wide text-muted">
                    Students
                  </p>
                  <p className="text-sm font-extrabold text-ink">{row.students}</p>
                </div>
                <div className="rounded-lg bg-surface-2 px-2 py-1.5">
                  <p className="text-[9px] font-semibold uppercase tracking-wide text-muted">
                    Topics
                  </p>
                  <p className="text-sm font-extrabold text-ink">{row.topics}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="card flex flex-col gap-3 p-4 sm:flex-row sm:items-center">
        <div className="flex flex-wrap gap-1.5">
          {LEVEL_FILTERS.map((level) => (
            <button
              key={level}
              type="button"
              onClick={() => setLevelFilter(level)}
              className={`chip transition ${
                levelFilter === level
                  ? "bg-primary-600 text-white"
                  : "bg-surface-2 text-muted hover:text-ink"
              }`}
            >
              {level}
            </button>
          ))}
        </div>
        <div className="relative sm:ml-auto sm:w-80">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search a topic..."
            className="input pl-9"
          />
        </div>
        <span className="chip bg-surface-2 text-muted">{shownTopics} shown</span>
      </div>

      {visibleSubjects.length === 0 ? (
        <EmptyState
          icon={BookOpen}
          title="No topics match"
          description="Try another word or switch the level filter."
          action={
            <button
              type="button"
              onClick={() => {
                setSearch("");
                setLevelFilter("All");
              }}
              className="btn-secondary"
            >
              Clear filters
            </button>
          }
        />
      ) : (
        visibleSubjects.map((subject) => {
          const style = subjectStyle(subject.name);
          const Icon = style.icon;
          return (
            <section key={subject.name} className={`card overflow-hidden border ${style.border}`}>
              <div className={`flex flex-wrap items-center gap-3 px-5 py-4 ${style.soft}`}>
                <span className="sticker bg-surface text-xl shadow-sm">{subject.emoji}</span>
                <div className="min-w-0 flex-1">
                  <h2 className="text-base font-extrabold text-ink">{subject.name}</h2>
                  <p className="text-[11px] text-ink/70">{subject.tagline}</p>
                </div>
                <div className="flex gap-2">
                  <span className="chip bg-surface/70 text-ink">
                    {subject.primary_topics} Primary
                  </span>
                  <span className="chip bg-surface/70 text-ink">
                    {subject.secondary_topics} Secondary
                  </span>
                </div>
              </div>

              <div className="px-5 py-4">
                <p className="text-xs leading-relaxed text-muted">{subject.description}</p>
                <div className="mt-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
                  {subject.topics.map((topic) => (
                    <div
                      key={topic.slug}
                      className="rounded-xl border border-line bg-surface-2/40 px-3 py-2.5"
                    >
                      <div className="flex items-start gap-2">
                        <span className="text-lg">{topic.emoji}</span>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-xs font-semibold text-ink">
                            {topic.title}
                          </p>
                          <p className="text-[10px] text-muted">
                            {topic.level} · {topic.classes?.length
                              ? topic.classes.join(", ")
                              : "All classes in level"}
                          </p>
                        </div>
                        <Icon className="h-3.5 w-3.5 shrink-0 text-muted" />
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4">
                  <ProgressBar
                    value={
                      ((subject.primary_topics + subject.secondary_topics) /
                        (data.total_topics || 1)) *
                      100
                    }
                    tone={style.bar}
                  />
                  <p className="mt-1.5 text-[11px] text-muted">
                    {subject.primary_topics + subject.secondary_topics} of {data.total_topics}{" "}
                    topics in this subject
                  </p>
                </div>
              </div>
            </section>
          );
        })
      )}
    </div>
  );
}
