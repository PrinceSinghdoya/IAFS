import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ArrowRight, BookOpen, Play, Search, Sparkles } from "lucide-react";

import Alert from "../components/Alert";
import { SectionLoader } from "../components/Loading";
import {
  EmptyState,
  PageHeader,
  ProgressBar,
  SectionHeading,
  StatusBadge,
} from "../components/ui";
import { SUBJECT_STYLES, classLevelLabel, subjectStyle, topicIcon } from "../lib/constants";
import { percent } from "../lib/format";
import { useApi, useDocumentTitle } from "../lib/useApi";

const SUBJECT_FILTERS = ["All", "English", "Mathematics"];

export default function Subjects() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeSubject = searchParams.get("subject") || "All";
  const [search, setSearch] = useState("");

  const subjectsQuery = useApi("/subjects");
  const topicsQuery = useApi("/topics");
  useDocumentTitle("Subjects");

  const loading = subjectsQuery.loading || topicsQuery.loading;
  const error = subjectsQuery.error || topicsQuery.error;
  const subjects = subjectsQuery.data?.subjects || [];
  const topics = topicsQuery.data?.topics || [];
  const classLevel = topicsQuery.data?.class_level || subjectsQuery.data?.class_level;
  const level = topicsQuery.data?.level || subjectsQuery.data?.level;

  const filteredTopics = useMemo(() => {
    const text = search.trim().toLowerCase();
    return topics.filter((topic) => {
      if (activeSubject !== "All" && topic.subject !== activeSubject) return false;
      if (!text) return true;
      return (
        topic.title.toLowerCase().includes(text) ||
        topic.description.toLowerCase().includes(text)
      );
    });
  }, [topics, activeSubject, search]);

  const grouped = useMemo(() => {
    const map = {};
    for (const topic of filteredTopics) {
      map[topic.subject] = map[topic.subject] || [];
      map[topic.subject].push(topic);
    }
    return map;
  }, [filteredTopics]);

  function chooseSubject(subject) {
    if (subject === "All") {
      setSearchParams({});
    } else {
      setSearchParams({ subject });
    }
  }

  if (loading && !topicsQuery.data) return <SectionLoader label="Loading subjects..." />;

  return (
    <div className="animate-fade-in space-y-6">
      <PageHeader
        eyebrow={classLevel ? `${classLevelLabel(classLevel)} · ${level}` : "Curriculum"}
        title="English and Mathematics"
        subtitle="Read a short lesson, look at the examples, then try the adaptive quiz for that topic."
        actions={
          <Link to="/quiz/start" className="btn-primary">
            <Sparkles className="h-4 w-4" />
            Surprise me with a quiz
          </Link>
        }
      />

      {error && <Alert tone="error">{error}</Alert>}

      <div className="grid gap-3 sm:grid-cols-2">
        {subjects.map((subject) => {
          const style = subjectStyle(subject.name);
          const Icon = style.icon;
          return (
            <div key={subject.name} className={`card border p-4 ${style.border}`}>
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
                <div className="text-right">
                  <p className="text-lg font-extrabold text-ink">{percent(subject.average)}</p>
                  <p className="text-[10px] text-muted">average</p>
                </div>
              </div>
              <div className="mt-3">
                <ProgressBar
                  value={
                    subject.topics_total
                      ? (subject.topics_started / subject.topics_total) * 100
                      : 0
                  }
                  tone={style.bar}
                />
                <p className="mt-1.5 text-[11px] text-muted">
                  {subject.topics_started}/{subject.topics_total} topics started · best{" "}
                  {percent(subject.best)}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="card flex flex-col gap-3 p-4 sm:flex-row sm:items-center">
        <div className="flex flex-wrap gap-1.5">
          {SUBJECT_FILTERS.map((subject) => (
            <button
              key={subject}
              type="button"
              onClick={() => chooseSubject(subject)}
              className={`chip transition ${
                activeSubject === subject
                  ? "bg-primary-600 text-white"
                  : "bg-surface-2 text-muted hover:text-ink"
              }`}
            >
              {subject}
            </button>
          ))}
        </div>
        <div className="relative sm:ml-auto sm:w-72">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search a topic..."
            className="input pl-9"
          />
        </div>
      </div>

      {Object.keys(grouped).length === 0 ? (
        <EmptyState
          icon={BookOpen}
          title="No topics match your search"
          description="Try a different word, or clear the subject filter."
          action={
            <button
              type="button"
              onClick={() => {
                setSearch("");
                chooseSubject("All");
              }}
              className="btn-secondary"
            >
              Clear filters
            </button>
          }
        />
      ) : (
        Object.entries(grouped).map(([subjectName, subjectTopics]) => {
          const style = SUBJECT_STYLES[subjectName] || SUBJECT_STYLES.Mathematics;
          return (
            <section key={subjectName}>
              <SectionHeading
                title={`${style.emoji} ${subjectName}`}
                subtitle={`${subjectTopics.length} topics for your class`}
              />
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {subjectTopics.map((topic) => {
                  const Icon = topicIcon(topic.icon);
                  const coverage = topic.best ?? 0;
                  return (
                    <div key={topic.slug} className="card card-hover flex flex-col p-4">
                      <div className="flex items-start gap-3">
                        <span className="sticker bg-surface-2 text-xl">{topic.emoji}</span>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-start justify-between gap-2">
                            <h3 className="text-sm font-bold leading-snug text-ink">
                              {topic.title}
                            </h3>
                            <StatusBadge status={topic.status} />
                          </div>
                          <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-muted">
                            {topic.description}
                          </p>
                        </div>
                      </div>

                      <div className="mt-3">
                        <div className="mb-1 flex items-center justify-between text-[11px]">
                          <span className="text-muted">
                            {topic.attempts
                              ? `${topic.attempts} attempt${topic.attempts === 1 ? "" : "s"}`
                              : "Not attempted"}
                          </span>
                          <span className="font-semibold text-ink">
                            Best {percent(topic.best)}
                          </span>
                        </div>
                        <ProgressBar value={coverage} tone={style.bar} />
                      </div>

                      <div className="mt-3 flex items-center gap-2 border-t border-line pt-3">
                        <span className="inline-flex items-center gap-1 text-[10px] font-medium text-muted">
                          <Icon className="h-3.5 w-3.5" />
                          {topic.estimated_minutes} min read
                        </span>
                        <div className="ml-auto flex gap-1.5">
                          <Link
                            to={`/topics/${topic.slug}`}
                            className="btn-secondary px-2.5 py-1.5 text-xs"
                          >
                            Lesson
                          </Link>
                          <Link
                            to={`/quiz/start?topic=${encodeURIComponent(topic.slug)}`}
                            className="btn-primary px-2.5 py-1.5 text-xs"
                          >
                            <Play className="h-3 w-3" />
                            Quiz
                          </Link>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          );
        })
      )}

      <div className="card flex flex-wrap items-center gap-3 bg-gradient-to-r from-primary-50 to-accent-50 p-5 dark:from-primary-500/10 dark:to-accent-500/10">
        <Sparkles className="h-5 w-5 text-primary-600 dark:text-primary-300" />
        <p className="min-w-0 flex-1 text-sm text-ink/80">
          Not sure where to begin? The assistant explains any topic in a simpler way and never
          gives away quiz answers.
        </p>
        <Link to="/assistant" className="btn-secondary">
          Ask a question <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
