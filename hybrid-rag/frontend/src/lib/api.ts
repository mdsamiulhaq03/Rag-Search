import type { AskResponse, DocumentInfo, Health, Mode } from "./types";

export const MAX_QUESTION_LENGTH = 1000;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const offline = "Can't reach the search service. Start it from backend/ with: uvicorn app.main:app";
  let res: Response;
  try {
    res = await fetch(`/api${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new Error(offline);
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (typeof data?.detail === "string") throw new Error(data.detail);
    // The Next.js proxy answers 500 without a JSON body when the backend is down.
    throw new Error(res.status >= 500 ? offline : `Request failed (${res.status})`);
  }
  return data as T;
}

export async function ask(question: string, mode: Mode): Promise<AskResponse> {
  const trimmed = question.trim();
  if (!trimmed) throw new Error("Question is empty.");
  if (trimmed.length > MAX_QUESTION_LENGTH) {
    throw new Error(`Question must be at most ${MAX_QUESTION_LENGTH} characters.`);
  }
  return request<AskResponse>("/ask", {
    method: "POST",
    body: JSON.stringify({ question: trimmed, mode }),
  });
}

export function ingest(): Promise<{ chunks: number }> {
  return request<{ chunks: number }>("/ingest", { method: "POST" });
}

export function health(): Promise<Health> {
  return request<Health>("/health");
}

export function documents(): Promise<DocumentInfo[]> {
  return request<DocumentInfo[]>("/documents");
}
