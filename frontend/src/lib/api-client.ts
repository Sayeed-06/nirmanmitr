/**
 * API client for communicating with the FastAPI backend.
 */

import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests (Clerk integration)
api.interceptors.request.use(async (config) => {
  if (typeof window !== "undefined") {
    const clerk = (window as any).Clerk;
    if (clerk && clerk.session) {
      try {
        const token = await clerk.session.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (err) {
        console.error("Failed to fetch Clerk token", err);
      }
    }
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to sign-in
      if (typeof window !== "undefined") {
        window.location.href = "/sign-in";
      }
    }
    return Promise.reject(error);
  }
);

// ─── API Functions ───

export async function uploadBOQ(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function parseBOQ(projectId: string) {
  const { data } = await api.post(`/parse/${projectId}`);
  return data;
}

export async function getProjects(page = 1, pageSize = 20) {
  const { data } = await api.get("/projects", {
    params: { page, page_size: pageSize },
  });
  return data;
}

export async function getProject(
  projectId: string,
  page = 1,
  pageSize = 50,
  matchedOnly?: boolean
) {
  const { data } = await api.get(`/project/${projectId}`, {
    params: { page, page_size: pageSize, matched_only: matchedOnly },
  });
  return data;
}

export async function getDSRItem(itemNumber: string) {
  const { data } = await api.get(`/dsr/${encodeURIComponent(itemNumber)}`);
  return data;
}

export async function searchDSR(
  query: string,
  chapter?: string,
  page = 1,
  pageSize = 20
) {
  const { data } = await api.get("/search", {
    params: { q: query, chapter, page, page_size: pageSize },
  });
  return data;
}

export async function getChapters() {
  const { data } = await api.get("/chapters");
  return data;
}

export async function getStats() {
  const { data } = await api.get("/stats");
  return data;
}
