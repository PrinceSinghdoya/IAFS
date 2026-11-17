import { CheckCircle2, Lightbulb, XCircle } from "lucide-react";

import { DifficultyPill } from "./ui";

/**
 * Answer-by-answer review for a completed quiz.
 * The API returns `selected_index`, `correct_index`, `explanation` and
 * `simpler_example` for every question, so this component only formats them.
 */
export default function AnswerReview({ answers = [] }) {
  if (!answers.length) {
    return <p className="text-sm text-muted">No answer details available.</p>;
  }

  return (
    <div className="space-y-4">
      {answers.map((answer, index) => {
        const options = answer.options || [];
        const selected = Number.isInteger(answer.selected_index)
          ? answer.selected_index
          : null;
        const correct = Number.isInteger(answer.correct_index)
          ? answer.correct_index
          : null;

        return (
          <div
            key={`${answer.question_id || index}`}
            className={`rounded-2xl border bg-surface p-4 sm:p-5 ${
              answer.is_correct
                ? "border-emerald-200 dark:border-emerald-400/30"
                : "border-rose-200 dark:border-rose-400/30"
            }`}
          >
            <div className="flex items-start gap-3">
              <span
                className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${
                  answer.is_correct
                    ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200"
                    : "bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-200"
                }`}
              >
                {index + 1}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <p className="text-sm font-semibold leading-relaxed text-ink">
                    {answer.question}
                  </p>
                  <span
                    className={`chip shrink-0 ${
                      answer.is_correct
                        ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200"
                        : "bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-200"
                    }`}
                  >
                    {answer.is_correct ? (
                      <CheckCircle2 className="h-3.5 w-3.5" />
                    ) : (
                      <XCircle className="h-3.5 w-3.5" />
                    )}
                    {answer.is_correct ? "Correct" : "Not yet"}
                  </span>
                </div>

                {answer.difficulty && (
                  <div className="mt-2">
                    <DifficultyPill difficulty={answer.difficulty} />
                  </div>
                )}

                <ul className="mt-3 space-y-1.5">
                  {options.map((option, optionIndex) => {
                    const isCorrect = optionIndex === correct;
                    const isSelected = optionIndex === selected;
                    return (
                      <li
                        key={optionIndex}
                        className={`flex items-start gap-2 rounded-lg border px-3 py-2 text-sm ${
                          isCorrect
                            ? "border-emerald-200 bg-emerald-50/70 text-emerald-900 dark:border-emerald-400/30 dark:bg-emerald-500/10 dark:text-emerald-100"
                            : isSelected
                              ? "border-rose-200 bg-rose-50/70 text-rose-900 dark:border-rose-400/30 dark:bg-rose-500/10 dark:text-rose-100"
                              : "border-line bg-surface-2/50 text-ink/80"
                        }`}
                      >
                        <span className="mt-0.5 text-[11px] font-bold uppercase text-muted">
                          {String.fromCharCode(65 + optionIndex)}
                        </span>
                        <span className="flex-1">{option}</span>
                        {isCorrect && (
                          <span className="text-[10px] font-bold uppercase tracking-wide text-emerald-600 dark:text-emerald-300">
                            Answer
                          </span>
                        )}
                        {isSelected && !isCorrect && (
                          <span className="text-[10px] font-bold uppercase tracking-wide text-rose-600 dark:text-rose-300">
                            You
                          </span>
                        )}
                      </li>
                    );
                  })}
                </ul>

                {answer.explanation && (
                  <p className="mt-3 rounded-lg bg-surface-2/70 px-3 py-2 text-xs leading-relaxed text-ink/80">
                    <span className="font-semibold text-ink">Why: </span>
                    {answer.explanation}
                  </p>
                )}

                {answer.simpler_example && !answer.is_correct && (
                  <p className="mt-2 flex items-start gap-2 rounded-lg border border-sun-200 bg-sun-50/70 px-3 py-2 text-xs leading-relaxed text-amber-900 dark:border-sun-400/25 dark:bg-sun-500/10 dark:text-amber-100">
                    <Lightbulb className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                    <span>
                      <span className="font-semibold">Try it this way: </span>
                      {answer.simpler_example}
                    </span>
                  </p>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
