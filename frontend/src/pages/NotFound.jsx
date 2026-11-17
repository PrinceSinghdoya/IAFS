import { Link } from "react-router-dom";
import { ArrowLeft, Compass } from "lucide-react";

import Logo from "../components/Logo";
import ThemeToggle from "../components/ThemeToggle";
import { homeForRole, useAuth } from "../context/AuthContext";

/** Friendly fallback page for unknown URLs. */
export default function NotFound() {
  const { user } = useAuth();
  const home = user ? homeForRole(user.role) : "/login";

  return (
    <div className="flex min-h-screen flex-col bg-canvas">
      <header className="border-b border-line bg-surface/80">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4 sm:px-6">
          <Logo variant="dark" to={home} />
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">
              404
            </span>
            <ThemeToggle compact />
          </div>
        </div>
      </header>

      <main className="flex flex-1 items-center justify-center px-4 py-16">
        <div className="mx-auto max-w-md text-center">
          <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-50 text-primary-600 dark:bg-primary-500/15 dark:text-primary-300">
            <Compass className="h-8 w-8" />
          </span>
          <p className="mt-6 text-xs font-semibold uppercase tracking-[0.16em] text-primary-600 dark:text-primary-300">
            Page not found
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-ink">
            This page is not on the timetable
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-muted">
            The link you followed does not exist in IAFS. Head back to your dashboard
            and continue from there.
          </p>
          <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
            <Link to={home} className="btn-primary">
              <ArrowLeft className="h-4 w-4" />
              {user ? "Back to dashboard" : "Sign in"}
            </Link>
            {user && user.role === "student" && (
              <Link to="/subjects" className="btn-secondary">
                Browse subjects
              </Link>
            )}
          </div>
        </div>
      </main>

      <footer className="border-t border-line py-5 text-center text-xs text-muted">
        IAFS School Learning · English and Mathematics for Classes 1-10
      </footer>
    </div>
  );
}
