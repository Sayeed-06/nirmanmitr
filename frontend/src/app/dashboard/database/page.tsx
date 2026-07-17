"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { api } from "@/lib/api-client";
import { DSRItem } from "@/types";
import { KnowledgeCard } from "@/components/knowledge-card";

export default function DatabasePage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const query = searchParams.get("q") || "";

  const [searchInput, setSearchInput] = useState(query);
  const [results, setResults] = useState<DSRItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(!!query);

  const [cardOpen, setCardOpen] = useState(false);
  const [activeItem, setActiveItem] = useState<string | null>(null);

  useEffect(() => {
    if (query) {
      handleSearch(query);
    }
  }, [query]);

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setHasSearched(true);
    try {
      const response = await api.get("/dsr/search", {
        params: { query: searchQuery, limit: 20 }
      });
      setResults(response.data);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      const params = new URLSearchParams(searchParams.toString());
      params.set("q", searchInput);
      router.push(`${pathname}?${params.toString()}`);
    }
  };

  const openCard = (itemNumber: string) => {
    setActiveItem(itemNumber);
    setCardOpen(true);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-tight">DSR Knowledge Base</h1>
        <p className="text-muted-foreground text-lg max-w-2xl">
          Search the complete CPWD Delhi Schedule of Rates (DSR) database. 
          Enter an item number (e.g., 2.8.1) or description keywords.
        </p>

        <form onSubmit={onSubmit} className="w-full max-w-2xl mt-8 relative flex items-center">
          <div className="absolute left-4 text-muted-foreground">
            <svg width="20" height="20" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M10 6.5C10 8.433 8.433 10 6.5 10C4.567 10 3 8.433 3 6.5C3 4.567 4.567 3 6.5 3C8.433 3 10 4.567 10 6.5ZM9.30884 10.0159C8.53901 10.6318 7.56251 11 6.5 11C4.01472 11 2 8.98528 2 6.5C2 4.01472 4.01472 2 6.5 2C8.98528 2 11 4.01472 11 6.5C11 7.56251 10.6318 8.53901 10.0159 9.30884L12.8536 12.1464C13.0488 12.3417 13.0488 12.6583 12.8536 12.8536C12.6583 13.0488 12.3417 13.0488 12.1464 12.8536L9.30884 10.0159Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path>
            </svg>
          </div>
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search for item 2.8.1, 'Earth work', 'Concrete'..."
            className="w-full h-14 pl-12 pr-32 rounded-full border border-border bg-card text-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent shadow-sm transition-all"
          />
          <button
            type="submit"
            disabled={loading}
            className="absolute right-2 h-10 px-6 bg-primary text-primary-foreground rounded-full font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </form>
      </div>

      {hasSearched && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">
            {results.length} Results for "{query}"
          </h2>

          {results.length === 0 && !loading ? (
            <div className="p-8 text-center rounded-xl border border-border bg-card">
              <p className="text-muted-foreground text-lg">No matching DSR items found.</p>
              <p className="text-sm text-muted-foreground mt-2">Try searching for a different keyword or standard item number.</p>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {results.map((item) => (
                <div 
                  key={item.id} 
                  onClick={() => openCard(item.item_number)}
                  className="group relative rounded-xl border border-border bg-card p-5 hover:shadow-md hover:border-primary/50 transition-all cursor-pointer flex flex-col h-full"
                >
                  <div className="flex items-start justify-between mb-3">
                    <span className="inline-flex items-center rounded-md bg-primary/10 px-2.5 py-0.5 text-sm font-semibold text-primary">
                      {item.item_number}
                    </span>
                  </div>
                  <h3 className="font-semibold text-lg mb-2 line-clamp-2 group-hover:text-primary transition-colors">
                    {item.simple_title || item.official_description.split('.')[0]}
                  </h3>
                  <p className="text-sm text-muted-foreground line-clamp-3 mb-4 flex-grow">
                    {item.official_description}
                  </p>
                  <div className="flex items-center justify-between mt-auto pt-4 border-t border-border/50 text-xs text-muted-foreground">
                    <span className="truncate pr-4">{item.chapter}</span>
                    <span className="flex-shrink-0 group-hover:translate-x-1 transition-transform">Read more →</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <KnowledgeCard
        itemNumber={activeItem}
        open={cardOpen}
        onOpenChange={setCardOpen}
      />
    </div>
  );
}
