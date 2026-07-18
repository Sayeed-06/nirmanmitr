"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api-client";
import { ParsedItem, ProjectDetailResponse } from "@/types";
import { cn, formatFileSize, formatNumber } from "@/lib/utils";
import { KnowledgeCard } from "@/components/knowledge-card";

export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = params.id as string;

  const [data, setData] = useState<ProjectDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "matched" | "unmatched">("all");
  
  // Knowledge Card state
  const [cardOpen, setCardOpen] = useState(false);
  const [activeItem, setActiveItem] = useState<string | null>(null);

  useEffect(() => {
    const fetchProject = async () => {
      setLoading(true);
      try {
        const isMatched = filter === "all" ? undefined : filter === "matched";
        // Fetch up to 50 items for demo (in prod, use pagination)
        const response = await api.get(`/project/${projectId}`, {
          params: { page: 1, page_size: 50, matched_only: isMatched }
        });
        setData(response.data);
      } catch (err) {
        console.error("Failed to load project:", err);
      } finally {
        setLoading(false);
      }
    };
    if (projectId) fetchProject();
  }, [projectId, filter]);

  const handleRowClick = (item: ParsedItem) => {
    if (item.dsr_item_number) {
      setActiveItem(item.dsr_item_number);
      setCardOpen(true);
    }
  };

  if (loading && !data) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold">Project not found</h2>
        <p className="text-muted-foreground mt-2">The BOQ file could not be loaded.</p>
      </div>
    );
  }

  const { project, items } = data;

  return (
    <div className="space-y-6">
      {/* ─── Header ─── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold tracking-tight truncate max-w-md">
              {project.name}
            </h1>
            <span
              className={cn(
                "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold",
                project.status === "completed" && "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400",
                project.status === "parsing" && "bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400",
                project.status === "failed" && "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400"
              )}
            >
              {project.status.toUpperCase()}
            </span>
          </div>
          <p className="text-sm text-muted-foreground flex gap-4">
            <span>Type: {project.file_type.toUpperCase()}</span>
            <span>Size: {formatFileSize(project.file_size)}</span>
          </p>
        </div>

        {project.status === "completed" && (
          <div className="flex gap-4 text-center">
            <div className="rounded-lg bg-card border border-border px-4 py-2">
              <p className="text-sm text-muted-foreground">Matches</p>
              <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
                {project.dsr_matches}
              </p>
            </div>
            <div className="rounded-lg bg-card border border-border px-4 py-2">
              <p className="text-sm text-muted-foreground">Total</p>
              <p className="text-lg font-bold">{project.total_items}</p>
            </div>
          </div>
        )}
      </div>

      {/* ─── Toolbar ─── */}
      <div className="flex items-center justify-between bg-card p-2 rounded-lg border border-border">
        <div className="flex gap-1">
          {(["all", "matched", "unmatched"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "px-4 py-1.5 text-sm font-medium rounded-md transition-colors",
                filter === f
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              )}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
              {f === "matched" && ` (${project.dsr_matches})`}
            </button>
          ))}
        </div>
      </div>

      {/* ─── Table ─── */}
      <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="px-4 py-3 font-medium text-muted-foreground w-20">S.No</th>
                <th className="px-4 py-3 font-medium text-muted-foreground w-24">Item No</th>
                <th className="px-4 py-3 font-medium text-muted-foreground min-w-[300px]">Description</th>
                <th className="px-4 py-3 font-medium text-muted-foreground text-right">Qty</th>
                <th className="px-4 py-3 font-medium text-muted-foreground text-center">Unit</th>
                <th className="px-4 py-3 font-medium text-muted-foreground text-right">Rate</th>
                <th className="px-4 py-3 font-medium text-muted-foreground text-center w-28">DSR Match</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                    No items found for this filter.
                  </td>
                </tr>
              ) : (
                items.map((item, idx) => (
                  <tr
                    key={item.id}
                    onClick={() => handleRowClick(item)}
                    className={cn(
                      "transition-colors",
                      item.is_matched
                        ? "cursor-pointer hover:bg-accent/50"
                        : "hover:bg-muted/30"
                    )}
                  >
                    <td className="px-4 py-3 align-top text-muted-foreground">
                      {idx + 1}
                    </td>
                    <td className="px-4 py-3 align-top font-medium">
                      {item.item_number || "—"}
                    </td>
                    <td className="px-4 py-3 align-top">
                      <div className="max-w-2xl">
                        {item.description}
                      </div>
                    </td>
                    <td className="px-4 py-3 align-top text-right">
                      {item.quantity ? formatNumber(item.quantity) : "—"}
                    </td>
                    <td className="px-4 py-3 align-top text-center">
                      {item.unit || "—"}
                    </td>
                    <td className="px-4 py-3 align-top text-right">
                      {item.rate ? formatNumber(item.rate) : "—"}
                    </td>
                    <td className="px-4 py-3 align-top text-center">
                      {item.is_matched ? (
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-100 dark:bg-emerald-950/40 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900/50 shadow-sm">
                          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                          {item.dsr_item_number}
                        </span>
                      ) : (
                        <span className="inline-flex rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
                          —
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ─── Knowledge Card Drawer ─── */}
      <KnowledgeCard
        itemNumber={activeItem}
        open={cardOpen}
        onOpenChange={setCardOpen}
      />
    </div>
  );
}
