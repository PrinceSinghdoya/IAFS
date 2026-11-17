import { Link } from "react-router-dom";
import { BookOpenCheck } from "lucide-react";

/** Brand logo used on auth pages and in the sidebar. */
export default function Logo({ variant = "light", to = "/", showTagline = false }) {
  const isLight = variant === "light";

  return (
    <Link to={to} className="inline-flex items-center gap-3">
      <span className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-accent-600 text-white shadow-float">
        <BookOpenCheck className="h-5 w-5" strokeWidth={2.2} />
        <span className="absolute -right-1 -top-1 h-3 w-3 rounded-full border-2 border-white bg-sun-400 dark:border-surface" />
      </span>
      <span>
        <span
          className={`block text-lg font-extrabold leading-tight tracking-tight ${
            isLight ? "text-white" : "text-ink"
          }`}
        >
          IAFS
        </span>
        <span
          className={`block text-[10px] font-semibold uppercase tracking-[0.16em] ${
            isLight ? "text-blue-100" : "text-muted"
          }`}
        >
          {showTagline ? "Learning that adapts" : "School learning"}
        </span>
      </span>
    </Link>
  );
}
