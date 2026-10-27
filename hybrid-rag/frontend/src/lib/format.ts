import type { Mode } from "./types";

export const MODES: { value: Mode; label: string; hint: string }[] = [
  { value: "hybrid", label: "Words + meaning", hint: "Combine exact word matches with matches by meaning" },
  { value: "bm25", label: "Exact words", hint: "Only find passages that use your words" },
  { value: "vector", label: "Meaning", hint: "Find passages that mean the same thing, even with different words" },
];

export const modeLabel = (mode: Mode) => MODES.find((m) => m.value === mode)?.label ?? mode;

const ACRONYMS = new Set(["hr", "it", "faq", "vpn", "mfa"]);

/** "hr-leave-policy.md" -> "HR leave policy" */
export function documentTitle(source: string): string {
  const base = (source.split("/").pop() ?? source).replace(/\.(md|txt)$/i, "");
  return base
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((word, i) => {
      const lower = word.toLowerCase();
      if (ACRONYMS.has(lower)) return lower.toUpperCase();
      return i === 0 ? lower[0].toUpperCase() + lower.slice(1) : lower;
    })
    .join(" ");
}

/** Strip markdown heading lines from chunk text; the heading is already shown above the excerpt. */
export function cleanExcerpt(text: string): string {
  return text
    .split("\n")
    .filter((line) => !/^#{1,6}\s/.test(line.trim()))
    .join("\n")
    .trim();
}
