import type { Source } from "@/lib/types";

const MAX_RANK = 15; // backend retrieves top_k * 3 candidates per search

const ROWS = [
  { key: "bm25", label: "Word match", fill: "bg-highlighter", ring: "ring-ink/15" },
  { key: "vector", label: "Meaning match", fill: "bg-violet", ring: "" },
] as const;

/** Two bars showing how each search ranked this passage: longer bar = ranked higher. */
export function RankMeter({ ranks }: { ranks: Source["ranks"] }) {
  return (
    <dl className="grid grid-cols-[auto_1fr_auto] items-center gap-x-3 gap-y-1 text-xs text-graphite">
      {ROWS.map(({ key, label, fill, ring }) => {
        const rank = ranks[key];
        const width = rank ? Math.max(8, ((MAX_RANK + 1 - Math.min(rank, MAX_RANK)) / MAX_RANK) * 100) : 0;
        return (
          <div key={key} className="contents">
            <dt>{label}</dt>
            <dd className="h-1.5 overflow-hidden rounded-full bg-rule" aria-hidden="true">
              <div className={`h-full rounded-full ring-1 ring-inset ${fill} ${ring}`} style={{ width: `${width}%` }} />
            </dd>
            <dd className="w-14 text-right tabular-nums">{rank ? `#${rank}` : "no match"}</dd>
          </div>
        );
      })}
    </dl>
  );
}
