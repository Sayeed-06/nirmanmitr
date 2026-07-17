"use client";

import Link from "next/link";
import { cn, formatFileSize, formatRelativeDate } from "@/lib/utils";
import type { Project } from "@/types";

// Placeholder projects for UI development
const MOCK_PROJECTS: Project[] = [];

export default function ProjectsPage() {
  const projects = MOCK_PROJECTS;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
          <p className="mt-1 text-muted-foreground">
            Your uploaded BOQ files and parsing results.
          </p>
        </div>
        <Link
          href="/dashboard/upload"
          className="inline-flex h-9 items-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Upload New
        </Link>
      </div>

      {projects.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-20 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-muted text-3xl mb-4">
            📁
          </div>
          <h3 className="text-lg font-medium mb-1">No projects yet</h3>
          <p className="text-sm text-muted-foreground max-w-sm mb-4">
            Upload your first BOQ file to get started with DSR item detection.
          </p>
          <Link
            href="/dashboard/upload"
            className="inline-flex h-9 items-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Upload BOQ
          </Link>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              href={`/dashboard/project/${project.id}`}
              className="group rounded-xl border border-border bg-card p-6 hover:shadow-md hover:border-primary/30 transition-all duration-200"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-lg">
                  {project.file_type === "pdf"
                    ? "📄"
                    : project.file_type === "xlsx"
                    ? "📊"
                    : "📋"}
                </div>
                <span
                  className={cn(
                    "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
                    project.status === "completed" &&
                      "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400",
                    project.status === "parsing" &&
                      "bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400",
                    project.status === "failed" &&
                      "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400"
                  )}
                >
                  {project.status}
                </span>
              </div>

              <h3 className="font-semibold truncate group-hover:text-primary transition-colors">
                {project.name}
              </h3>
              <p className="text-xs text-muted-foreground mt-1">
                {formatFileSize(project.file_size)} •{" "}
                {formatRelativeDate(project.created_at)}
              </p>

              {project.status === "completed" && (
                <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                  <div className="rounded-lg bg-muted p-2">
                    <p className="text-sm font-bold">{project.total_items}</p>
                    <p className="text-xs text-muted-foreground">Items</p>
                  </div>
                  <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 p-2">
                    <p className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                      {project.dsr_matches}
                    </p>
                    <p className="text-xs text-muted-foreground">Matched</p>
                  </div>
                  <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-2">
                    <p className="text-sm font-bold text-amber-600 dark:text-amber-400">
                      {project.unknown_items}
                    </p>
                    <p className="text-xs text-muted-foreground">Unknown</p>
                  </div>
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
