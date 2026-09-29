const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface FetchOptions extends RequestInit {
  token?: string;
}

export async function apiFetch<T = any>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const url = endpoint.startsWith("http") ? endpoint : `${API_URL}${endpoint}`;

  const res = await fetch(url, {
    ...options,
    headers,
    credentials: "include", // send cookies
  });

  const json = await res.json().catch(() => null);

  if (!res.ok) {
    const errorMsg = json?.error?.message || json?.detail || res.statusText || "Request failed";
    throw new Error(errorMsg);
  }

  return json;
}
