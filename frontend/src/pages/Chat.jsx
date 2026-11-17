import { useCallback, useEffect, useRef, useState } from "react";
import {
  ArrowUp,
  Info,
  MessageCircle,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import Alert from "../components/Alert";
import { SectionLoader, Spinner } from "../components/Loading";
import { EmptyState, PageHeader, SentimentPill } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";
import { CLASS_LEVELS, classLevelLabel } from "../lib/constants";
import { formatTime, initials } from "../lib/format";

const EXAMPLES = [
  "I do not understand how to compare fractions.",
  "I understood the lesson today.",
  "Can someone explain number patterns?",
];

function mergeMessages(current, incoming) {
  const seen = new Set(current.map((message) => message.id));
  return [...current, ...incoming.filter((message) => !seen.has(message.id))];
}

export default function Chat() {
  const { user } = useAuth();
  const isStaff = user?.role === "teacher" || user?.role === "admin";

  const [messages, setMessages] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [classFilter, setClassFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState("");

  const scrollRef = useRef(null);
  const textareaRef = useRef(null);

  const messagesPath = isStaff && classFilter ? `/chat/messages?class_level=${classFilter}` : "/chat/messages";

  const loadMessages = useCallback(
    async (replace = false) => {
      const data = await api.get(messagesPath);
      setMessages((current) =>
        replace ? data.messages : mergeMessages(current, data.messages)
      );
      return data;
    },
    [messagesPath]
  );

  const loadAnalysis = useCallback(async () => {
    if (isStaff) return;
    try {
      const data = await api.get("/chat/my-analysis");
      setAnalysis(data);
    } catch {
      // The private summary is non-critical.
    }
  }, [isStaff]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");

    loadMessages(true)
      .catch((err) => {
        if (active) setError(err.message || "Could not load class chat.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    loadAnalysis();
    const interval = setInterval(() => {
      loadMessages(false).catch(() => {});
    }, 8000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [loadMessages, loadAnalysis]);

  useEffect(() => {
    const element = scrollRef.current;
    if (element) element.scrollTop = element.scrollHeight;
  }, [messages.length]);

  async function handleSend(event) {
    event?.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || sending) return;

    setSending(true);
    setSendError("");
    try {
      const body = { text: trimmed };
      if (isStaff && classFilter) body.class_level = Number(classFilter);
      const data = await api.post("/chat/messages", body);
      setMessages((current) => mergeMessages(current, [data.message]));
      setText("");
      await loadAnalysis();
      textareaRef.current?.focus();
    } catch (err) {
      setSendError(err.message || "Could not send the message.");
    } finally {
      setSending(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }

  if (loading && messages.length === 0) {
    return <SectionLoader label="Loading class chat..." />;
  }

  return (
    <div className="animate-fade-in space-y-5">
      <PageHeader
        eyebrow="Class chat"
        title={isStaff ? "Classroom conversation" : "Ask your class a question"}
        subtitle="A calm, class-only space to ask about English or Mathematics. Teachers can reply and see the class conversation."
        actions={
          <div className="flex items-center gap-2">
            {isStaff && (
              <select
                value={classFilter}
                onChange={(event) => setClassFilter(event.target.value)}
                className="input w-auto py-2 text-xs"
                aria-label="Filter class chat"
              >
                <option value="">Whole school notices</option>
                {CLASS_LEVELS.map((level) => (
                  <option key={level} value={level}>
                    Class {level}
                  </option>
                ))}
              </select>
            )}
            <span className="chip bg-surface-2 text-muted">
              <RefreshCw className="h-3.5 w-3.5" /> Auto-refresh
            </span>
          </div>
        }
      />

      {error && <Alert tone="error">{error}</Alert>}

      <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
        <div className="card flex h-[600px] min-h-[460px] flex-col overflow-hidden">
          <div className="flex items-center justify-between gap-3 border-b border-line px-4 py-3">
            <div className="flex items-center gap-2.5">
              <span className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-primary-50 text-primary-600 dark:bg-primary-500/15 dark:text-primary-300">
                <MessageCircle className="h-[18px] w-[18px]" />
                <span className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full border-2 border-surface bg-emerald-500" />
              </span>
              <div>
                <p className="text-sm font-bold text-ink">
                  {isStaff
                    ? classFilter
                      ? classLevelLabel(Number(classFilter))
                      : "Whole school"
                    : classLevelLabel(user?.class_level)}
                </p>
                <p className="text-[11px] text-muted">
                  {messages.length} message{messages.length === 1 ? "" : "s"} · class channel
                </p>
              </div>
            </div>
            <span className="hidden text-[10px] text-muted sm:block">
              Be kind and keep personal details private
            </span>
          </div>

          <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto bg-surface-2/30 px-4 py-4">
            {messages.length === 0 ? (
              <EmptyState
                icon={MessageCircle}
                title="No messages yet"
                description="Start with a question about the topic you are learning."
              />
            ) : (
              messages.map((message) => {
                const isOwn = message.student_id === user?.id;
                const isTeacher = message.is_teacher;
                const needsHelp = message.analysis?.learning_difficulty === "Possible";
                return (
                  <div
                    key={message.id}
                    className={`flex items-start gap-2.5 ${isOwn ? "flex-row-reverse" : ""}`}
                  >
                    <span
                      className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-[10px] font-bold text-white ${
                        isTeacher
                          ? "bg-gradient-to-br from-accent-500 to-accent-700"
                          : isOwn
                            ? "bg-gradient-to-br from-primary-500 to-primary-700"
                            : "bg-slate-400 dark:bg-slate-600"
                      }`}
                    >
                      {initials(message.student_name)}
                    </span>

                    <div className={`flex max-w-[85%] flex-col sm:max-w-[75%] ${isOwn ? "items-end" : ""}`}>
                      <div
                        className={`mb-1 flex flex-wrap items-center gap-1.5 text-[10px] ${
                          isOwn ? "justify-end" : ""
                        }`}
                      >
                        <span className="font-semibold text-ink/80">
                          {isOwn ? "You" : message.student_name}
                        </span>
                        {isTeacher && (
                          <span className="chip bg-accent-50 px-1.5 py-0 text-[9px] text-accent-700 dark:bg-accent-500/15 dark:text-accent-200">
                            Teacher
                          </span>
                        )}
                        <span className="text-muted">{formatTime(message.created_at)}</span>
                      </div>

                      <div
                        className={`rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
                          isTeacher
                            ? "rounded-tl-sm border border-accent-200 bg-accent-50 text-ink dark:border-accent-400/25 dark:bg-accent-500/10"
                            : isOwn
                              ? "rounded-tr-sm bg-primary-600 text-white"
                              : "rounded-tl-sm border border-line bg-surface text-ink"
                        }`}
                      >
                        {message.text}
                      </div>

                      {!isTeacher && message.analysis && (
                        <div className={`mt-1.5 flex flex-wrap gap-1 ${isOwn ? "justify-end" : ""}`}>
                          <SentimentPill sentiment={message.analysis.sentiment} />
                          {needsHelp && (
                            <span className="chip bg-amber-50 text-amber-800 dark:bg-amber-500/15 dark:text-amber-200">
                              Needs help
                            </span>
                          )}
                          {message.analysis.subtopic && (
                            <span className="chip bg-violet-50 text-violet-700 dark:bg-violet-500/15 dark:text-violet-200">
                              {message.analysis.subtopic}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          <form onSubmit={handleSend} className="border-t border-line bg-surface p-3 sm:p-4">
            {sendError && <p className="mb-2 text-xs font-medium text-rose-600 dark:text-rose-300">{sendError}</p>}
            <div className="flex items-end gap-2">
              <div className="relative flex-1">
                <textarea
                  ref={textareaRef}
                  value={text}
                  onChange={(event) => setText(event.target.value.slice(0, 600))}
                  onKeyDown={handleKeyDown}
                  rows={2}
                  placeholder={
                    isStaff
                      ? "Reply to your class..."
                      : "Ask a question, for example: I do not understand fractions."
                  }
                  className="input resize-none py-2.5 pr-14"
                  aria-label="Chat message"
                />
                <span className="pointer-events-none absolute bottom-2 right-3 text-[10px] text-muted">
                  {text.length}/600
                </span>
              </div>
              <button
                type="submit"
                disabled={!text.trim() || sending}
                className="btn-primary h-[42px] w-[42px] shrink-0 rounded-xl p-0"
                aria-label="Send message"
              >
                {sending ? <Spinner className="h-4 w-4" /> : <ArrowUp className="h-5 w-5" />}
              </button>
            </div>
            <p className="mt-1.5 text-[10px] text-muted">
              Enter to send · Shift + Enter for a new line · Visible to your class only
            </p>
          </form>
        </div>

        <aside className="space-y-5">
          <div className="card p-5">
            <h2 className="inline-flex items-center gap-2 text-sm font-bold text-ink">
              <Sparkles className="h-4 w-4 text-accent-600 dark:text-accent-300" />
              How the text signal works
            </h2>
            <ol className="mt-3 space-y-2.5">
              {[
                "A small rule-based analyser reads the words you use.",
                "Phrases such as “not understanding” mark a possible help request.",
                "A topic name in your message links it to the curriculum.",
                "The signal can support your feedback, but never changes a quiz score.",
              ].map((step, index) => (
                <li key={step} className="flex gap-2.5 text-[11px] leading-relaxed text-muted">
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-surface-2 text-[10px] font-bold text-ink">
                    {index + 1}
                  </span>
                  {step}
                </li>
              ))}
            </ol>
            <div className="mt-4 space-y-2">
              {EXAMPLES.map((example) => (
                <button
                  key={example}
                  type="button"
                  onClick={() => {
                    setText(example);
                    textareaRef.current?.focus();
                  }}
                  className="w-full rounded-lg border border-line bg-surface-2/40 px-3 py-2 text-left text-[11px] italic text-muted transition hover:border-primary-300 hover:text-ink"
                >
                  “{example}”
                </button>
              ))}
            </div>
          </div>

          {!isStaff && (
            <div className="card p-5">
              <h2 className="text-sm font-bold text-ink">Your private signals</h2>
              {analysis && analysis.messages_analyzed > 0 ? (
                <>
                  <div className="mt-3 grid grid-cols-2 gap-2 text-center">
                    <div className="rounded-lg bg-surface-2 px-2 py-2">
                      <p className="text-lg font-bold text-ink">{analysis.messages_analyzed}</p>
                      <p className="text-[9px] font-semibold uppercase text-muted">Messages</p>
                    </div>
                    <div className="rounded-lg bg-surface-2 px-2 py-2">
                      <p className="text-lg font-bold text-ink">{analysis.difficulty_signals}</p>
                      <p className="text-[9px] font-semibold uppercase text-muted">Help signals</p>
                    </div>
                  </div>
                  {analysis.topics.length > 0 && (
                    <div className="mt-3">
                      <p className="text-[10px] font-semibold uppercase tracking-wide text-muted">
                        Topics mentioned
                      </p>
                      <div className="mt-1.5 flex flex-wrap gap-1.5">
                        {analysis.topics.map((topic) => (
                          <span
                            key={topic}
                            className="chip bg-violet-50 text-violet-700 dark:bg-violet-500/15 dark:text-violet-200"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  <p className="mt-3 text-[10px] leading-relaxed text-muted">{analysis.note}</p>
                </>
              ) : (
                <p className="mt-2 text-xs leading-relaxed text-muted">
                  Send a question to see a short, private summary here.
                </p>
              )}
            </div>
          )}

          <div className="card p-4">
            <p className="flex items-center gap-1.5 text-[11px] font-bold text-ink">
              <ShieldCheck className="h-4 w-4 text-emerald-500 dark:text-emerald-400" />
              Responsible use
            </p>
            <p className="mt-1.5 text-[11px] leading-relaxed text-muted">
              Sentiment is a rough word-pattern signal, not a diagnosis of anyone&apos;s emotions.
              Teachers use it only to offer support.
            </p>
          </div>

          <div className="flex items-start gap-2 rounded-xl bg-surface-2 px-3 py-2.5 text-[10px] leading-relaxed text-muted">
            <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
            This is a learning space. Be respectful and do not share personal information.
          </div>
        </aside>
      </div>
    </div>
  );
}
