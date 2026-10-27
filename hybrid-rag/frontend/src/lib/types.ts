export type Mode = "hybrid" | "bm25" | "vector";

export interface Source {
  n: number;
  source: string;
  heading: string;
  text: string;
  score: number;
  ranks: Partial<Record<"bm25" | "vector", number>>;
}

export interface AskResponse {
  answer: string;
  mode: Mode;
  sources: Source[];
}

export interface Health {
  status: string;
  indexed: boolean;
  config_error: string | null;
}

export interface DocumentInfo {
  source: string;
  chunks: number;
}

export type TurnStatus = "loading" | "done" | "error";

export interface Turn {
  id: string;
  question: string;
  mode: Mode;
  status: TurnStatus;
  answer?: string;
  sources?: Source[];
  error?: string;
}
