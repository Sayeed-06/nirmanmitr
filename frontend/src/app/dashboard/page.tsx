"use client";

import { formatNumber } from "@/lib/utils";
import Link from "next/link";

// Dashboard overview page with statistics
export default function DashboardPage() {
  // In production, these come from the API via TanStack Query
  const stats = {
    total_projects: 0,
    total_items: 0,
    total_matches: 0,
    total_unknown: 0,
  };

  const matchRate =
    stats.total_items > 0
      ? ((stats.total_matches / stats.total_items) * 100).toFixed(1)
      : "—";

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-muted-foreground">
          Upload BOQs and explore CPWD DSR knowledge.
        </p>
      </div>

      {/* ─── Stats Grid ─── */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          {
            label: "Total Projects",
            value: formatNumber(stats.total_projects),
            icon: "📁",
            color: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
          },
          {
            label: "BOQ Items Parsed",
            value: formatNumber(stats.total_items),
            icon: "📋",
            color: "bg-purple-500/10 text-purple-600 dark:text-purple-400",
          },
          {
            label: "DSR Matches",
            value: formatNumber(stats.total_matches),
            icon: "✅",
            color: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
          },
          {
            label: "Match Rate",
            value: `${matchRate}%`,
            icon: "📊",
            color: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
          },
        ].map((stat, idx) => (
          <div
            key={idx}
            className="group relative rounded-xl border border-border bg-card p-6 hover:shadow-md transition-all duration-200"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium text-muted-foreground">
                {stat.label}
              </span>
              <span className={`flex h-8 w-8 items-center justify-center rounded-lg text-sm ${stat.color}`}>
                {stat.icon}
              </span>
            </div>
            <p className="text-3xl font-bold tracking-tight">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* ─── Quick Actions ─── */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Link
          href="/dashboard/upload"
          className="group relative flex items-center gap-4 rounded-xl border border-dashed border-border bg-card p-6 hover:border-primary/50 hover:shadow-md transition-all duration-200"
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-2xl">
            📤
          </div>
          <div>
            <h3 className="text-lg font-semibold group-hover:text-primary transition-colors">
              Upload New BOQ
            </h3>
            <p className="text-sm text-muted-foreground">
              PDF, Excel, or CSV — drag and drop
            </p>
          </div>
        </Link>

        <Link
          href="/search"
          className="group relative flex items-center gap-4 rounded-xl border border-dashed border-border bg-card p-6 hover:border-primary/50 hover:shadow-md transition-all duration-200"
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-2xl">
            🔍
          </div>
          <div>
            <h3 className="text-lg font-semibold group-hover:text-primary transition-colors">
              Search DSR Database
            </h3>
            <p className="text-sm text-muted-foreground">
              Browse 12+ chapters of CPWD DSR items
            </p>
          </div>
        </Link>
      </div>

      {/* ─── Empty State / Recent Projects ─── */}
      <div className="rounded-xl border border-border bg-card">
        <div className="border-b border-border px-6 py-4">
          <h2 className="text-lg font-semibold">Recent Projects</h2>
        </div>
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-muted text-3xl mb-4">
            📁
          </div>
          <h3 className="text-lg font-medium mb-1">No projects yet</h3>
          <p className="text-sm text-muted-foreground max-w-sm">
            Upload your first BOQ to see your projects listed here with parsed
            items and DSR matches.
          </p>
          <Link
            href="/dashboard/upload"
            className="mt-4 inline-flex h-9 items-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Upload BOQ
          </Link>
        </div>
      </div>
    </div>
  );
}
