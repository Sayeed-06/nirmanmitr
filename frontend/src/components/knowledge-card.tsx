"use client";

import { useState, useEffect } from "react";
import { DSRItem } from "@/types";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
} from "@/components/ui/drawer";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api-client";

interface KnowledgeCardProps {
  itemNumber: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function KnowledgeCard({
  itemNumber,
  open,
  onOpenChange,
}: KnowledgeCardProps) {
  const [data, setData] = useState<DSRItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (open && itemNumber) {
      const fetchData = async () => {
        setLoading(true);
        setError(false);
        try {
          const response = await api.get(`/dsr/${encodeURIComponent(itemNumber)}`);
          setData(response.data);
        } catch (err) {
          setError(true);
          console.error("Failed to load DSR item:", err);
        } finally {
          setLoading(false);
        }
      };
      fetchData();
    }
  }, [open, itemNumber]);

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        {loading ? (
          <div className="flex h-full items-center justify-center p-6">
            <div className="flex flex-col items-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="mt-4 text-sm text-muted-foreground">Loading knowledge card...</p>
            </div>
          </div>
        ) : error || !data ? (
          <div className="flex h-full items-center justify-center p-6 text-center">
            <div>
              <div className="text-4xl mb-4">⚠️</div>
              <h3 className="text-lg font-semibold mb-2">Item Not Found</h3>
              <p className="text-sm text-muted-foreground max-w-sm">
                We couldn't find detailed knowledge for item <strong>{itemNumber}</strong> in our current database.
              </p>
            </div>
          </div>
        ) : (
          <>
            <DrawerHeader>
              <div className="flex items-center gap-2 mb-2">
                <span className="inline-flex items-center rounded-md bg-primary/10 px-2 py-1 text-xs font-semibold text-primary">
                  DSR {data.item_number}
                </span>
                <span className="text-xs text-muted-foreground">{data.chapter}</span>
              </div>
              <DrawerTitle className="text-2xl">
                {data.simple_title || `DSR Item ${data.item_number}`}
              </DrawerTitle>
              <DrawerDescription className="mt-2 text-sm leading-relaxed text-foreground/80">
                {data.official_description}
              </DrawerDescription>
            </DrawerHeader>

            <div className="flex-1 overflow-y-auto scrollbar-thin p-6">
              {!data.summary && (
                <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-4 mb-6 border border-amber-200 dark:border-amber-900/50">
                  <h4 className="text-sm font-semibold text-amber-800 dark:text-amber-400">Under Construction</h4>
                  <p className="mt-1 text-sm text-amber-700 dark:text-amber-500">
                    The structured knowledge for this item is currently being prepared by our engineering team.
                  </p>
                </div>
              )}

              {data.summary && (
                <div className="prose prose-sm dark:prose-invert max-w-none mb-8">
                  <h3 className="text-base font-semibold">Plain English Summary</h3>
                  <p className="text-muted-foreground">{data.summary}</p>
                </div>
              )}

              <Tabs defaultValue="execution" className="w-full">
                <TabsList className="w-full justify-start border-b border-border rounded-none bg-transparent h-auto p-0 mb-6">
                  <TabsTrigger
                    value="execution"
                    className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none px-4 py-2"
                  >
                    Execution & Mistakes
                  </TabsTrigger>
                  <TabsTrigger
                    value="materials"
                    className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none px-4 py-2"
                  >
                    Materials
                  </TabsTrigger>
                  <TabsTrigger
                    value="specs"
                    className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none px-4 py-2"
                  >
                    Specs & Context
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="execution" className="space-y-8">
                  {data.execution_steps && data.execution_steps.length > 0 ? (
                    <div>
                      <h4 className="flex items-center gap-2 font-semibold mb-4">
                        <span className="text-primary">📋</span> Step-by-Step Execution
                      </h4>
                      <ol className="space-y-4">
                        {data.execution_steps.map((step, idx) => (
                          <li key={idx} className="flex gap-4">
                            <span className="flex-shrink-0 flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs font-medium">
                              {idx + 1}
                            </span>
                            <span className="text-sm pt-0.5">{step}</span>
                          </li>
                        ))}
                      </ol>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground italic">No execution steps available.</p>
                  )}

                  {data.common_mistakes && data.common_mistakes.length > 0 && (
                    <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-5">
                      <h4 className="flex items-center gap-2 font-semibold text-destructive mb-3">
                        <span className="text-lg">⚠️</span> Common Mistakes to Avoid
                      </h4>
                      <ul className="space-y-2">
                        {data.common_mistakes.map((mistake, idx) => (
                          <li key={idx} className="flex gap-2 text-sm text-destructive/90">
                            <span>•</span>
                            <span>{mistake}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="materials">
                  {data.materials && data.materials.length > 0 ? (
                    <div className="rounded-lg border border-border overflow-hidden">
                      <table className="w-full text-sm">
                        <thead className="bg-muted/50 text-left">
                          <tr>
                            <th className="px-4 py-3 font-medium">Material</th>
                            <th className="px-4 py-3 font-medium">Standard Quantity</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                          {data.materials.map((mat, idx) => (
                            <tr key={idx}>
                              <td className="px-4 py-3">{mat.name}</td>
                              <td className="px-4 py-3 text-muted-foreground">{mat.quantity || "—"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground italic">No material data available.</p>
                  )}
                </TabsContent>

                <TabsContent value="specs" className="space-y-6">
                  {data.purpose && (
                    <div>
                      <h4 className="font-semibold mb-2">Purpose</h4>
                      <p className="text-sm text-muted-foreground">{data.purpose}</p>
                    </div>
                  )}

                  {data.where_used && data.where_used.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">Commonly Used In</h4>
                      <div className="flex flex-wrap gap-2">
                        {data.where_used.map((place, idx) => (
                          <span key={idx} className="inline-flex rounded-md bg-secondary px-2.5 py-1 text-xs text-secondary-foreground">
                            {place}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {data.specification_reference && (
                    <div className="rounded-lg bg-muted p-4">
                      <h4 className="text-sm font-semibold mb-1">CPWD Specification Reference</h4>
                      <p className="text-sm text-muted-foreground font-mono">{data.specification_reference}</p>
                    </div>
                  )}

                  <div className="rounded-lg border border-dashed border-border p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-semibold">Video Explainer</h4>
                        <p className="text-xs text-muted-foreground mt-1">Coming soon in Phase 2</p>
                      </div>
                      <span className="text-2xl opacity-50">🎥</span>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          </>
        )}
      </DrawerContent>
    </Drawer>
  );
}
