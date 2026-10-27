// Mirrors the backend BM25 tokenizer (backend/app/retrieval.py) so highlights show
// exactly the words keyword search can match. Keep STOP_WORDS in sync.
const TOKEN_RE = /[a-z0-9]+(?:-[a-z0-9]+)*/g;

const STOP_WORDS = new Set(
  "a an and are as at be by can do does for from get got how i if in is it me my of on or so the to was we what when where which who why will with you your".split(
    " ",
  ),
);

export type TextPart = { text: string; match: boolean };

export function queryTerms(question: string): Set<string> {
  const tokens = question.toLowerCase().match(TOKEN_RE) ?? [];
  return new Set(tokens.filter((t) => !STOP_WORDS.has(t)));
}

/** Split text into runs, marking tokens that appear in the question. */
export function highlightTerms(text: string, terms: Set<string>): TextPart[] {
  if (terms.size === 0) return [{ text, match: false }];
  const parts: TextPart[] = [];
  const re = /[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*/g;
  let last = 0;
  for (const m of text.matchAll(re)) {
    const start = m.index ?? 0;
    if (!terms.has(m[0].toLowerCase())) continue;
    if (start > last) parts.push({ text: text.slice(last, start), match: false });
    parts.push({ text: m[0], match: true });
    last = start + m[0].length;
  }
  if (last < text.length) parts.push({ text: text.slice(last), match: false });
  return parts;
}
