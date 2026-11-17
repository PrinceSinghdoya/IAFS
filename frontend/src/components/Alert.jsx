import { AlertCircle, CheckCircle2, Info } from "lucide-react";

const STYLES = {
  error: {
    wrapper:
      "border-rose-200 bg-rose-50 text-rose-800 dark:border-rose-400/30 dark:bg-rose-500/10 dark:text-rose-100",
    Icon: AlertCircle,
    iconColor: "text-rose-500 dark:text-rose-300",
  },
  success: {
    wrapper:
      "border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-400/30 dark:bg-emerald-500/10 dark:text-emerald-100",
    Icon: CheckCircle2,
    iconColor: "text-emerald-500 dark:text-emerald-300",
  },
  info: {
    wrapper:
      "border-blue-200 bg-blue-50 text-blue-800 dark:border-blue-400/30 dark:bg-blue-500/10 dark:text-blue-100",
    Icon: Info,
    iconColor: "text-blue-500 dark:text-blue-300",
  },
};

/** Small inline alert used for form and API errors. */
export default function Alert({ tone = "error", title, children, className = "" }) {
  const style = STYLES[tone] || STYLES.info;
  const Icon = style.Icon;

  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      className={`flex gap-3 rounded-xl border px-4 py-3 text-sm ${style.wrapper} ${className}`}
    >
      <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${style.iconColor}`} />
      <div>
        {title && <p className="font-semibold">{title}</p>}
        <div className={title ? "mt-0.5" : ""}>{children}</div>
      </div>
    </div>
  );
}
