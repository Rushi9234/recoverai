const getApiBase = () => {
  if (typeof window !== "undefined") {
    // In browser: use relative /api endpoint on production or localhost:8000 in dev if needed
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
      return "http://localhost:8000/api";
    }
    return "/api";
  }
  return "http://localhost:8000/api";
};

export async function fetchApi<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${getApiBase()}${cleanEndpoint}`;
  
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
