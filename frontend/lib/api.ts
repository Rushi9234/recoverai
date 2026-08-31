const API_BASE = "http://localhost:8000/api";

export async function fetchApi<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${API_BASE}${cleanEndpoint}`;
  
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    cache: "no-store"
  });

  const data = await res.json();
  if (!res.ok) {
    const errorMsg = data?.error?.message || data?.detail || `HTTP Error ${res.status}`;
    throw new Error(errorMsg);
  }
  return data;
}

export function formatCurrency(amountMinor: number, currency: string = "INR"): string {
  const major = amountMinor / 100;
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: currency,
    maximumFractionDigits: 0
  }).format(major);
}
