export type DeviceStatus = "unknown" | "online" | "offline";
export type DeviceType = "router" | "server" | "switch";
export type AlertSeverity = "warning" | "critical";
export type AlertType =
  | "device_offline"
  | "high_cpu"
  | "high_memory"
  | "high_latency";

export interface Device {
  id: number;
  name: string;
  hostname: string;
  ip_address: string;
  device_type: DeviceType;
  status: DeviceStatus;
  last_seen: string | null;
  created_at: string;
}

export interface DeviceCreate {
  name: string;
  hostname: string;
  ip_address: string;
  device_type: DeviceType;
}

export interface Metric {
  id: number;
  device_id: number;
  cpu_usage: number;
  memory_usage: number;
  latency_ms: number;
  uptime_seconds: number;
  recorded_at: string;
}

export interface Alert {
  id: number;
  device_id: number;
  alert_type: AlertType;
  severity: AlertSeverity;
  message: string;
  resolved: boolean;
  created_at: string;
  resolved_at: string | null;
}
