import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  BookOpenCheck,
  Eye,
  EyeOff,
  Hash,
  KeyRound,
  Lock,
  Mail,
  Presentation,
  UserRound,
} from "lucide-react";

import Alert from "../components/Alert";
import AuthShell from "../components/AuthShell";
import { Spinner } from "../components/Loading";
import { homeForRole, useAuth } from "../context/AuthContext";
import { CLASS_LEVELS } from "../lib/constants";

const INITIAL_FORM = {
  name: "",
  email: "",
  password: "",
  confirmPassword: "",
  class_level: "1",
  section: "A",
  roll_no: "",
  invite_code: "",
};

const SECTIONS = ["A", "B", "C", "D"];

export default function Register() {
  const { user, register } = useAuth();
  const navigate = useNavigate();

  const [role, setRole] = useState("student");
  const [form, setForm] = useState(INITIAL_FORM);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (user) {
    return <Navigate to={homeForRole(user.role)} replace />;
  }

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (form.password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }
    if (!/[A-Za-z]/.test(form.password) || !/\d/.test(form.password)) {
      setError("Password must include at least one letter and one number.");
      return;
    }
    if (form.password !== form.confirmPassword) {
      setError("The two passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        name: form.name.trim(),
        email: form.email.trim(),
        password: form.password,
        role,
      };
      if (role === "student") {
        payload.class_level = Number(form.class_level);
        payload.section = form.section;
        payload.roll_no = form.roll_no.trim();
      } else {
        payload.invite_code = form.invite_code.trim();
      }
      const created = await register(payload);
      navigate(homeForRole(created.role), { replace: true });
    } catch (err) {
      setError(err.message || "Could not create the account. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  const classLevel = Number(form.class_level);

  return (
    <AuthShell>
      <div className="mb-5">
        <span className="inline-flex items-center gap-1.5 rounded-full bg-accent-50 px-3 py-1 text-[11px] font-bold uppercase tracking-wide text-accent-700 dark:bg-accent-500/15 dark:text-accent-200">
          <BookOpenCheck className="h-3.5 w-3.5" />
          Join IAFS
        </span>
        <h1 className="mt-3 text-2xl font-extrabold tracking-tight text-ink">
          Create your account
        </h1>
        <p className="mt-1 text-sm text-muted">
          Students choose a class from 1 to 10. Teachers need the school invite code.
        </p>
      </div>

      <div className="mb-5 grid grid-cols-2 gap-1 rounded-xl border border-line bg-surface-2/60 p-1">
        {[
          { value: "student", label: "Student", icon: UserRound },
          { value: "teacher", label: "Teacher", icon: Presentation },
        ].map((tab) => {
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
              className={`inline-flex items-center justify-center gap-1.5 rounded-lg px-3 py-2 text-xs font-semibold transition ${
                active ? "bg-surface text-ink shadow-sm" : "text-muted hover:text-ink"
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      <form onSubmit={handleSubmit} className="space-y-3.5">
        {error && <Alert tone="error">{error}</Alert>}

        <div>
          <label htmlFor="name" className="label">
            Full name
          </label>
          <div className="relative">
            <UserRound className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
            <input
              id="name"
              type="text"
              autoComplete="name"
              required
              minLength={2}
              maxLength={60}
              value={form.name}
              onChange={(event) => update("name", event.target.value)}
              placeholder="For example, Aarav Mehta"
              className="input pl-10"
            />
          </div>
        </div>

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
              value={form.email}
              onChange={(event) => update("email", event.target.value)}
              placeholder="you@iafs.school"
              className="input pl-10"
            />
          </div>
        </div>

        {role === "student" ? (
          <>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="class_level" className="label">
                  Class
                </label>
                <select
                  id="class_level"
                  value={form.class_level}
                  onChange={(event) => update("class_level", event.target.value)}
                  className="input"
                >
                  {CLASS_LEVELS.map((level) => (
                    <option key={level} value={level}>
                      Class {level}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="section" className="label">
                  Section
                </label>
                <select
                  id="section"
                  value={form.section}
                  onChange={(event) => update("section", event.target.value)}
                  className="input"
                >
                  {SECTIONS.map((section) => (
                    <option key={section} value={section}>
                      {section}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="rounded-xl border border-line bg-surface-2/50 px-3 py-2 text-[11px] leading-relaxed text-muted">
              You will study the{" "}
              <span className="font-semibold text-ink">
                {classLevel <= 5 ? "Primary" : "Secondary"}
              </span>{" "}
              English and Mathematics topics for Class {classLevel}.
            </div>

            <div>
              <label htmlFor="roll_no" className="label">
                Roll number <span className="font-normal text-muted">(optional)</span>
              </label>
              <div className="relative">
                <Hash className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
                <input
                  id="roll_no"
                  type="text"
                  maxLength={20}
                  value={form.roll_no}
                  onChange={(event) => update("roll_no", event.target.value)}
                  placeholder="For example, 4A-07"
                  className="input pl-10"
                />
              </div>
            </div>
          </>
        ) : (
          <div>
            <label htmlFor="invite_code" className="label">
              Teacher invite code
            </label>
            <div className="relative">
              <KeyRound className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
              <input
                id="invite_code"
                type="text"
                required
                value={form.invite_code}
                onChange={(event) => update("invite_code", event.target.value)}
                placeholder="Ask your school administrator"
                className="input pl-10"
              />
            </div>
            <p className="mt-1.5 text-[11px] text-muted">
              Demo invite code: <span className="font-semibold text-ink">IAFS2026</span>
            </p>
          </div>
        )}

        <div>
          <label htmlFor="password" className="label">
            Password
          </label>
          <div className="relative">
            <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              required
              minLength={8}
              value={form.password}
              onChange={(event) => update("password", event.target.value)}
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
          <p className="mt-1 text-[11px] text-muted">
            Use at least 8 characters with one letter and one number.
          </p>
        </div>

        <div>
          <label htmlFor="confirmPassword" className="label">
            Confirm password
          </label>
          <div className="relative">
            <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
            <input
              id="confirmPassword"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              required
              value={form.confirmPassword}
              onChange={(event) => update("confirmPassword", event.target.value)}
              placeholder="Type it again"
              className="input pl-10"
            />
          </div>
        </div>

        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? <Spinner className="h-4 w-4" /> : null}
          {submitting ? "Creating account..." : "Create account"}
          {!submitting && <ArrowRight className="h-4 w-4" />}
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-muted">
        Already have an account?{" "}
        <Link to="/login" className="link">
          Sign in
        </Link>
      </p>
    </AuthShell>
  );
}
