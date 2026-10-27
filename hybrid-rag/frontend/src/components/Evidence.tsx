"use client";

import { useState } from "react";

import { cleanExcerpt, documentTitle } from "@/lib/format";
import { highlightTerms } from "@/lib/highlight";
import type { Source } from "@/lib/types";
import { RankMeter } from "./RankMeter";

interface Props {
  source: Source;
  terms: Set<string>;
  domId: string;
  active: boolean;
  delayMs: number;
}

export function Evidence({ source, terms, domId, active, delayMs }: Props) {
  const [expanded, setExpanded] = useState(false);
  let markIndex = 0;

  return (
    <li
      id={domId}
      className={`scroll-mt-40 border-t border-rule py-4 pl-3 transition-[border-color,background-color] duration-300 first:border-t-0 border-l-2 ${
        active ? "border-l-violet bg-sheet" : "border-l-transparent"
      }`}
      title={`Combined score ${source.score.toFixed(4)}`}
    >
      <p className="flex gap-2.5 text-sm">
        <span className="tabular-nums font-semibold text-violet">{source.n}</span>
        <span className="min-w-0">
          <span className="font-semibold">{documentTitle(source.source)}</span>
          {source.heading && <span className="text-graphite"> › {source.heading}</span>}
        </span>
      </p>

      <p className={`mt-2 pl-[1.4rem] font-serif text-[0.95rem] leading-relaxed ${expanded ? "" : "line-clamp-4"}`}>
        {highlightTerms(cleanExcerpt(source.text), terms).map((part, i) =>
          part.match ? (
            <mark
              key={i}
              className="hl"
              style={{ "--hl-delay": `${delayMs + markIndex++ * 70}ms` } as React.CSSProperties}
            >
              {part.text}
            </mark>
          ) : (
            <span key={i}>{part.text}</span>
          ),
        )}
      </p>

      <div className="mt-3 space-y-3 pl-[1.4rem]">
        <RankMeter ranks={source.ranks} />
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="text-xs font-medium text-graphite underline decoration-rule underline-offset-4 hover:text-ink"
        >
          {expanded ? "Show less" : "Read full passage"}
        </button>
      </div>
    </li>
  );
}
