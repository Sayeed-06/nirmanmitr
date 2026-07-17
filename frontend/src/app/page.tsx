import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* ─── Navigation ─── */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
              N
            </div>
            <span className="text-lg font-semibold tracking-tight">NirmanMitr</span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/sign-in"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Sign in
            </Link>
            <Link
              href="/sign-up"
              className="inline-flex h-9 items-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ─── Hero Section ─── */}
      <section className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 pt-16">
        {/* Gradient background */}
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[600px] rounded-full bg-primary/5 blur-[120px]" />
          <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full bg-blue-500/5 blur-[100px]" />
        </div>

        <div className="relative z-10 mx-auto max-w-4xl text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-4 py-1.5 text-xs font-medium text-muted-foreground mb-8">
            <span className="flex h-2 w-2 rounded-full bg-success" />
            CPWD DSR 2021 Knowledge Base — 12 Chapters Available
          </div>

          <h1 className="text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
            Understand every{" "}
            <span className="bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent">
              BOQ item
            </span>{" "}
            instantly
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed">
            Upload your Bill of Quantities. NirmanMitr detects CPWD DSR item numbers and
            shows you structured knowledge cards with materials, execution steps,
            and common mistakes — in plain language.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="inline-flex h-12 items-center rounded-xl bg-primary px-8 text-sm font-medium text-primary-foreground shadow-lg shadow-primary/25 hover:bg-primary/90 hover:shadow-xl transition-all"
            >
              Upload BOQ — Free
            </Link>
            <Link
              href="/dashboard/database"
              className="inline-flex h-12 items-center rounded-xl border border-border bg-card px-8 text-sm font-medium hover:bg-accent transition-colors"
            >
              Browse DSR Database
            </Link>
          </div>
        </div>
      </section>

      {/* ─── Features ─── */}
      <section className="relative py-32 px-6">
        <div className="mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Everything you need to decode a BOQ
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              No more flipping through DSR books. Upload, detect, understand.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: "📄",
                title: "Upload Any Format",
                description:
                  "PDF, Excel, CSV — we parse them all. Smart table detection handles messy formatting.",
              },
              {
                icon: "🔍",
                title: "DSR Item Detection",
                description:
                  "Automatic regex-based detection of CPWD DSR item numbers with exact and partial matching.",
              },
              {
                icon: "📚",
                title: "Knowledge Cards",
                description:
                  "Each item gets a structured card: simple explanation, materials, execution steps, and common mistakes.",
              },
              {
                icon: "🏗️",
                title: "Construction Context",
                description:
                  "Written for engineers, by engineers. Every explanation is reviewed and construction-specific.",
              },
              {
                icon: "⚡",
                title: "Instant Results",
                description:
                  "No AI inference delays. All knowledge is pre-generated and served from a structured database.",
              },
              {
                icon: "🔒",
                title: "Your Data, Secured",
                description:
                  "Enterprise authentication, encrypted storage, and your files are never shared or used for training.",
              },
            ].map((feature, idx) => (
              <div
                key={idx}
                className="group relative rounded-2xl border border-border bg-card p-8 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300"
              >
                <div className="text-3xl mb-4">{feature.icon}</div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── How It Works ─── */}
      <section className="relative py-32 px-6 bg-muted/30">
        <div className="mx-auto max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Three steps to clarity
            </h2>
          </div>

          <div className="space-y-12">
            {[
              {
                step: "01",
                title: "Upload your BOQ",
                description:
                  "Drag and drop your PDF, Excel, or CSV file. Our parser handles multi-page tables, merged cells, and messy formatting.",
              },
              {
                step: "02",
                title: "Auto-detect DSR items",
                description:
                  "We scan every line for CPWD DSR item numbers using deterministic pattern matching. No AI hallucinations — just precise regex.",
              },
              {
                step: "03",
                title: "Read Knowledge Cards",
                description:
                  "Click any matched item to see its Knowledge Card: a structured breakdown of what the work is, materials needed, how to execute it, and mistakes to avoid.",
              },
            ].map((item, idx) => (
              <div key={idx} className="flex gap-8 items-start">
                <div className="flex-shrink-0 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary font-mono font-bold text-sm">
                  {item.step}
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {item.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CTA ─── */}
      <section className="relative py-32 px-6">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Start understanding your BOQ today
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Built for contractors, engineers, and students who need answers, not more confusion.
          </p>
          <div className="mt-8">
            <Link
              href="/dashboard"
              className="inline-flex h-12 items-center rounded-xl bg-primary px-8 text-sm font-medium text-primary-foreground shadow-lg shadow-primary/25 hover:bg-primary/90 transition-all"
            >
              Get Started — Free
            </Link>
          </div>
        </div>
      </section>

      {/* ─── Footer ─── */}
      <footer className="border-t border-border py-12 px-6">
        <div className="mx-auto max-w-7xl flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded bg-primary text-primary-foreground font-bold text-xs">
              N
            </div>
            <span className="text-sm font-medium">NirmanMitr</span>
          </div>
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} NirmanMitr. CPWD DSR 2021 reference.
          </p>
        </div>
      </footer>
    </div>
  );
}
