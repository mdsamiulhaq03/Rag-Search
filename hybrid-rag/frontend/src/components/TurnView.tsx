"use client";

import { useMemo, useState } from "react";

import { parseCitations } from "@/lib/citations";
import { modeLabel } from "@/lib/format";
import { queryTerms } from "@/lib/highlight";
import type { Turn } from "@/lib/types";
import { Evidence } from "./Evidence";

const ACTIVE_MS = 1800;

export function TurnView({ turn }: { turn: Turn }) {
  const [active, setActive] = useState<number | null>(null);
  const terms = useMemo(() => queryTerms(turn.question), [turn.question]);
  const sourceId = (n: number) => `${turn.id}-src-${n}`;

  function showSource(n: number) {
    setActive(n);
    document.getElementById(sourceId(n))?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    setTimeout(() => setActive((cur) => (cur === n ? null : cur)), ACTIVE_MS);
  }

  return (
    <article className="border-t-2 border-ink py-8 first:border-t-0 first:pt-2" aria-busy={turn.status === "loading"}>
      <header className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
        <h2 className="max-w-[40ch] text-2xl font-bold leading-tight tracking-tight text-balance">{turn.question}</h2>
        <p className="text-sm text-graphite">Searched by {modeLabel(turn.mode).toLowerCase()}</p>
      </header>

      {turn.status === "loading" && (
        <p className="mt-5 flex items-center gap-2 font-serif text-lg text-graphite" role="status">
          <span className="inline-block h-4 w-10 animate-pulse rounded-sm bg-highlighter" aria-hidden="true" />
          Reading the docs…
        </p>
      )}

      {turn.status === "error" && (
        <p className="mt-5 max-w-[62ch] border-l-2 border-danger pl-4 text-danger" role="alert">
          {turn.error}
        </p>
      )}

      {turn.status === "done" && (
        <div className="mt-5 grid gap-x-12 gap-y-8 lg:grid-cols-12">
          <div className="lg:col-span-7">
            <p className="max-w-[62ch] whitespace-pre-wrap font-serif text-lg leading-[1.7]">
              {parseCitations(turn.answer ?? "").map((part, i) =>
                part.kind === "text" ? (
                  <span key={i}>{part.value}</span>
                ) : (
                  <button
                    key={i}
                    type="button"
                    onClick={() => showSource(part.n)}
                    onMouseEnter={() => setActive(part.n)}
                    onMouseLeave={() => setActive(null)}
                    className="relative top-[-0.45em] ml-0.5 font-sans text-[0.7rem] font-bold text-violet hover:underline"
                    aria-label={`Go to source ${part.n}`}
                  >
                    {part.n}
                  </button>
                ),
              )}
            </p>
          </div>

          {!!turn.sources?.length && (
            <aside className="lg:col-span-5" aria-label="Sources">
              <h3 className="text-sm font-semibold text-graphite">Where this comes from</h3>
              <ol className="mt-1">
                {turn.sources.map((s, i) => (
                  <Evidence
                    key={s.n}
                    source={s}
                    terms={terms}
                    domId={sourceId(s.n)}
                    active={active === s.n}
                    delayMs={150 + i * 120}
                  />
                ))}
              </ol>
            </aside>
          )}
        </div>
      )}
    </article>
  );
}
