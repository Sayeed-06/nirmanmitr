"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api-client";
import { DSRItemSummary } from "@/types";
import { cn } from "@/lib/utils";

export default function AdminPage() {
  const [items, setItems] = useState<DSRItemSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "empty" | "populated">("all");

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const response = await api.get("/admin/dsr", {
        params: { page_size: 100 }
      });
      setItems(response.data);
    } catch (err) {
      console.error("Failed to load admin items:", err);
    } finally {
      setLoading(false);
    }
  };

  const filteredItems = items.filter(item => {
    const matchesSearch = 
      item.item_number.toLowerCase().includes(search.toLowerCase()) || 
      (item.simple_title || "").toLowerCase().includes(search.toLowerCase());
      
    if (filter === "empty") return matchesSearch && !item.is_populated;
    if (filter === "populated") return matchesSearch && item.is_populated;
    return matchesSearch;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Knowledge Base Admin</h1>
          <p className="text-muted-foreground mt-1">
            Manage and edit DSR Knowledge Cards.
          </p>
        </div>
        <button
          className="h-10 px-4 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
          onClick={() => alert("Creating new items requires API integration. See Phase 7 documentation.")}
        >
          + Add New DSR Item
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 items-center bg-card p-2 rounded-lg border border-border">
        <div className="relative flex-1 w-full">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by item number or title..."
            className="w-full h-10 px-4 rounded-md border border-border bg-transparent text-sm focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
        <div className="flex gap-1 w-full sm:w-auto">
          {(["all", "empty", "populated"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "flex-1 sm:flex-none px-4 py-2 text-sm font-medium rounded-md transition-colors",
                filter === f
                  ? "bg-secondary text-secondary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              )}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="px-4 py-3 font-medium text-muted-foreground">Item Number</th>
                <th className="px-4 py-3 font-medium text-muted-foreground">Title / Chapter</th>
                <th className="px-4 py-3 font-medium text-muted-foreground text-center">Status</th>
                <th className="px-4 py-3 font-medium text-muted-foreground text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {loading ? (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">
                    <div className="flex justify-center mb-2">
                      <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                    </div>
                    Loading items...
                  </td>
                </tr>
              ) : filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">
                    No items found matching the current filters.
                  </td>
                </tr>
              ) : (
                filteredItems.map((item) => (
                  <tr key={item.id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-4 py-3 align-top font-medium">
                      {item.item_number}
                    </td>
                    <td className="px-4 py-3 align-top">
                      <div className="font-medium text-foreground">
                        {item.simple_title || <span className="italic text-muted-foreground">No simple title</span>}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {item.chapter}
                      </div>
                    </td>
                    <td className="px-4 py-3 align-top text-center">
                      {item.is_populated ? (
                        <span className="inline-flex items-center rounded-full bg-emerald-100 dark:bg-emerald-950/40 px-2 py-0.5 text-xs font-semibold text-emerald-700 dark:text-emerald-400">
                          Populated
                        </span>
                      ) : (
                        <span className="inline-flex items-center rounded-full bg-amber-100 dark:bg-amber-950/40 px-2 py-0.5 text-xs font-semibold text-amber-700 dark:text-amber-400">
                          Empty
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 align-top text-right">
                      <button 
                        className="text-sm text-primary font-medium hover:underline"
                        onClick={() => alert(`Editing item ${item.item_number} is not implemented in this demo.`)}
                      >
                        Edit
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
