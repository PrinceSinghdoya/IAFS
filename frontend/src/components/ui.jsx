import { BookOpen, Sparkles } from "lucide-react";

import {
  DIFFICULTY_STYLES,
  SENTIMENT_STYLES,
  STATUS_STYLES,
  categoryStyle,
  classLevelLabel,
} from "../lib/constants";

const STAT_TONES = {
  blue: "bg-blue-50 text-blue-600 dark:bg-blue-500/15 dark:text-blue-300",
  violet: "bg-violet-50 text-violet-600 dark:bg-violet-500/15 dark:text-violet-300",
  emerald: "bg-emerald-50 text-emerald-600 dark:bg-emerald-500/15 dark:text-emerald-300",
  amber: "bg-amber-50 text-amber-600 dark:bg-amber-500/15 dark:text-amber-300",
  rose: "bg-rose-50 text-rose-600 dark:bg-rose-500/15 dark:text-rose-300",
  sun: "bg-sun-100 text-sun-600 dark:bg-sun-500/15 dark:text-sun-300",
  slate: "bg-slate-100 text-slate-600 dark:bg-slate-700/50 dark:text-slate-300",
};

export function PageHeader({ eyebrow, title, subtitle, actions }) {
  return (
    <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {eyebrow && (
          <p className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-primary-600 dark:text-primary-300">
            {eyebrow}
          </p>
        )}
        <h1 className="text-2xl font-extrabold tracking-tight text-ink sm:text-[30px]">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-1.5 max-w-2xl text-sm leading-relaxed text-muted">
            {subtitle}
          </p>
        )}
      </div>
      {actions && <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}

export function StatCard({ label, value, suffix, icon: Icon, tone = "blue", helper }) {
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-wide text-muted">
            {label}
          </p>
          <p className="mt-2 text-2xl font-extrabold tracking-tight text-ink">
            {value}
            {suffix && (
              <span className="ml-0.5 text-base font-semibold text-muted">{suffix}</span>
            )}
          </p>
        </div>
        {Icon && (
          <span
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
              STAT_TONES[tone] || STAT_TONES.blue
            }`}
          >
            <Icon className="h-5 w-5" />
          </span>
        )}
      </div>
      {helper && <p className="mt-3 text-xs leading-relaxed text-muted">{helper}</p>}
    </div>
  );
}

export function CategoryBadge({ category, className = "" }) {
  const style = categoryStyle(category);
  return (
    <span className={`chip ${style.badge} ${className}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${style.bar}`} />
      {category || "Getting Started"}
    </span>
  );
}

export function StatusBadge({ status }) {
  return (
    <span className={`chip ${STATUS_STYLES[status] || STATUS_STYLES["Not started"]}`}>
      {status || "Not started"}
    </span>
  );
}

export function SentimentPill({ sentiment }) {
  if (!sentiment) return null;
  return (
    <span className={`chip ${SENTIMENT_STYLES[sentiment] || SENTIMENT_STYLES.Neutral}`}>
      {sentiment}
    </span>
  );
}

export function DifficultyPill({ difficulty, label = "Difficulty" }) {
  if (!difficulty) return null;
  return (
    <span className={`chip capitalize ${DIFFICULTY_STYLES[difficulty] || DIFFICULTY_STYLES.easy}`}>
      {label}: {difficulty}
    </span>
  );
}

export function ProgressBar({ value = 0, tone = "bg-primary-500", className = "" }) {
  const safeValue = Math.max(0, Math.min(100, Number(value) || 0));
  return (
    <div className={`h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700/60 ${className}`}>
      <div
        className={`h-full rounded-full transition-all duration-500 ${tone}`}
        style={{ width: `${safeValue}%` }}
      />
    </div>
  );
}

export function EmptyState({ icon: Icon = BookOpen, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-line bg-surface-2/60 px-6 py-12 text-center">
      <span className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-surface text-primary-600 shadow-sm dark:text-primary-300">
        <Icon className="h-6 w-6" />
      </span>
      <h3 className="text-sm font-semibold text-ink">{title}</h3>
      {description && (
        <p className="mt-1 max-w-sm text-sm leading-relaxed text-muted">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function ClassBadge({ level, className = "" }) {
  return (
    <span
      className={`chip bg-primary-50 text-primary-700 dark:bg-primary-500/15 dark:text-primary-200 ${className}`}
    >
      <Sparkles className="h-3.5 w-3.5" />
      {classLevelLabel(level)}
    </span>
  );
}

export function SectionHeading({ title, subtitle, action, icon: Icon }) {
  return (
    <div className="mb-3 flex flex-wrap items-end justify-between gap-2">
      <div>
        <h2 className="inline-flex items-center gap-2 text-lg font-bold text-ink">
          {Icon && <Icon className="h-5 w-5 text-primary-600 dark:text-primary-300" />}
          {title}
        </h2>
        {subtitle && <p className="mt-0.5 text-xs text-muted">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function Avatar({ name = "?", size = "md", className = "" }) {
  const sizes = {
    sm: "h-8 w-8 text-[10px]",
    md: "h-10 w-10 text-xs",
    lg: "h-14 w-14 text-base",
  };
  const initials = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
  return (
    <span
      className={`flex shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-accent-500 font-bold text-white shadow-sm ${
        sizes[size] || sizes.md
      } ${className}`}
      aria-hidden="true"
    >
      {initials || "?"}
    </span>
  );
}

export function MiniTrend({ value, label }) {
  const positive = Number(value) > 0;
  const negative = Number(value) < 0;
  return (
    <span
      className={`chip ${
        positive
          ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200"
          : negative
            ? "bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-200"
            : "bg-slate-100 text-slate-600 dark:bg-slate-700/50 dark:text-slate-300"
      }`}
    >
      {positive ? "▲" : negative ? "▼" : "•"} {label}
    </span>
  );
}
