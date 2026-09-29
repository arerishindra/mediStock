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
    let errorMsg = res.statusText || "Request failed";
    if (json?.error?.message) {
      errorMsg = json.error.message;
    } else if (Array.isArray(json?.detail)) {
      errorMsg = json.detail.map((d: any) => d.msg || JSON.stringify(d)).join(", ");
    } else if (typeof json?.detail === "string") {
      errorMsg = json.detail;
    } else if (json?.detail?.message) {
      errorMsg = json.detail.message;
    }
    throw new Error(errorMsg);
  }

  return json;
}
