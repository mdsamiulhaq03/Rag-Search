"use client";

import { documentTitle } from "@/lib/format";
import type { DocumentInfo, Mode } from "@/lib/types";
import { AskForm } from "./AskForm";

const EXAMPLES = [
  "What is the hotel cap in EXP-204?",
  "How much vacation do I get?",
  "What do I do if I lose my laptop?",
];

interface Props {
  mode: Mode;
  onModeChange: (mode: Mode) => void;
  onAsk: (question: string) => void;
  disabled: boolean;
  documents: DocumentInfo[];
}

export function EmptyState({ mode, onModeChange, onAsk, disabled, documents }: Props) {
  return (
    <section className="grid gap-x-16 gap-y-12 pt-10 sm:pt-20 lg:grid-cols-12">
      <div className="lg:col-span-8">
        <h1 className="max-w-[14ch] text-5xl font-bold leading-[1.02] tracking-[-0.03em] sm:text-7xl">
          What do you need to know?
        </h1>
        <p className="mt-5 max-w-[52ch] font-serif text-lg leading-relaxed text-graphite">
          Answers come straight from the company docs. Every answer shows the passages it used, with
          your words highlighted.
        </p>
        <div className="mt-10">
          <AskForm mode={mode} onModeChange={onModeChange} onSubmit={onAsk} disabled={disabled} size="large" />
        </div>
        <ul className="mt-8 space-y-2">
          {EXAMPLES.map((q) => (
            <li key={q}>
              <button
                type="button"
                onClick={() => onAsk(q)}
                disabled={disabled}
                className="text-left font-serif text-graphite underline decoration-rule decoration-2 underline-offset-[5px] hover:text-ink hover:decoration-highlighter disabled:opacity-50"
              >
                {q}
              </button>
            </li>
          ))}
        </ul>
      </div>

      {documents.length > 0 && (
        <aside className="lg:col-span-4 lg:pt-4">
          <h2 className="text-sm font-semibold text-graphite">Searching these documents</h2>
          <ul className="mt-3 border-t border-rule">
            {documents.map((d) => (
              <li key={d.source} className="flex items-baseline justify-between gap-4 border-b border-rule py-2.5">
                <span className="font-medium">{documentTitle(d.source)}</span>
                <span className="text-sm tabular-nums text-graphite">
                  {d.chunks} {d.chunks === 1 ? "passage" : "passages"}
                </span>
              </li>
            ))}
          </ul>
        </aside>
      )}
    </section>
  );
}
