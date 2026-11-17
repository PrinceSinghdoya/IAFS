import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { LogOut, Menu, X } from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { ROLE_LABELS, classLevelLabel, navForRole, pageTitle } from "../lib/constants";
import { initials } from "../lib/format";
import Logo from "./Logo";
import ThemeToggle from "./ThemeToggle";

function SidebarContent({ onNavigate }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const navItems = navForRole(user?.role);
  const home = user?.role === "admin" ? "/admin" : user?.role === "teacher" ? "/teacher" : "/student";

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex h-16 items-center justify-between border-b border-line px-5">
        <Logo variant="dark" to={home} />
        <ThemeToggle compact className="sm:hidden" />
      </div>

      <nav className="flex-1 space-y-5 overflow-y-auto px-3 py-5">
        {navItems.map((group) => (
          <div key={group.group}>
            <p className="mb-1.5 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-muted">
              {group.group}
            </p>
            <div className="space-y-0.5">
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    onClick={onNavigate}
                    className={({ isActive }) =>
                      `sidebar-link ${isActive ? "sidebar-link-active" : ""}`
                    }
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    <span className="truncate">{item.label}</span>
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-line p-3">
        <div className="flex items-center gap-3 rounded-xl bg-surface-2/70 px-3 py-2.5">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-accent-500 text-[11px] font-bold text-white">
            {initials(user?.name || "?")}
          </span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-bold text-ink">{user?.name}</p>
            <p className="truncate text-[10px] text-muted">
              {ROLE_LABELS[user?.role] || "User"}
              {user?.class_level ? ` · ${classLevelLabel(user.class_level)}` : ""}
            </p>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            title="Log out"
            aria-label="Log out"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-muted transition hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-500/15 dark:hover:text-rose-300"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

/** App shell: fixed sidebar on desktop, slide-over drawer on mobile. */
export default function AppLayout() {
  const { user } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Close the drawer whenever the route changes.
  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-canvas">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-line bg-surface lg:block">
        <SidebarContent />
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Close navigation"
            className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="absolute inset-y-0 left-0 w-72 max-w-[85%] border-r border-line bg-surface shadow-2xl">
            <SidebarContent onNavigate={() => setMobileOpen(false)} />
          </aside>
        </div>
      )}

      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 border-b border-line bg-surface/85 backdrop-blur">
          <div className="flex h-16 items-center gap-3 px-4 sm:px-6">
            <button
              type="button"
              onClick={() => setMobileOpen(true)}
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-line text-muted transition hover:bg-surface-2 hover:text-ink lg:hidden"
              aria-label="Open navigation"
            >
              {mobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </button>

            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-bold text-ink">{pageTitle(location.pathname)}</p>
              <p className="hidden truncate text-[11px] text-muted sm:block">
                {user?.class_level
                  ? `${classLevelLabel(user.class_level)} · English and Mathematics`
                  : "IAFS School Learning · English and Mathematics"}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="hidden rounded-full border border-line bg-surface-2/60 px-3 py-1 text-[11px] font-semibold text-muted sm:inline">
                {ROLE_LABELS[user?.role] || "Guest"}
              </span>
              <ThemeToggle />
            </div>
          </div>
        </header>

        <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
