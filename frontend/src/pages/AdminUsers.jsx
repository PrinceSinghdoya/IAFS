import { useState } from "react";
import {
  Check,
  KeyRound,
  Pencil,
  Plus,
  Search,
  ShieldCheck,
  UserCog,
  UserX,
  X,
} from "lucide-react";

import Alert from "../components/Alert";
import { SectionLoader, Spinner } from "../components/Loading";
import {
  Avatar,
  EmptyState,
  PageHeader,
  SectionHeading,
} from "../components/ui";
import { api } from "../lib/api";
import {
  CLASS_LEVELS,
  ROLE_LABELS,
  classLevelLabel,
} from "../lib/constants";
import { formatDate } from "../lib/format";
import { useApi, useDocumentTitle } from "../lib/useApi";

const EMPTY_FORM = {
  name: "",
  email: "",
  password: "",
  role: "student",
  class_level: "1",
  section: "A",
  roll_no: "",
};

const SECTIONS = ["A", "B", "C", "D"];

function UserForm({ mode, initial, onClose, onSaved }) {
  const [form, setForm] = useState(initial);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSaving(true);
    try {
      if (mode === "create") {
        const payload = {
          name: form.name.trim(),
          email: form.email.trim(),
          password: form.password,
          role: form.role,
        };
        if (form.role === "student") {
          payload.class_level = Number(form.class_level);
          payload.section = form.section;
          payload.roll_no = form.roll_no.trim();
        }
        await api.post("/admin/users", payload);
      } else {
        const payload = { name: form.name.trim(), role: form.role };
        if (form.role === "student") {
          payload.class_level = Number(form.class_level);
          payload.section = form.section;
          payload.roll_no = form.roll_no.trim();
        }
        await api.patch(`/admin/users/${form.id}`, payload);
      }
      onSaved();
      onClose();
    } catch (err) {
      setError(err.message || "Could not save this account.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card space-y-3 p-5">
      <div className="flex items-start justify-between gap-2">
        <SectionHeading
          title={mode === "create" ? "Add an account" : `Edit ${initial.name}`}
          subtitle={
            mode === "create"
              ? "Students need a class. Teachers and administrators do not."
              : "Change the name, role or class. The email cannot be changed."
          }
        />
        <button
          type="button"
          onClick={onClose}
          className="flex h-8 w-8 items-center justify-center rounded-lg text-muted transition hover:bg-surface-2 hover:text-ink"
          aria-label="Close form"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {error && <Alert tone="error">{error}</Alert>}

      <div className="grid gap-3 sm:grid-cols-2">
        <div>
          <label className="label" htmlFor="user-name">
            Full name
          </label>
          <input
            id="user-name"
            className="input"
            required
            minLength={2}
            maxLength={60}
            value={form.name}
            onChange={(event) => update("name", event.target.value)}
            placeholder="For example, Aarav Mehta"
          />
        </div>
        <div>
          <label className="label" htmlFor="user-email">
            School email
          </label>
          <input
            id="user-email"
            className="input"
            type="email"
            required
            disabled={mode === "edit"}
            value={form.email}
            onChange={(event) => update("email", event.target.value)}
            placeholder="name@iafs.school"
          />
        </div>
        <div>
          <label className="label" htmlFor="user-role">
            Role
          </label>
          <select
            id="user-role"
            className="input"
            value={form.role}
            onChange={(event) => update("role", event.target.value)}
          >
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
            <option value="admin">Administrator</option>
          </select>
        </div>
        {mode === "create" && (
          <div>
            <label className="label" htmlFor="user-password">
              Temporary password
            </label>
            <input
              id="user-password"
              className="input"
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={(event) => update("password", event.target.value)}
              placeholder="At least 8 characters, one number"
            />
          </div>
        )}
      </div>

      {form.role === "student" && (
        <div className="grid gap-3 sm:grid-cols-3">
          <div>
            <label className="label" htmlFor="user-class">
              Class
            </label>
            <select
              id="user-class"
              className="input"
              value={form.class_level}
              onChange={(event) => update("class_level", event.target.value)}
            >
              {CLASS_LEVELS.map((level) => (
                <option key={level} value={level}>
                  Class {level}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="user-section">
              Section
            </label>
            <select
              id="user-section"
              className="input"
              value={form.section || ""}
              onChange={(event) => update("section", event.target.value)}
            >
              {SECTIONS.map((section) => (
                <option key={section} value={section}>
                  {section}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="user-roll">
              Roll number
            </label>
            <input
              id="user-roll"
              className="input"
              maxLength={20}
              value={form.roll_no || ""}
              onChange={(event) => update("roll_no", event.target.value)}
              placeholder="Optional"
            />
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-2 pt-1">
        <button type="submit" disabled={saving} className="btn-primary">
          {saving ? <Spinner className="h-4 w-4" /> : <Check className="h-4 w-4" />}
          {mode === "create" ? "Create account" : "Save changes"}
        </button>
        <button type="button" onClick={onClose} className="btn-secondary">
          Cancel
        </button>
      </div>
    </form>
  );
}

export default function AdminUsers() {
  const [role, setRole] = useState("");
  const [classLevel, setClassLevel] = useState("");
  const [search, setSearch] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState(null);
  const [resetTarget, setResetTarget] = useState(null);
  const [newPassword, setNewPassword] = useState("");
  const [resetError, setResetError] = useState("");
  const [resetting, setResetting] = useState(false);
  const [message, setMessage] = useState("");
  const [actionError, setActionError] = useState("");
  const [busyId, setBusyId] = useState("");

  const query = new URLSearchParams();
  if (role) query.set("role", role);
  if (classLevel) query.set("class_level", classLevel);
  if (appliedSearch) query.set("search", appliedSearch);
  const { data, loading, error, reload } = useApi(
    `/admin/users${query.toString() ? `?${query}` : ""}`
  );
  useDocumentTitle("User directory");

  const users = data?.users || [];

  function applySearch(event) {
    event.preventDefault();
    setAppliedSearch(search.trim());
  }

  async function toggleActive(user) {
    setBusyId(user.id);
    setActionError("");
    setMessage("");
    try {
      await api.patch(`/admin/users/${user.id}`, { is_active: !user.is_active });
      setMessage(`${user.name} is now ${user.is_active ? "deactivated" : "active"}.`);
      await reload();
    } catch (err) {
      setActionError(err.message || "Could not update this account.");
    } finally {
      setBusyId("");
    }
  }

  async function resetPassword(event) {
    event.preventDefault();
    if (!resetTarget) return;
    setResetting(true);
    setResetError("");
    try {
      const response = await api.post(`/admin/users/${resetTarget.id}/reset-password`, {
        password: newPassword,
      });
      setMessage(response.message || "Password reset.");
      setResetTarget(null);
      setNewPassword("");
    } catch (err) {
      setResetError(err.message || "Could not reset the password.");
    } finally {
      setResetting(false);
    }
  }

  return (
    <div className="animate-fade-in space-y-6">
      <PageHeader
        eyebrow="Administration"
        title="User directory"
        subtitle="Create accounts, correct class details, reset passwords and deactivate access. Student records stay visible only to staff."
        actions={
          <button
            type="button"
            onClick={() => {
              setShowCreate((value) => !value);
              setEditing(null);
            }}
            className="btn-primary"
          >
            <Plus className="h-4 w-4" /> Add account
          </button>
        }
      />

      {message && <Alert tone="success">{message}</Alert>}
      {actionError && <Alert tone="error">{actionError}</Alert>}

      {showCreate && (
        <UserForm
          mode="create"
          initial={EMPTY_FORM}
          onClose={() => setShowCreate(false)}
          onSaved={async () => {
            setMessage("Account created.");
            await reload();
          }}
        />
      )}

      {editing && (
        <UserForm
          mode="edit"
          initial={{
            id: editing.id,
            name: editing.name || "",
            email: editing.email || "",
            role: editing.role || "student",
            class_level: String(editing.class_level || 1),
            section: editing.section || "A",
            roll_no: editing.roll_no || "",
            password: "",
          }}
          onClose={() => setEditing(null)}
          onSaved={async () => {
            setMessage("Account updated.");
            await reload();
          }}
        />
      )}

      {resetTarget && (
        <form onSubmit={resetPassword} className="card space-y-3 p-5">
          <SectionHeading
            title={`Reset password for ${resetTarget.name}`}
            subtitle="Share the new password with the account holder privately."
          />
          {resetError && <Alert tone="error">{resetError}</Alert>}
          <div className="flex flex-col gap-2 sm:flex-row">
            <input
              type="password"
              className="input flex-1"
              required
              minLength={8}
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              placeholder="New password (8+ characters, one number)"
            />
            <button type="submit" disabled={resetting} className="btn-primary">
              {resetting ? <Spinner className="h-4 w-4" /> : <KeyRound className="h-4 w-4" />}
              Reset password
            </button>
            <button
              type="button"
              onClick={() => {
                setResetTarget(null);
                setNewPassword("");
                setResetError("");
              }}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="card flex flex-col gap-3 p-4 lg:flex-row lg:items-center">
        <select
          value={role}
          onChange={(event) => setRole(event.target.value)}
          className="input lg:w-40"
          aria-label="Filter by role"
        >
          <option value="">All roles</option>
          <option value="student">Students</option>
          <option value="teacher">Teachers</option>
          <option value="admin">Administrators</option>
        </select>
        <select
          value={classLevel}
          onChange={(event) => setClassLevel(event.target.value)}
          className="input lg:w-40"
          aria-label="Filter by class"
        >
          <option value="">All classes</option>
          {CLASS_LEVELS.map((level) => (
            <option key={level} value={level}>
              Class {level}
            </option>
          ))}
        </select>
        <form onSubmit={applySearch} className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by name or email..."
            className="input pl-9"
          />
        </form>
        <span className="chip bg-surface-2 text-muted">
          <UserCog className="h-3.5 w-3.5" /> {data?.total ?? 0} accounts
        </span>
      </div>

      {error && <Alert tone="error">{error}</Alert>}

      {loading && !data ? (
        <SectionLoader label="Loading accounts..." />
      ) : users.length === 0 ? (
        <EmptyState
          icon={UserCog}
          title="No accounts match these filters"
          description="Try another role, class or search term."
        />
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-line">
              <thead className="bg-surface-2/60">
                <tr>
                  <th className="table-th">Account</th>
                  <th className="table-th">Role</th>
                  <th className="table-th">Class</th>
                  <th className="table-th">Quizzes</th>
                  <th className="table-th">Status</th>
                  <th className="table-th">Last login</th>
                  <th className="table-th" />
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {users.map((user) => (
                  <tr key={user.id} className="transition hover:bg-surface-2/40">
                    <td className="table-td">
                      <div className="flex items-center gap-2.5">
                        <Avatar name={user.name || "?"} size="sm" />
                        <div className="min-w-0">
                          <p className="truncate font-semibold text-ink">{user.name}</p>
                          <p className="truncate text-[10px] text-muted">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="table-td">
                      <span
                        className={`chip ${
                          user.role === "admin"
                            ? "bg-accent-50 text-accent-700 dark:bg-accent-500/15 dark:text-accent-200"
                            : user.role === "teacher"
                              ? "bg-primary-50 text-primary-700 dark:bg-primary-500/15 dark:text-primary-200"
                              : "bg-surface-2 text-muted"
                        }`}
                      >
                        {ROLE_LABELS[user.role] || user.role}
                      </span>
                    </td>
                    <td className="table-td text-muted">
                      {user.role === "student" ? classLevelLabel(user.class_level) : "—"}
                      {user.section ? `-${user.section}` : ""}
                    </td>
                    <td className="table-td text-muted">
                      {user.role === "student" ? user.attempts ?? 0 : "—"}
                    </td>
                    <td className="table-td">
                      <span
                        className={`chip ${
                          user.is_active
                            ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200"
                            : "bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-200"
                        }`}
                      >
                        {user.is_active ? "Active" : "Deactivated"}
                      </span>
                    </td>
                    <td className="table-td text-[11px] text-muted">
                      {user.last_login ? formatDate(user.last_login, { withTime: true }) : "Never"}
                    </td>
                    <td className="table-td">
                      <div className="flex flex-wrap justify-end gap-1.5">
                        <button
                          type="button"
                          onClick={() => {
                            setEditing(user);
                            setShowCreate(false);
                          }}
                          className="btn-ghost px-2 py-1 text-[11px]"
                        >
                          <Pencil className="h-3.5 w-3.5" /> Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setResetTarget(user);
                            setNewPassword("");
                            setResetError("");
                          }}
                          className="btn-ghost px-2 py-1 text-[11px]"
                        >
                          <KeyRound className="h-3.5 w-3.5" /> Password
                        </button>
                        <button
                          type="button"
                          disabled={busyId === user.id}
                          onClick={() => toggleActive(user)}
                          className={`btn-ghost px-2 py-1 text-[11px] ${
                            user.is_active
                              ? "text-rose-600 hover:bg-rose-50 dark:text-rose-300 dark:hover:bg-rose-500/15"
                              : "text-emerald-600 hover:bg-emerald-50 dark:text-emerald-300 dark:hover:bg-emerald-500/15"
                          }`}
                        >
                          {busyId === user.id ? (
                            <Spinner className="h-3.5 w-3.5" />
                          ) : user.is_active ? (
                            <UserX className="h-3.5 w-3.5" />
                          ) : (
                            <ShieldCheck className="h-3.5 w-3.5" />
                          )}
                          {user.is_active ? "Deactivate" : "Activate"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <p className="text-[11px] leading-relaxed text-muted">
        Deactivating an account blocks sign-in but keeps its learning history for staff review.
        Passwords are stored only as hashes.
      </p>
    </div>
  );
}
