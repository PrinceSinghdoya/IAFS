import { Moon, Sun } from "lucide-react";

import { useTheme } from "../context/ThemeContext";

/**
 * Light / dark switch used on every page.
 * The icon shows what the button will switch to, with a readable label.
 */
export default function ThemeToggle({ className = "", compact = false }) {
  const { isDark, toggle } = useTheme();

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      className={`group inline-flex items-center gap-2 rounded-full border border-line bg-surface px-2 py-1.5 text-muted shadow-sm transition hover:border-primary-300 hover:text-ink ${
        compact ? "" : "sm:pr-3"
      } ${className}`}
    >
      <span className="relative flex h-7 w-7 items-center justify-center rounded-full bg-surface-2 transition group-hover:bg-primary-50 dark:group-hover:bg-primary-500/20">
        {isDark ? (
          <Sun className="h-4 w-4 text-sun-400" strokeWidth={2.2} />
        ) : (
          <Moon className="h-4 w-4 text-accent-600" strokeWidth={2.2} />
        )}
      </span>
      {!compact && (
        <span className="hidden text-xs font-semibold sm:inline">
          {isDark ? "Light" : "Dark"}
        </span>
      )}
    </button>
  );
}
