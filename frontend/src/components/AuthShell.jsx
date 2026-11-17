import { BookOpenCheck, CameraOff, Sparkles, TrendingUp } from "lucide-react";

import Logo from "./Logo";
import ThemeToggle from "./ThemeToggle";

const FEATURES = [
  {
    icon: Sparkles,
    title: "Lessons that fit the class",
    text: "Every English and Mathematics topic is written for Classes 1-5 or 6-10, with examples and practice.",
  },
  {
    icon: TrendingUp,
    title: "Quizzes that adapt",
    text: "Questions get easier after a mistake and harder after success. Feedback comes from your real scores.",
  },
  {
    icon: CameraOff,
    title: "Private by design",
    text: "The camera check is optional and off by default. No images, video or personal data are stored.",
  },
];

/** Split-screen shell shared by the login and registration pages. */
export default function AuthShell({ children }) {
  return (
    <div className="min-h-screen bg-canvas lg:grid lg:grid-cols-[1.05fr_1fr]">
      <aside className="relative flex flex-col overflow-hidden bg-gradient-to-br from-primary-800 via-indigo-700 to-accent-700 px-6 py-8 text-white sm:px-10 lg:justify-between lg:px-14 lg:py-12">
        <div
          className="pointer-events-none absolute inset-0 opacity-30"
          style={{
            backgroundImage:
              "radial-gradient(circle at 20% 15%, rgba(255,255,255,0.35), transparent 22rem), radial-gradient(circle at 85% 80%, rgba(253,230,138,0.35), transparent 18rem)",
          }}
        />

        <div className="relative">
          <Logo variant="light" to="/login" showTagline />
          <span className="mt-6 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-blue-100 ring-1 ring-white/15">
            <BookOpenCheck className="h-3.5 w-3.5" />
            Classes 1-10 · English &amp; Mathematics
          </span>
          <h1 className="mt-5 max-w-lg text-3xl font-extrabold leading-tight tracking-tight sm:text-4xl">
            Learning that adapts to every child.
          </h1>
          <p className="mt-3 max-w-md text-sm leading-relaxed text-blue-100 sm:text-[15px]">
            Simple lessons, friendly practice and honest progress for primary and secondary
            students — with a teacher view that is built from real class data.
          </p>
        </div>

        <div className="relative mt-8 grid gap-3 sm:grid-cols-3 lg:mt-10">
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="rounded-2xl border border-white/15 bg-white/10 p-3.5 backdrop-blur-sm"
              >
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/15">
                  <Icon className="h-5 w-5 text-sun-200" />
                </span>
                <p className="mt-2.5 text-xs font-bold">{feature.title}</p>
                <p className="mt-1 text-[11px] leading-relaxed text-blue-100">{feature.text}</p>
              </div>
            );
          })}
        </div>

        <p className="relative mt-6 text-[11px] leading-relaxed text-blue-200">
          Demo accounts use fictional names only. No real children&apos;s data, photos or
          videos are stored anywhere in this project.
        </p>
      </aside>

      <main className="relative flex min-h-screen flex-col bg-canvas">
        <div className="flex items-center justify-between px-5 py-4 sm:px-8">
          <span className="text-xs font-semibold uppercase tracking-[0.14em] text-muted lg:hidden">
            IAFS School Learning
          </span>
          <span className="hidden lg:block" />
          <ThemeToggle />
        </div>
        <div className="flex flex-1 items-center justify-center px-4 pb-10 pt-2 sm:px-8">
          <div className="w-full max-w-md">{children}</div>
        </div>
      </main>
    </div>
  );
}
