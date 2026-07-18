"use client";

import * as Dialog from "@radix-ui/react-dialog";
import { useState } from "react";
import { api } from "@/lib/api-client";
import { useRouter } from "next/navigation";

interface AddItemDialogProps {
  children: React.ReactNode;
  onSuccess?: () => void;
}

export function AddItemDialog({ children, onSuccess }: AddItemDialogProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const [formData, setFormData] = useState({
    item_number: "",
    chapter: "",
    official_description: "",
    simple_title: "",
    summary: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.post("/admin/dsr", formData);
      setOpen(false);
      setFormData({
        item_number: "",
        chapter: "",
        official_description: "",
        simple_title: "",
        summary: "",
      });
      if (onSuccess) onSuccess();
      router.refresh();
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to add item");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>
        {children}
      </Dialog.Trigger>
      
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg sm:rounded-xl data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]">
          <div className="flex flex-col space-y-1.5 text-center sm:text-left mb-6">
            <Dialog.Title className="text-lg font-semibold leading-none tracking-tight">Add DSR Item</Dialog.Title>
            <Dialog.Description className="text-sm text-muted-foreground">
              Manually add a new item to the CPWD DSR knowledge base.
            </Dialog.Description>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
                {error}
              </div>
            )}
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">Item Number *</label>
                <input
                  required
                  name="item_number"
                  value={formData.item_number}
                  onChange={handleChange}
                  placeholder="e.g. 5.33"
                  className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">Chapter *</label>
                <input
                  required
                  name="chapter"
                  value={formData.chapter}
                  onChange={handleChange}
                  placeholder="e.g. 5.0 Reinforced Cement Concrete"
                  className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">Title</label>
              <input
                name="simple_title"
                value={formData.simple_title}
                onChange={handleChange}
                placeholder="e.g. Brick Masonry Work"
                className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">Official Description *</label>
              <textarea
                required
                name="official_description"
                value={formData.official_description}
                onChange={handleChange}
                placeholder="Exact CPWD description..."
                className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">Plain English Summary</label>
              <textarea
                name="summary"
                value={formData.summary}
                onChange={handleChange}
                placeholder="Simple explanation of what this work is..."
                className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-4 border-t">
              <Dialog.Close asChild>
                <button type="button" className="px-4 py-2 text-sm font-medium rounded-md hover:bg-muted transition-colors">
                  Cancel
                </button>
              </Dialog.Close>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm font-medium rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                {loading ? "Adding..." : "Add Item"}
              </button>
            </div>
          </form>

          <Dialog.Close asChild>
            <button className="absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100 transition-opacity focus:outline-none focus:ring-2 focus:ring-primary">
              ✕
            </button>
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
