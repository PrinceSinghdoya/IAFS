import {
  AlignLeft,
  ArrowLeftRight,
  ArrowUpDown,
  BarChart3,
  Blocks,
  BookMarked,
  BookOpen,
  BookOpenCheck,
  Camera,
  CheckCheck,
  CirclePercent,
  ClipboardList,
  Clock3,
  Compass,
  Divide,
  Equal,
  GraduationCap,
  Hash,
  Layers,
  LayoutDashboard,
  Library,
  MessageCircle,
  MessagesSquare,
  Minus,
  PenLine,
  PenTool,
  Percent,
  PieChart,
  Plus,
  Quote,
  Scale,
  School,
  Shapes,
  Sparkles,
  SpellCheck,
  SpellCheck2,
  TrendingUp,
  Type,
  UserCog,
  Users,
  Variable,
  Waves,
  X,
} from "lucide-react";

export const CLASS_LEVELS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
export const PRIMARY_CLASSES = [1, 2, 3, 4, 5];
export const SECONDARY_CLASSES = [6, 7, 8, 9, 10];

export function classLevelLabel(level) {
  return level ? `Class ${level}` : "No class";
}

/** Topic icon names come from the backend and map to lucide components. */
export const TOPIC_ICONS = {
  AlignLeft,
  ArrowLeftRight,
  ArrowUpDown,
  BarChart3,
  Blocks,
  BookMarked,
  BookOpen,
  BookOpenCheck,
  CheckCheck,
  Clock3,
  Compass,
  Divide,
  Equal,
  Hash,
  Library,
  Minus,
  PenLine,
  PenTool,
  Percent,
  PercentCircle: CirclePercent,
  PieChart,
  Plus,
  Quote,
  Scale,
  Shapes,
  SpellCheck,
  SpellCheck2,
  Type,
  Users,
  Variable,
  Waves,
  X,
};

export function topicIcon(name) {
  return TOPIC_ICONS[name] || BookOpen;
}

/** Soft colour palettes that stay readable in light and dark mode. */
export const TOPIC_TONES = [
  {
    soft: "bg-blue-50 text-blue-700 dark:bg-blue-500/15 dark:text-blue-200",
    border: "border-blue-100 dark:border-blue-400/20",
    bar: "bg-blue-500",
  },
  {
    soft: "bg-violet-50 text-violet-700 dark:bg-violet-500/15 dark:text-violet-200",
    border: "border-violet-100 dark:border-violet-400/20",
    bar: "bg-violet-500",
  },
  {
    soft: "bg-amber-50 text-amber-700 dark:bg-amber-500/15 dark:text-amber-200",
    border: "border-amber-100 dark:border-amber-400/20",
    bar: "bg-amber-500",
  },
  {
    soft: "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200",
    border: "border-emerald-100 dark:border-emerald-400/20",
    bar: "bg-emerald-500",
  },
  {
    soft: "bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-200",
    border: "border-rose-100 dark:border-rose-400/20",
    bar: "bg-rose-500",
  },
  {
    soft: "bg-cyan-50 text-cyan-700 dark:bg-cyan-500/15 dark:text-cyan-200",
    border: "border-cyan-100 dark:border-cyan-400/20",
    bar: "bg-cyan-500",
  },
];

export function topicTone(index = 0) {
  return TOPIC_TONES[Math.abs(Number(index) || 0) % TOPIC_TONES.length];
}

export const SUBJECT_STYLES = {
  English: {
    emoji: "📖",
    icon: BookOpen,
    gradient: "from-violet-500 via-purple-500 to-fuchsia-500",
    soft: "bg-violet-50 text-violet-700 dark:bg-violet-500/15 dark:text-violet-200",
    solid: "bg-violet-600",
    bar: "bg-violet-500",
    border: "border-violet-200 dark:border-violet-400/25",
  },
  Mathematics: {
    emoji: "🔢",
    icon: CirclePercent,
    gradient: "from-blue-500 via-sky-500 to-cyan-500",
    soft: "bg-blue-50 text-blue-700 dark:bg-blue-500/15 dark:text-blue-200",
    solid: "bg-blue-600",
    bar: "bg-blue-500",
    border: "border-blue-200 dark:border-blue-400/25",
  },
};

export function subjectStyle(name) {
  return SUBJECT_STYLES[name] || SUBJECT_STYLES.Mathematics;
}

/**
 * Feedback categories are shared by the badge, the cards and the result page.
 * Keep one object per category so every surface uses the same colours.
 */
export const CATEGORY_STYLES = {
  "Getting Started": {
    badge: "bg-slate-100 text-slate-700 dark:bg-slate-700/50 dark:text-slate-200",
    soft: "bg-slate-50 border-slate-200 text-slate-800 dark:bg-slate-500/10 dark:border-slate-400/20 dark:text-slate-100",
    bar: "bg-slate-400",
    text: "text-slate-700 dark:text-slate-200",
    gradient: "from-slate-500 to-slate-700",
  },
  "Needs Improvement": {
    badge: "bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-200",
    soft: "bg-rose-50 border-rose-200 text-rose-900 dark:bg-rose-500/10 dark:border-rose-400/20 dark:text-rose-100",
    bar: "bg-rose-500",
    text: "text-rose-700 dark:text-rose-200",
    gradient: "from-rose-500 to-orange-500",
  },
  "Needs Practice": {
    badge: "bg-amber-50 text-amber-800 dark:bg-amber-500/15 dark:text-amber-200",
    soft: "bg-amber-50 border-amber-200 text-amber-900 dark:bg-amber-500/10 dark:border-amber-400/20 dark:text-amber-100",
    bar: "bg-amber-500",
    text: "text-amber-700 dark:text-amber-200",
    gradient: "from-amber-400 to-orange-500",
  },
  "Good Progress": {
    badge: "bg-blue-50 text-blue-700 dark:bg-blue-500/15 dark:text-blue-200",
    soft: "bg-blue-50 border-blue-200 text-blue-900 dark:bg-blue-500/10 dark:border-blue-400/20 dark:text-blue-100",
    bar: "bg-blue-500",
    text: "text-blue-700 dark:text-blue-200",
    gradient: "from-blue-500 to-cyan-500",
  },
  "Excellent Performance": {
    badge: "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200",
    soft: "bg-emerald-50 border-emerald-200 text-emerald-900 dark:bg-emerald-500/10 dark:border-emerald-400/20 dark:text-emerald-100",
    bar: "bg-emerald-500",
    text: "text-emerald-700 dark:text-emerald-200",
    gradient: "from-emerald-500 to-teal-500",
  },
};

