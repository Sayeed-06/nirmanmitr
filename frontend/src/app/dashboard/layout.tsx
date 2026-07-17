"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useTheme } from "@/components/theme-provider";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboardIcon },
  { href: "/dashboard/upload", label: "Upload BOQ", icon: UploadIcon },
  { href: "/dashboard/projects", label: "Projects", icon: FolderIcon },
  { href: "/dashboard/database", label: "DSR Search", icon: SearchIcon },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex h-screen bg-background">
      {/* ─── Sidebar ─── */}
      <aside className="hidden md:flex flex-col w-64 border-r border-border bg-card">
        {/* Logo */}
        <div className="flex h-16 items-center gap-2 px-6 border-b border-border">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
            N
          </div>
          <span className="text-lg font-semibold tracking-tight">NirmanMitr</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive =
              pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-border p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Theme</span>
            <div className="flex gap-1">
              {(["light", "dark", "system"] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTheme(t)}
                  className={cn(
                    "rounded-md px-2 py-1 text-xs transition-colors",
                    theme === t
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {t === "light" ? "☀️" : t === "dark" ? "🌙" : "💻"}
                </button>
              ))}
            </div>
          </div>

          {/* Coming Soon Badge */}
          <div className="mt-3 rounded-lg border border-dashed border-border p-3">
            <p className="text-xs font-medium text-muted-foreground">Coming Soon</p>
            <p className="text-xs text-muted-foreground/70 mt-1">
              AI Assistant • Video Explainers
            </p>
          </div>
        </div>
      </aside>

      {/* ─── Main Content ─── */}
      <main className="flex-1 overflow-auto scrollbar-thin">
        {/* Mobile Header */}
        <div className="md:hidden flex h-14 items-center justify-between border-b border-border px-4">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-xs">
              N
            </div>
            <span className="font-semibold">NirmanMitr</span>
          </div>
        </div>

        <div className="p-6 lg:p-8">{children}</div>
      </main>
    </div>
  );
}

// ─── Icon Components ───
function LayoutDashboardIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect width="7" height="9" x="3" y="3" rx="1" />
      <rect width="7" height="5" x="14" y="3" rx="1" />
      <rect width="7" height="9" x="14" y="12" rx="1" />
      <rect width="7" height="5" x="3" y="16" rx="1" />
    </svg>
  );
}

function UploadIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" x2="12" y1="3" y2="15" />
    </svg>
  );
}

function FolderIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z" />
    </svg>
  );
}

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.3-4.3" />
    </svg>
  );
}
