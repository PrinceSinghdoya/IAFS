import { Link } from "react-router-dom";
import { ArrowRight, Sparkles, TrendingUp } from "lucide-react";

import { CategoryBadge, ProgressBar } from "./ui";
import { percent } from "../lib/format";
import { categoryStyle } from "../lib/constants";

/**
 * Compact adaptive-feedback summary used on the student dashboard.
 * Everything shown here is computed from real quiz data by the backend.
 */
export default function FeedbackCard({ feedback }) {
  if (!feedback) return null;

  const style = categoryStyle(feedback.category);
  const metrics = feedback.metrics || {};
  const suggestions = (feedback.suggestions || []).slice(0, 2);
  const focus = (feedback.focus_topics || []).slice(0, 1)[0];

  return (
    <div className="card overflow-hidden">
      <div className={`border-b border-line bg-gradient-to-r px-5 py-4 ${style.soft}`}>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide">
            <Sparkles className="h-4 w-4" />
            Adaptive feedback
          </p>
          <CategoryBadge category={feedback.category} />
        </div>
        <h3 className="mt-2.5 text-[15px] font-bold leading-snug text-ink">
          {feedback.headline}
        </h3>
      </div>

      <div className="px-5 py-4">
        <p className="text-sm leading-relaxed text-ink/80">{feedback.message}</p>

        <div className="mt-4 grid grid-cols-3 gap-2 text-center">
          <div className="rounded-xl bg-surface-2 px-2 py-2">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">Average</p>
            <p className="mt-0.5 text-sm font-bold text-ink">{percent(metrics.average_percentage)}</p>
          </div>
          <div className="rounded-xl bg-surface-2 px-2 py-2">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">Quizzes</p>
            <p className="mt-0.5 text-sm font-bold text-ink">{metrics.attempts ?? 0}</p>
          </div>
          <div className="rounded-xl bg-surface-2 px-2 py-2">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">Streak</p>
            <p className="mt-0.5 text-sm font-bold text-ink">
              {metrics.streak_days ?? 0}d
            </p>
          </div>
        </div>

        {focus && (
          <div className="mt-4">
            <div className="mb-1.5 flex items-center justify-between text-xs">
              <span className="inline-flex items-center gap-1.5 font-semibold text-ink">
                <TrendingUp className="h-3.5 w-3.5 text-primary-600 dark:text-primary-300" />
                Focus: {focus.title}
              </span>
              <span className="font-semibold text-muted">{percent(focus.percentage)}</span>
            </div>
            <ProgressBar value={focus.percentage || 0} tone={style.bar} />
          </div>
        )}

        {suggestions.length > 0 && (
          <ul className="mt-4 space-y-1.5">
            {suggestions.map((suggestion, index) => (
              <li key={index} className="flex gap-2 text-xs leading-relaxed text-ink/80">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary-400" />
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        )}

        <Link
          to="/feedback"
          className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-300 dark:hover:text-primary-200"
        >
          See full feedback
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
