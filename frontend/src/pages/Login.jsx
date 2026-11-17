import { useEffect, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  Eye,
  EyeOff,
  GraduationCap,
  Lock,
  Mail,
  Presentation,
  ShieldCheck,
  UserRound,
} from "lucide-react";

import Alert from "../components/Alert";
import AuthShell from "../components/AuthShell";
import { Spinner } from "../components/Loading";
import { homeForRole, useAuth } from "../context/AuthContext";
import { api } from "../lib/api";
import { classLevelLabel } from "../lib/constants";

const ROLE_TABS = [
  { value: "student", label: "Student", icon: UserRound },
  { value: "teacher", label: "Teacher", icon: Presentation },
  { value: "admin", label: "Administrator", icon: ShieldCheck },
];

const FALLBACK_DEMO = [
  { role: "student", label: "Class 4 student", name: "Aarav Mehta", email: "aarav@iafs.school", password: "Student@123" },
  { role: "student", label: "Class 8 student", name: "Priya Nair", email: "priya@iafs.school", password: "Student@123" },
  { role: "teacher", label: "Teacher", name: "Ananya Sharma", email: "teacher@iafs.school", password: "Teacher@123" },
  { role: "admin", label: "Administrator", name: "Meera Kapoor", email: "admin@iafs.school", password: "Admin@123" },
];

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [role, setRole] = useState("student");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [demoAccounts, setDemoAccounts] = useState(FALLBACK_DEMO);

  // Demo credentials come from the backend so they never go stale.
  useEffect(() => {
    let cancelled = false;
    api
      .get("/meta")
      .then((data) => {
        if (!cancelled && Array.isArray(data.demo_accounts) && data.demo_accounts.length) {
          setDemoAccounts(data.demo_accounts);
        }
      })
      .catch(() => {
        // The fallback list is shown when the API is not reachable yet.
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (user) {
    return <Navigate to={homeForRole(user.role)} replace />;
  }

  const visibleDemos = demoAccounts.filter((account) => account.role === role);

  function useDemo(account) {
    setRole(account.role);
    setEmail(account.email);
    setPassword(account.password);
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const signedIn = await login(email.trim(), password);
      const fallback = homeForRole(signedIn.role);
      const from = location.state?.from;
      const target = from && from.startsWith("/") ? from : fallback;
      navigate(target, { replace: true });
    } catch (err) {
      setError(err.message || "Could not sign in. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthShell>
      <div className="mb-6">
        <span className="inline-flex items-center gap-1.5 rounded-full bg-primary-50 px-3 py-1 text-[11px] font-bold uppercase tracking-wide text-primary-700 dark:bg-primary-500/15 dark:text-primary-200">
          <GraduationCap className="h-3.5 w-3.5" />
          Welcome back
        </span>
        <h1 className="mt-3 text-2xl font-extrabold tracking-tight text-ink">Sign in to IAFS</h1>
        <p className="mt-1 text-sm text-muted">
          Choose your role, then use your school email and password.
        </p>
      </div>

      <div className="mb-5 grid grid-cols-3 gap-1 rounded-xl border border-line bg-surface-2/60 p-1">
        {ROLE_TABS.map((tab) => {
          const Icon = tab.icon;
          const active = role === tab.value;
          return (
            <button
              key={tab.value}
              type="button"
              onClick={() => {
                setRole(tab.value);
                setError("");
              }}
              className={`inline-flex items-center justify-center gap-1.5 rounded-lg px-2 py-2 text-xs font-semibold transition ${
                active
                  ? "bg-surface text-ink shadow-sm"
                  : "text-muted hover:text-ink"
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              <span className="truncate">{tab.label}</span>
            </button>
          );
        })}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Alert tone="error">{error}</Alert>}

        <div>
          <label htmlFor="email" className="label">
            School email
          </label>
          <div className="relative">
            <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@iafs.school"
              className="input pl-10"
            />
          </div>
        </div>

        <div>
          <label htmlFor="password" className="label">
            Password
          </label>
          <div className="relative">
            <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="At least 8 characters"
              className="input px-10"
            />
            <button
              type="button"
              onClick={() => setShowPassword((value) => !value)}
              className="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-lg text-muted transition hover:bg-surface-2 hover:text-ink"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? <Spinner className="h-4 w-4" /> : null}
          {submitting ? "Signing in..." : "Sign in"}
          {!submitting && <ArrowRight className="h-4 w-4" />}
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-muted">
        New student?{" "}
        <Link to="/register" className="link">
          Create an account
        </Link>
      </p>

      <div className="mt-6 rounded-2xl border border-dashed border-line bg-surface-2/50 p-3.5">
        <p className="text-[11px] font-bold uppercase tracking-wide text-muted">
          Demo {ROLE_TABS.find((tab) => tab.value === role)?.label.toLowerCase()} accounts
        </p>
        <div className="mt-2 space-y-1.5">
          {visibleDemos.length === 0 && (
            <p className="text-xs text-muted">No demo account for this role.</p>
          )}
          {visibleDemos.map((account) => (
            <button
              key={account.email}
              type="button"
              onClick={() => useDemo(account)}
              className="flex w-full items-center justify-between gap-3 rounded-lg border border-line bg-surface px-3 py-2 text-left transition hover:border-primary-300 dark:hover:border-primary-400/40"
            >
              <span className="min-w-0">
                <span className="block truncate text-xs font-semibold text-ink">
                  {account.name}
                </span>
                <span className="block truncate text-[10px] text-muted">
                  {account.label} · {account.email}
                  {account.class_level ? ` · ${classLevelLabel(account.class_level)}` : ""}
                </span>
              </span>
              <span className="shrink-0 text-[10px] font-bold uppercase tracking-wide text-primary-600 dark:text-primary-300">
                Use
              </span>
            </button>
          ))}
        </div>
        <p className="mt-2 text-[10px] leading-relaxed text-muted">
          Demo passwords are shown in the project README. All demo names are fictional.
        </p>
      </div>
    </AuthShell>
  );
}
