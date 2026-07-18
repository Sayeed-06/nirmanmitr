"use client";

import * as Dialog from "@radix-ui/react-dialog";
import { useState, useEffect } from "react";
import { api } from "@/lib/api-client";
import { useRouter } from "next/navigation";
import { DSRItemSummary } from "@/types";

interface EditItemDialogProps {
  children: React.ReactNode;
  itemSummary: DSRItemSummary;
  onSuccess?: () => void;
}

export function EditItemDialog({ children, itemSummary, onSuccess }: EditItemDialogProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const [formData, setFormData] = useState({
    item_number: "",
    chapter: "",
    official_description: "",
    simple_title: "",
    summary: "",
    future_video: "",
    execution_steps: "",
  });

  const [materials, setMaterials] = useState([{ name: "", quantity: "", grade: "" }]);

  useEffect(() => {
    if (open) {
      const fetchItemDetails = async () => {
        setFetching(true);
        try {
          // Fetch full item details
          const { data } = await api.get(`/dsr/${encodeURIComponent(itemSummary.item_number)}`);
          setFormData({
            item_number: data.item_number || "",
            chapter: data.chapter || "",
            official_description: data.official_description || "",
            simple_title: data.simple_title || "",
            summary: data.summary || "",
            future_video: data.future_video || "",
            execution_steps: (data.execution_steps || []).join("\n"),
          });
          
          if (data.materials && data.materials.length > 0) {
            setMaterials(data.materials.map((m: any) => ({
              name: m.name || "",
              quantity: m.quantity || "",
              grade: m.grade || "",
            })));
          } else {
            setMaterials([{ name: "", quantity: "", grade: "" }]);
          }
        } catch (err) {
          console.error(err);
          setError("Failed to load item details for editing.");
        } finally {
          setFetching(false);
        }
      };
      fetchItemDetails();
    }
  }, [open, itemSummary]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleMaterialChange = (index: number, field: string, value: string) => {
    const newMaterials = [...materials];
    newMaterials[index] = { ...newMaterials[index], [field]: value };
    setMaterials(newMaterials);
  };

  const addMaterial = () => setMaterials([...materials, { name: "", quantity: "", grade: "" }]);
  
  const removeMaterial = (index: number) => {
    setMaterials(materials.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        ...formData,
        materials: materials.filter((m) => m.name.trim() !== ""),
        execution_steps: formData.execution_steps
          .split("\n")
          .map((s) => s.trim())
          .filter((s) => s.length > 0),
      };

      await api.patch(`/admin/dsr/${itemSummary.id}`, payload);
      setOpen(false);
      if (onSuccess) onSuccess();
      router.refresh();
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to update item");
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
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-2xl max-h-[90vh] overflow-y-auto translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg sm:rounded-xl data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]">
          <div className="flex flex-col space-y-1.5 text-center sm:text-left mb-6">
            <Dialog.Title className="text-lg font-semibold leading-none tracking-tight">Edit DSR Item</Dialog.Title>
            <Dialog.Description className="text-sm text-muted-foreground">
              Modify the robust entry for item {itemSummary.item_number}.
            </Dialog.Description>
          </div>

          {fetching ? (
            <div className="py-12 text-center text-sm text-muted-foreground">Loading item details...</div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
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
                  className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">Plain English Summary</label>
                <textarea
                  name="summary"
                  value={formData.summary}
                  onChange={handleChange}
                  className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">Execution Steps (One per line)</label>
                <textarea
                  name="execution_steps"
                  value={formData.execution_steps}
                  onChange={handleChange}
                  placeholder="Step 1...&#10;Step 2..."
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium leading-none">Materials Required</label>
                  <button type="button" onClick={addMaterial} className="text-xs text-primary font-medium hover:underline">
                    + Add Material
                  </button>
                </div>
                <div className="space-y-2">
                  {materials.map((mat, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <input
                        placeholder="Material Name"
                        value={mat.name}
                        onChange={(e) => handleMaterialChange(i, "name", e.target.value)}
                        className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                      <input
                        placeholder="Quantity/Unit"
                        value={mat.quantity}
                        onChange={(e) => handleMaterialChange(i, "quantity", e.target.value)}
                        className="flex h-9 w-32 rounded-md border border-input bg-transparent px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                      <button type="button" onClick={() => removeMaterial(i)} className="text-destructive text-sm px-2">
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">Video URL (Optional)</label>
                <input
                  name="future_video"
                  value={formData.future_video}
                  onChange={handleChange}
                  placeholder="https://youtube.com/..."
                  className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-4 border-t sticky bottom-0 bg-background/95 pb-2">
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
                  {loading ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          )}

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
