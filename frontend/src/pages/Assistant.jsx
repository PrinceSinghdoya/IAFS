import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { ArrowUp, BookOpen, Lightbulb, RotateCcw, Sparkles, UserRound } from "lucide-react";

import Alert from "../components/Alert";
import { Spinner } from "../components/Loading";
import { PageHeader, SectionHeading } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";
import { CLASS_LEVELS, classLevelLabel } from "../lib/constants";
import { useApi, useDocumentTitle } from "../lib/useApi";

const STARTER = {
  role: "assistant",
  text:
    "Hi! I can explain a topic in a simpler way, show a worked example, or help you practise. I will not give away answers to a live quiz — tell me what you are learning and where you feel stuck.",
};

export default function Assistant() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const initialTopic = searchParams.get("topic") || "";
  const isStaff = user?.role === "teacher" || user?.role === "admin";

  const [classLevel, setClassLevel] = useState(user?.class_level || 1);
  const suggestionsQuery = useApi(
    `/assistant/suggestions${isStaff ? `?class_level=${classLevel}` : ""}`
  );
  const [topicSlug, setTopicSlug] = useState(initialTopic);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([STARTER]);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);

  useDocumentTitle("Learning assistant");

  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [messages, sending]);

  const topics = suggestionsQuery.data?.topics || [];
  const prompts = suggestionsQuery.data?.prompts || [];

  const activeTopic = useMemo(
    () => topics.find((topic) => topic.slug === topicSlug),
    [topics, topicSlug]
  );

  async function send(text) {
    const trimmed = (text || "").trim();
    if (!trimmed || sending) return;
    setError("");
    setMessages((current) => [...current, { role: "user", text: trimmed }]);
    setMessage("");
    setSending(true);
    try {
      const body = { message: trimmed };
      if (topicSlug) body.topic_slug = topicSlug;
      if (isStaff) body.class_level = Number(classLevel);
      const data = await api.post("/assistant/ask", body);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: data.answer,
          topicTitle: data.topic_title,
          suggestions: data.suggestions || [],
        },
      ]);
    } catch (err) {
      setError(err.message || "The assistant could not answer. Please try again.");
    } finally {
      setSending(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    send(message);
  }

  return (
    <div className="animate-fade-in space-y-6">
      <PageHeader
        eyebrow="Class-aware help"
        title="Learning assistant"
        subtitle={
          isStaff
            ? "Preview how the assistant explains a topic for any class. It teaches the method, never the live quiz answer."
            : `Explanations written for ${classLevelLabel(user?.class_level)}. It teaches the method, never the live quiz answer.`
        }
        actions={
          isStaff ? (
            <select
              value={classLevel}
              onChange={(event) => setClassLevel(Number(event.target.value))}
              className="input w-auto"
              aria-label="Preview class"
            >
              {CLASS_LEVELS.map((level) => (
                <option key={level} value={level}>
                  Preview Class {level}
                </option>
              ))}
            </select>
          ) : (
            <button
              type="button"
              onClick={() => {
                setMessages([STARTER]);
                setError("");
              }}
              className="btn-secondary"
            >
              <RotateCcw className="h-4 w-4" /> New chat
            </button>
          )
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <section className="card flex min-h-[560px] flex-col overflow-hidden lg:col-span-2">
          <div className="flex items-center gap-2 border-b border-line px-4 py-3">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-accent-500 to-primary-500 text-white">
              <Sparkles className="h-4 w-4" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-bold text-ink">IAFS learning assistant</p>
              <p className="truncate text-[11px] text-muted">
                {activeTopic
                  ? `Topic: ${activeTopic.title}`
                  : isStaff
                    ? `Class ${classLevel} · staff preview`
                    : "Ask about any English or Mathematics topic"}
              </p>
            </div>
            {activeTopic && (
              <button
                type="button"
                onClick={() => setTopicSlug("")}
                className="chip bg-surface-2 text-muted hover:text-ink"
              >
                Clear topic
              </button>
            )}
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto px-4 py-4">
            {messages.map((item, index) => (
              <div
                key={index}
                className={`flex gap-2.5 ${item.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {item.role === "assistant" && (
                  <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent-50 text-accent-600 dark:bg-accent-500/15 dark:text-accent-300">
                    <Sparkles className="h-3.5 w-3.5" />
                  </span>
                )}
                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
                    item.role === "user"
                      ? "rounded-br-md bg-primary-600 text-white"
                      : "rounded-bl-md border border-line bg-surface-2/60 text-ink"
                  }`}
                >
                  {item.topicTitle && item.role === "assistant" && (
                    <p className="mb-1 inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide text-primary-600 dark:text-primary-300">
                      <BookOpen className="h-3 w-3" />
                      {item.topicTitle}
                    </p>
                  )}
                  <p className="assistant-answer whitespace-pre-line">{item.text}</p>
                  {item.suggestions?.length > 0 && (
                    <div className="mt-2.5 flex flex-wrap gap-1.5">
                      {item.suggestions.map((suggestion) => (
                        <button
                          key={suggestion}
                          type="button"
                          onClick={() => send(suggestion)}
                          className="rounded-full border border-line bg-surface px-2.5 py-1 text-[10px] font-semibold text-muted transition hover:border-primary-300 hover:text-ink"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {item.role === "user" && (
                  <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-200">
                    <UserRound className="h-3.5 w-3.5" />
                  </span>
                )}
              </div>
            ))}

            {sending && (
              <div className="flex items-center gap-2 text-xs font-medium text-muted">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-accent-50 dark:bg-accent-500/15">
                  <Spinner className="h-3.5 w-3.5 text-accent-600 dark:text-accent-300" />
                </span>
                Thinking about the simplest way to explain it...
              </div>
            )}
            <div ref={endRef} />
          </div>

          <form onSubmit={handleSubmit} className="border-t border-line p-3">
            {error && (
              <div className="mb-2">
                <Alert tone="error">{error}</Alert>
              </div>
            )}
            <div className="flex items-end gap-2">
              <textarea
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    send(message);
                  }
                }}
                rows={2}
                maxLength={500}
                placeholder="For example: I do not understand how to compare fractions"
                className="input min-h-[46px] flex-1 resize-none py-2.5"
              />
              <button
                type="submit"
                disabled={sending || !message.trim()}
                className="btn-primary h-[46px] w-[46px] shrink-0 p-0"
                aria-label="Send question"
              >
                {sending ? <Spinner className="h-4 w-4" /> : <ArrowUp className="h-4 w-4" />}
              </button>
            </div>
            <p className="mt-1.5 text-[10px] text-muted">
              Press Enter to send, Shift+Enter for a new line. Questions are private to you.
            </p>
          </form>
        </section>

        <div className="space-y-6">
          <section className="card p-5">
            <SectionHeading
              title="Try a prompt"
              subtitle={suggestionsQuery.data ? `Ideas for Class ${suggestionsQuery.data.class_level}` : "Quick questions"}
              icon={Lightbulb}
            />
            <div className="space-y-2">
              {prompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => send(prompt)}
                  className="w-full rounded-xl border border-line bg-surface-2/40 px-3 py-2 text-left text-xs font-medium text-ink transition hover:border-primary-300 hover:bg-surface-2"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </section>

          <section className="card p-5">
            <SectionHeading title="Focus a topic" subtitle="Optional: keeps the answer relevant" />
            <div className="flex flex-wrap gap-1.5">
              {topics.map((topic) => (
                <button
                  key={topic.slug}
                  type="button"
                  onClick={() => setTopicSlug(topic.slug === topicSlug ? "" : topic.slug)}
                  className={`chip border transition ${
                    topic.slug === topicSlug
                      ? "border-primary-300 bg-primary-50 text-primary-700 dark:border-primary-400/40 dark:bg-primary-500/15 dark:text-primary-200"
                      : "border-line bg-surface-2/40 text-muted hover:text-ink"
                  }`}
                >
                  {topic.title}
                </button>
              ))}
            </div>
          </section>

          <section className="card border-dashed p-5">
            <SectionHeading title="How it works" />
            <ul className="space-y-2 text-[11px] leading-relaxed text-muted">
              <li>• Answers use the same curriculum as your lessons and quizzes.</li>
              <li>• Primary answers use simpler words and shorter steps.</li>
              <li>• It explains the method and gives a different example — it never reveals a live quiz answer.</li>
              <li>• No paid AI service is called; everything runs from the local school knowledge base.</li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
}
