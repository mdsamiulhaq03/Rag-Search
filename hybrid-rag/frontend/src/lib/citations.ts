export type AnswerPart = { kind: "text"; value: string } | { kind: "cite"; n: number };

const CITATION_RE = /\[(\d+)\]/g;

/** Split an answer like "20 days [1][3]." into text and citation parts. */
export function parseCitations(answer: string): AnswerPart[] {
  const parts: AnswerPart[] = [];
  let last = 0;
  for (const match of answer.matchAll(CITATION_RE)) {
    const index = match.index ?? 0;
    if (index > last) parts.push({ kind: "text", value: answer.slice(last, index) });
    parts.push({ kind: "cite", n: Number(match[1]) });
    last = index + match[0].length;
  }
  if (last < answer.length) parts.push({ kind: "text", value: answer.slice(last) });
  return parts;
}
