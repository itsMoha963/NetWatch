import type { Alert, Device, DeviceCreate, Metric } from "./types";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed with ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function getDevices(): Promise<Device[]> {
  return request<Device[]>("/devices");
}

export function createDevice(device: DeviceCreate): Promise<Device> {
  return request<Device>("/devices", {
    method: "POST",
    body: JSON.stringify(device),
  });
}

export function getMetrics(deviceId: number): Promise<Metric[]> {
  return request<Metric[]>(`/devices/${deviceId}/metrics?limit=30`);
}

export function getAlerts(): Promise<Alert[]> {
  return request<Alert[]>("/alerts?resolved=false&limit=50");
}
