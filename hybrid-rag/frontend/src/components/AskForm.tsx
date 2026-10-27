"use client";

import { useLayoutEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";

import { MAX_QUESTION_LENGTH } from "@/lib/api";
import { MODES } from "@/lib/format";
import type { Mode } from "@/lib/types";

interface Props {
  mode: Mode;
  onModeChange: (mode: Mode) => void;
  onSubmit: (question: string) => void;
  disabled: boolean;
  size: "large" | "compact";
}

export function AskForm({ mode, onModeChange, onSubmit, disabled, size }: Props) {
  const [question, setQuestion] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Grow with the text up to max-h-40, then scroll.
  useLayoutEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
    el.style.overflowY = el.scrollHeight > el.clientHeight ? "auto" : "hidden";
  }, [question]);
  const canSend = !disabled && question.trim().length > 0;
  const large = size === "large";

  function submit(e?: FormEvent) {
    e?.preventDefault();
    if (!canSend) return;
    onSubmit(question);
    setQuestion("");
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <form onSubmit={submit} className={large ? "space-y-4" : "space-y-2.5"}>
      <div
        className={`flex items-end gap-3 border-b-2 border-ink focus-within:border-violet ${large ? "pb-2" : "pb-1.5"}`}
      >
        <textarea
          ref={inputRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={onKeyDown}
          maxLength={MAX_QUESTION_LENGTH}
          rows={1}
          autoFocus={large}
          placeholder={large ? "Ask about leave, expenses, IT, onboarding…" : "Ask another question…"}
          aria-label="Your question"
          className={`max-h-40 min-w-0 flex-1 resize-none overflow-hidden bg-transparent outline-none placeholder:text-graphite/70 focus-visible:outline-none ${
            large ? "py-2 text-xl sm:text-2xl" : "py-1.5 text-lg"
          }`}
        />
        <button
          type="submit"
          disabled={!canSend}
          className={`shrink-0 rounded-md bg-ink font-semibold text-on-ink transition-opacity disabled:opacity-30 ${
            large ? "mb-1 px-5 py-2.5" : "mb-0.5 px-4 py-2 text-sm"
          }`}
        >
          Ask
        </button>
      </div>

      <fieldset className="flex flex-wrap items-center gap-x-1 gap-y-2 text-sm">
        <legend className="sr-only">How to search</legend>
        <span className="mr-2 hidden text-graphite sm:inline">Search by</span>
        {MODES.map((m) => (
          <label
            key={m.value}
            title={m.hint}
            className={`cursor-pointer rounded-full px-3 py-1 transition-colors has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-violet ${
              mode === m.value ? "bg-ink text-on-ink" : "text-ink hover:bg-rule/60"
            }`}
          >
            <input
              type="radio"
              name={`mode-${size}`}
              value={m.value}
              checked={mode === m.value}
              onChange={() => onModeChange(m.value)}
              className="sr-only"
            />
            {m.label}
          </label>
        ))}
      </fieldset>
    </form>
  );
}
