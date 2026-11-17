import { Loader2 } from "lucide-react";

export function Spinner({ className = "h-5 w-5" }) {
  return <Loader2 className={`animate-spin ${className}`} aria-hidden="true" />;
}

export function FullPageLoader({ label = "Loading..." }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-canvas">
      <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-surface shadow-card">
        <Spinner className="h-6 w-6 text-primary-600 dark:text-primary-300" />
      </span>
      <p className="text-sm font-medium text-muted">{label}</p>
    </div>
  );
}

export function SectionLoader({ label = "Loading data..." }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-line bg-surface py-16">
      <Spinner className="h-6 w-6 text-primary-600 dark:text-primary-300" />
      <p className="text-sm text-muted">{label}</p>
    </div>
  );
}

export function SkeletonRows({ rows = 3 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, index) => (
        <div
          key={index}
          className="h-16 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-700/40"
        />
      ))}
    </div>
  );
}
