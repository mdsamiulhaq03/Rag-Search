"use client";

import { useCallback, useEffect, useState } from "react";

import { AskForm } from "@/components/AskForm";
import { EmptyState } from "@/components/EmptyState";
import { Header } from "@/components/Header";
import { TurnView } from "@/components/TurnView";
import { ask, documents as fetchDocuments, health as fetchHealth, ingest } from "@/lib/api";
import type { DocumentInfo, Health, Mode, Turn } from "@/lib/types";

const message = (err: unknown, fallback: string) => (err instanceof Error ? err.message : fallback);

export default function Home() {
  const [turns, setTurns] = useState<Turn[]>([]); // newest first
  const [mode, setMode] = useState<Mode>("hybrid");
  const [health, setHealth] = useState<Health | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [docs, setDocs] = useState<DocumentInfo[]>([]);
  const [notice, setNotice] = useState<string | null>(null);
  const [reindexing, setReindexing] = useState(false);

  const busy = turns.some((t) => t.status === "loading");

  const refreshStatus = useCallback(async () => {
    try {
      const [h, d] = await Promise.all([fetchHealth(), fetchDocuments()]);
      setHealth(h);
      setDocs(d);
      setHealthError(null);
    } catch (err) {
      setHealthError(message(err, "Search service unavailable"));
    }
  }, []);

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  const updateTurn = (id: string, patch: Partial<Turn>) =>
    setTurns((prev) => prev.map((t) => (t.id === id ? { ...t, ...patch } : t)));

  async function handleAsk(question: string) {
    const id = crypto.randomUUID();
    setNotice(null);
    setTurns((prev) => [{ id, question: question.trim(), mode, status: "loading" }, ...prev]);
    window.scrollTo({ top: 0, behavior: "smooth" });
    try {
      const res = await ask(question, mode);
      updateTurn(id, { status: "done", answer: res.answer, sources: res.sources });
    } catch (err) {
      updateTurn(id, { status: "error", error: message(err, "The question couldn't be answered. Try again.") });
    }
  }

  async function handleReindex() {
    setReindexing(true);
    setNotice(null);
    try {
      const { chunks } = await ingest();
      setNotice(`Re-indexed. ${chunks} passages are searchable.`);
    } catch (err) {
      setNotice(message(err, "Re-indexing failed. Check the search service logs."));
    } finally {
      setReindexing(false);
      refreshStatus();
    }
  }

  const problem = healthError ?? health?.config_error ?? (health && !health.indexed ? "No docs are indexed yet. Choose Re-index docs to build the index." : null);
  const banner = notice ?? problem;

  return (
    <div className="min-h-dvh">
      <div className="sticky top-0 z-10 border-b border-rule bg-paper/95 backdrop-blur">
        <Header
          health={health}
          healthError={healthError}
          documentCount={docs.length}
          reindexing={reindexing}
          onReindex={handleReindex}
        />
        {turns.length > 0 && (
          <div className="mx-auto max-w-6xl px-4 pb-4 sm:px-8">
            <AskForm mode={mode} onModeChange={setMode} onSubmit={handleAsk} disabled={busy} size="compact" />
          </div>
        )}
      </div>

      <main className="mx-auto max-w-6xl px-4 pb-24 sm:px-8">
        {banner && (
          <p className="mt-6 max-w-[70ch] border-l-2 border-highlighter bg-sheet px-4 py-3 text-sm" role="status">
            {banner}
          </p>
        )}

        {turns.length === 0 ? (
          <EmptyState mode={mode} onModeChange={setMode} onAsk={handleAsk} disabled={busy} documents={docs} />
        ) : (
          <div className="pt-6">
            {turns.map((turn) => (
              <TurnView key={turn.id} turn={turn} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
