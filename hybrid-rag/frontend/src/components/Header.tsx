"use client";

import type { Health } from "@/lib/types";
import { Logo } from "./Logo";
import { ThemeToggle } from "./ThemeToggle";

interface Props {
  health: Health | null;
  healthError: string | null;
  documentCount: number;
  reindexing: boolean;
  onReindex: () => void;
}

function statusOf(health: Health | null, healthError: string | null, documentCount: number) {
  if (healthError) return { dot: "bg-danger", label: "Search service offline" };
  if (!health) return { dot: "bg-rule", label: "Connecting…" };
  if (health.config_error) return { dot: "bg-danger", label: "Setup needed" };
  if (!health.indexed) return { dot: "bg-highlighter", label: "No docs indexed yet" };
  return { dot: "bg-emerald-500", label: `${documentCount} documents searchable` };
}

export function Header({ health, healthError, documentCount, reindexing, onReindex }: Props) {
  const status = statusOf(health, healthError, documentCount);

  return (
    <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-8">
      <Logo />
      <div className="flex items-center gap-3">
        <span className="hidden items-center gap-2 text-sm text-graphite sm:flex">
          <span className={`size-2 rounded-full ${status.dot}`} aria-hidden="true" />
          {status.label}
        </span>
        <button
          type="button"
          onClick={onReindex}
          disabled={reindexing || !!healthError}
          className="rounded-md border border-rule px-3 py-1.5 text-sm font-medium hover:border-ink disabled:opacity-40"
        >
          {reindexing ? "Re-indexing…" : "Re-index docs"}
        </button>
        <ThemeToggle />
      </div>
    </div>
  );
}
