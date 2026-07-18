"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import { DSRItemSummary } from "@/types";
import { AddItemDialog } from "@/components/admin/add-item-dialog";

import { EditItemDialog } from "@/components/admin/edit-item-dialog";

export default function AdminDsrPage() {
  const [items, setItems] = useState<DSRItemSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const response = await api.get("/admin/dsr");
      setItems(response.data);
    } catch (err) {
      console.error("Failed to fetch admin DSR items", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
          <p className="text-muted-foreground mt-1">Manage DSR knowledge base items manually.</p>
        </div>
        
        <AddItemDialog onSuccess={fetchItems}>
          <button className="px-4 py-2 bg-primary text-primary-foreground font-medium rounded-md hover:bg-primary/90 transition-colors flex items-center gap-2">
            <span>+</span> Add New Item
          </button>
        </AddItemDialog>
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <table className="w-full text-sm text-left">
          <thead className="bg-muted/50 text-muted-foreground border-b border-border">
            <tr>
              <th className="px-6 py-4 font-medium">Item Number</th>
              <th className="px-6 py-4 font-medium">Chapter</th>
              <th className="px-6 py-4 font-medium w-1/3">Title / Description</th>
              <th className="px-6 py-4 font-medium text-center">Status</th>
              <th className="px-6 py-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-muted-foreground">
                  Loading items...
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-muted-foreground">
                  No DSR items found in the database. Add one to get started.
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.id} className="hover:bg-muted/30 transition-colors">
                  <td className="px-6 py-4 font-semibold text-primary">{item.item_number}</td>
                  <td className="px-6 py-4 text-muted-foreground">{item.chapter}</td>
                  <td className="px-6 py-4">
                    <p className="font-medium">{item.simple_title || "No Title"}</p>
                    <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">{item.official_description}</p>
                  </td>
                  <td className="px-6 py-4 text-center">
                    {item.is_populated ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-full bg-green-500/10 text-green-500 text-xs font-medium">
                        Populated
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded-full bg-amber-500/10 text-amber-500 text-xs font-medium">
                        Draft
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <EditItemDialog itemSummary={item} onSuccess={fetchItems}>
                      <button className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium">
                        Edit
                      </button>
                    </EditItemDialog>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
