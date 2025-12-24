const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type IngestParams = {
  file: File;
  collection?: string;
  chunk_size?: number;
  overlap?: number;
  model_dir?: string;
};

export type IngestResponse = {
  stored_chunks: number;
  collection: string;
  source: string;
};

export async function ingestFile(params: IngestParams): Promise<IngestResponse> {
  const form = new FormData();
  form.append("file", params.file);
  if (params.collection) form.append("collection", params.collection);
  if (params.chunk_size != null) form.append("chunk_size", String(params.chunk_size));
  if (params.overlap != null) form.append("overlap", String(params.overlap));
  if (params.model_dir) form.append("model_dir", params.model_dir);

  const res = await fetch(`${API_BASE}/api/ingest`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || res.statusText);
  }
  return res.json();
}

export type QueryParams = {
  question: string;
  collection?: string;
  top_k?: number;
  model_dir?: string;
  use_llm?: boolean;
};

export type QueryHit = {
  rank: number;
  distance: number;
  metadata?: {
    source?: string;
    page?: number;
    chunk_in_page?: number;
  };
  text: string;
};

export type QueryResponse = {
  question: string;
  collection: string;
  results: QueryHit[];
  answer?: string | null;
};

export async function queryRag(params: QueryParams): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || res.statusText);
  }
  return res.json();
}
