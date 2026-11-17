import { useId } from "react";

const TONES = {
  excellent: { from: "#10b981", to: "#059669", text: "text-emerald-600 dark:text-emerald-300" },
  good: { from: "#3b82f6", to: "#2563eb", text: "text-blue-600 dark:text-blue-300" },
  practice: { from: "#f59e0b", to: "#d97706", text: "text-amber-600 dark:text-amber-300" },
  needs: { from: "#f43f5e", to: "#e11d48", text: "text-rose-600 dark:text-rose-300" },
};

function toneFor(value) {
  if (value >= 85) return TONES.excellent;
  if (value >= 60) return TONES.good;
  if (value >= 40) return TONES.practice;
  return TONES.needs;
}

/** Circular score indicator used on quiz results and progress cards. */
export default function ScoreRing({ value = 0, size = 140, label = "Score" }) {
  const gradientId = useId().replace(/:/g, "");
  const safe = Math.max(0, Math.min(100, Number(value) || 0));
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const tone = toneFor(safe);

  return (
    <div
      className="relative inline-flex items-center justify-center"
      style={{ width: size, height: size }}
      role="img"
      aria-label={`${label}: ${Math.round(safe)} percent`}
    >
      <svg viewBox="0 0 120 120" width={size} height={size} aria-hidden="true">
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={tone.from} />
            <stop offset="100%" stopColor={tone.to} />
          </linearGradient>
        </defs>
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          className="stroke-slate-200 dark:stroke-slate-700"
          strokeWidth="9"
        />
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth="9"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - (safe / 100) * circumference}
          transform="rotate(-90 60 60)"
          style={{ transition: "stroke-dashoffset 0.8s ease" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-3xl font-extrabold tracking-tight ${tone.text}`}>
          {Math.round(safe)}%
        </span>
        <span className="mt-0.5 text-[10px] font-semibold uppercase tracking-wider text-muted">
          {label}
        </span>
      </div>
    </div>
  );
}