export function categoryStyle(category) {
  return CATEGORY_STYLES[category] || CATEGORY_STYLES["Getting Started"];
}

export const DIFFICULTY_STYLES = {
  easy: "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200",
  medium: "bg-amber-50 text-amber-800 dark:bg-amber-500/15 dark:text-amber-200",
  hard: "bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-200",
};

export const STATUS_STYLES = {
  "Not started":
    "bg-slate-100 text-slate-600 dark:bg-slate-700/50 dark:text-slate-300",
  Strong:
    "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200",
  Practising:
    "bg-blue-50 text-blue-700 dark:bg-blue-500/15 dark:text-blue-200",
  "Needs review":
    "bg-amber-50 text-amber-800 dark:bg-amber-500/15 dark:text-amber-200",
  "Needs attention":
    "bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-200",
  "On track":
    "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200",
  "Not attempted":
    "bg-slate-100 text-slate-600 dark:bg-slate-700/50 dark:text-slate-300",
  online:
    "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200",
  offline:
    "bg-slate-100 text-slate-600 dark:bg-slate-700/50 dark:text-slate-300",
};

export const SENTIMENT_STYLES = {
  Positive:
    "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200",
  Neutral: "bg-slate-100 text-slate-700 dark:bg-slate-700/50 dark:text-slate-200",
  Negative: "bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-200",
};

export const TREND_LABELS = {
  improving: { label: "Improving", tone: "text-emerald-600 dark:text-emerald-300" },
  steady: { label: "Steady", tone: "text-blue-600 dark:text-blue-300" },
  slipping: { label: "Needs a push", tone: "text-amber-600 dark:text-amber-300" },
};

export const NAV_BY_ROLE = {
  student: [
    {
      group: "Learn",
      items: [
        { label: "Dashboard", to: "/student", icon: LayoutDashboard, end: true },
        { label: "Subjects", to: "/subjects", icon: BookOpen },
        { label: "Learning assistant", to: "/assistant", icon: Sparkles },
      ],
    },
    {
      group: "My learning",
      items: [
        { label: "My progress", to: "/progress", icon: TrendingUp },
        { label: "Feedback", to: "/feedback", icon: MessageCircle },
      ],
    },
    {
      group: "Class",
      items: [
        { label: "Class chat", to: "/chat", icon: MessagesSquare },
        { label: "Focus check", to: "/camera", icon: Camera },
      ],
    },
  ],
  teacher: [
    {
      group: "Teaching",
      items: [
        { label: "Overview", to: "/teacher", icon: LayoutDashboard, end: true },
        { label: "Students", to: "/teacher/students", icon: Users },
        { label: "Classes", to: "/teacher/classes", icon: School },
      ],
    },
    {
      group: "Support",
      items: [
        { label: "Learning assistant", to: "/assistant", icon: Sparkles },
        { label: "Class chat", to: "/chat", icon: MessagesSquare },
      ],
    },
  ],
  admin: [
    {
      group: "Administration",
      items: [
        { label: "Overview", to: "/admin", icon: LayoutDashboard, end: true },
        { label: "User directory", to: "/admin/users", icon: UserCog },
        { label: "Classes & subjects", to: "/admin/classes-subjects", icon: Layers },
      ],
    },
    {
      group: "Support",
      items: [
        { label: "Teacher overview", to: "/teacher", icon: GraduationCap },
        { label: "Learning assistant", to: "/assistant", icon: Sparkles },
      ],
    },
  ],
};

export function navForRole(role) {
  return NAV_BY_ROLE[role] || NAV_BY_ROLE.student;
}

export const ROLE_LABELS = {
  student: "Student",
  teacher: "Teacher",
  admin: "Administrator",
};

const PAGE_TITLES = [
  ["/student", "Dashboard"],
  ["/subjects", "Subjects"],
  ["/topics/", "Topic lesson"],
  ["/quiz/", "Adaptive quiz"],
  ["/results/", "Quiz result"],
  ["/assistant", "Learning assistant"],
  ["/progress", "My progress"],
  ["/feedback", "Adaptive feedback"],
  ["/chat", "Class chat"],
  ["/camera", "Focus check"],
  ["/teacher/students/", "Student report"],
  ["/teacher/students", "Students"],
  ["/teacher/classes", "Classes"],
  ["/teacher", "Teacher overview"],
  ["/admin/users", "User directory"],
  ["/admin/classes-subjects", "Classes & subjects"],
  ["/admin", "Administrator overview"],
];

export function pageTitle(pathname = "") {
  const match = PAGE_TITLES.find(([path]) =>
    path.endsWith("/") ? pathname.startsWith(path) : pathname === path
  );
  return match ? match[1] : "IAFS School Learning";
}
