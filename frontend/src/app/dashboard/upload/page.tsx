"use client";

import { useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api-client";
import { cn } from "@/lib/utils";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    setError(null);
    const validTypes = [
      "application/pdf", 
      "text/csv", 
      "application/vnd.ms-excel", 
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ];
    
    if (!validTypes.includes(selectedFile.type)) {
      setError("Invalid file type. Please upload a PDF, Excel, or CSV file.");
      return;
    }
    
    if (selectedFile.size > 10 * 1024 * 1024) { // 10MB
      setError("File is too large. Maximum size is 10MB.");
      return;
    }
    
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setProgress(10);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    
    // Simulate initial upload progress
    const progressInterval = setInterval(() => {
      setProgress(prev => (prev >= 90 ? 90 : prev + 10));
    }, 500);

    try {
      const response = await api.post("/upload/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      
      const projectId = response.data.project_id;
      
      // Delay slightly for UX
      setTimeout(() => {
        router.push(`/dashboard/project/${projectId}`);
      }, 500);
      
    } catch (err: any) {
      clearInterval(progressInterval);
      setProgress(0);
      setUploading(false);
      setError(err.response?.data?.detail || "Failed to upload file. Please try again.");
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Upload BOQ</h1>
        <p className="text-muted-foreground mt-2">
          Upload a Bill of Quantities (BOQ) document. We will parse it and instantly map items to the DSR Knowledge Base.
        </p>
      </div>

      <div
        className={cn(
          "relative flex flex-col items-center justify-center w-full h-80 px-6 py-10 rounded-2xl border-2 border-dashed transition-all",
          isDragging 
            ? "border-primary bg-primary/5 shadow-sm scale-[1.01]" 
            : file
              ? "border-primary/50 bg-card"
              : "border-border hover:border-primary/50 hover:bg-accent/50 bg-card cursor-pointer"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !file && fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.csv,.xlsx,.xls"
          className="hidden"
        />

        {file ? (
          <div className="flex flex-col items-center text-center space-y-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
              <svg width="32" height="32" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 9.5C1 8.67157 1.67157 8 2.5 8H4.14645L2.14645 6H1C0.447715 6 0 6.44772 0 7V13C0 13.5523 0.447715 14 1 14H14C14.5523 14 15 13.5523 15 13V7C15 6.44772 14.5523 6 14 6H12.8536L10.8536 8H12.5C13.3284 8 14 8.67157 14 9.5V12.5C14 13.3284 13.3284 14 12.5 14H2.5C1.67157 14 1 13.3284 1 12.5V9.5ZM4.14645 5L7.14645 2H3C2.44772 2 2 2.44772 2 3V5H4.14645ZM7.85355 2L10.8536 5H13V3C13 2.44772 12.5523 2 12 2H7.85355ZM7.5 4.70711L9.64645 6.85355L8.93934 7.56066L7.5 6.12132L6.06066 7.56066L5.35355 6.85355L7.5 4.70711Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path>
              </svg>
            </div>
            <div>
              <p className="text-lg font-medium">{file.name}</p>
              <p className="text-sm text-muted-foreground mt-1">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            
            {!uploading && (
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                }}
                className="text-sm text-destructive hover:underline mt-2"
              >
                Remove file
              </button>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center text-center space-y-4 pointer-events-none">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted text-muted-foreground">
              <svg width="24" height="24" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7.5 2C7.77614 2 8 2.22386 8 2.5V7H12.5C12.7761 7 13 7.22386 13 7.5C13 7.77614 12.7761 8 12.5 8H8V12.5C8 12.7761 7.77614 13 7.5 13C7.22386 13 7 12.7761 7 12.5V8H2.5C2.22386 8 2 7.77614 2 7.5C2 7.22386 2.22386 7 2.5 7H7V2.5C7 2.22386 7.22386 2 7.5 2Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path>
              </svg>
            </div>
            <div>
              <p className="text-lg font-medium">Click to upload or drag and drop</p>
              <p className="text-sm text-muted-foreground mt-1">
                PDF, Excel (XLSX), or CSV up to 10MB
              </p>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-2">
          <span>⚠️</span> {error}
        </div>
      )}

      {uploading && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm font-medium">
            <span>Uploading & Parsing...</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
            <div 
              className="h-full bg-primary transition-all duration-300 ease-out" 
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      <div className="flex justify-end pt-4">
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="h-12 px-8 rounded-lg bg-primary text-primary-foreground font-medium transition-colors hover:bg-primary/90 disabled:opacity-50 disabled:pointer-events-none"
        >
          {uploading ? "Processing..." : "Process BOQ"}
        </button>
      </div>
    </div>
  );
}
