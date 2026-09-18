import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import { createDevice, getAlerts, getDevices, getMetrics } from "./api";
import type { Alert, Device, DeviceCreate, Metric } from "./types";

const emptyDevice: DeviceCreate = {
  name: "",
  hostname: "",
  ip_address: "",
  device_type: "router",
};

function formatRelativeTime(value: string | null): string {
  if (!value) return "Never seen";

  const seconds = Math.max(
    0,
    Math.floor((Date.now() - new Date(value).getTime()) / 1000),
  );
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString([], {
    dateStyle: "short",
    timeStyle: "short",
  });
}

function statusLabel(status: Device["status"]): string {
  return status.toUpperCase();
}

function MetricBars({ metrics }: { metrics: Metric[] }) {
  const ordered = [...metrics].reverse();

  return (
    <div className="metric-chart" aria-label="CPU usage history">
      {ordered.length === 0 ? (
        <div className="empty-chart">No measurements yet</div>
      ) : (
        ordered.map((metric) => (
          <div className="chart-column" key={metric.id} title={formatDate(metric.recorded_at)}>
            <div className="bar-track">
              <div
                className="bar-fill cpu-bar"
                style={{ height: `${Math.max(4, metric.cpu_usage)}%` }}
              />
            </div>
            <span>{Math.round(metric.cpu_usage)}</span>
          </div>
        ))
      )}
    </div>
  );
}

function App() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [form, setForm] = useState<DeviceCreate>(emptyDevice);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const selectedDevice = useMemo(
    () => devices.find((device) => device.id === selectedId) ?? devices[0],
    [devices, selectedId],
  );

  const loadOverview = useCallback(async () => {
    setError(null);
    try {
      const [nextDevices, nextAlerts] = await Promise.all([
        getDevices(),
        getAlerts(),
      ]);
      setDevices(nextDevices);
      setAlerts(nextAlerts);
      setSelectedId((current) => current ?? nextDevices[0]?.id ?? null);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load dashboard");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadMetrics = useCallback(async (deviceId: number) => {
    try {
      setMetrics(await getMetrics(deviceId));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load metrics");
    }
  }, []);

  useEffect(() => {
    void loadOverview();
  }, [loadOverview]);

  useEffect(() => {
    if (selectedDevice) void loadMetrics(selectedDevice.id);
  }, [loadMetrics, selectedDevice]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const created = await createDevice(form);
      setForm(emptyDevice);
      setSelectedId(created.id);
      await loadOverview();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to create device");
    } finally {
      setSubmitting(false);
    }
  }

  const onlineCount = devices.filter((device) => device.status === "online").length;
  const offlineCount = devices.filter((device) => device.status === "offline").length;

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Infrastructure control room</p>
          <h1>NetWatch</h1>
        </div>
        <div className="topbar-actions">
          <span className="connection-state"><span className="state-dot" /> API connected</span>
          <button className="button button-secondary" onClick={() => void loadOverview()}>
            Refresh data
          </button>
        </div>
      </header>

      {error && <div className="error-banner" role="alert">{error}</div>}

      <section className="summary-grid" aria-label="Network summary">
        <div className="summary-card">
          <span>Total devices</span>
          <strong>{devices.length}</strong>
        </div>
        <div className="summary-card summary-online">
          <span>Online</span>
          <strong>{onlineCount}</strong>
        </div>
        <div className="summary-card summary-offline">
          <span>Offline</span>
          <strong>{offlineCount}</strong>
        </div>
        <div className="summary-card summary-alerts">
          <span>Open alerts</span>
          <strong>{alerts.length}</strong>
        </div>
      </section>

      <section className="workspace-grid">
        <section className="panel device-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Inventory</p>
              <h2>Devices</h2>
            </div>
            <span className="count-label">{devices.length} tracked</span>
          </div>

          {loading ? (
            <div className="empty-state">Loading devices...</div>
          ) : devices.length === 0 ? (
            <div className="empty-state">No devices registered.</div>
          ) : (
            <div className="device-list">
              {devices.map((device) => (
                <button
                  className={`device-row ${selectedDevice?.id === device.id ? "selected" : ""}`}
                  key={device.id}
                  onClick={() => setSelectedId(device.id)}
                >
                  <span className={`status-indicator status-${device.status}`} />
                  <span className="device-row-main">
                    <strong>{device.name}</strong>
                    <small>{device.hostname} · {device.ip_address}</small>
                  </span>
                  <span className={`status-text status-text-${device.status}`}>
                    {statusLabel(device.status)}
                  </span>
                </button>
              ))}
            </div>
          )}

          <form className="device-form" onSubmit={handleSubmit}>
            <div className="form-heading">
              <h3>Register device</h3>
              <span>Stored in PostgreSQL</span>
            </div>
            <div className="form-grid">
              <label>
                Name
                <input required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="Router-Fulda" />
              </label>
              <label>
                Hostname
                <input required value={form.hostname} onChange={(event) => setForm({ ...form, hostname: event.target.value })} placeholder="router-fulda" />
              </label>
              <label>
                IP address
                <input required value={form.ip_address} onChange={(event) => setForm({ ...form, ip_address: event.target.value })} placeholder="10.0.0.10" />
              </label>
              <label>
                Type
                <select value={form.device_type} onChange={(event) => setForm({ ...form, device_type: event.target.value as DeviceCreate["device_type"] })}>
                  <option value="router">Router</option>
                  <option value="server">Server</option>
                  <option value="switch">Switch</option>
                </select>
              </label>
            </div>
            <button className="button button-primary" disabled={submitting} type="submit">
              {submitting ? "Registering..." : "Register device"}
            </button>
          </form>
        </section>

        <section className="panel detail-panel">
          {selectedDevice ? (
            <>
              <div className="detail-heading">
                <div>
                  <p className="eyebrow">Selected device</p>
                  <h2>{selectedDevice.name}</h2>
                  <p className="muted">{selectedDevice.device_type} · {selectedDevice.hostname}</p>
                </div>
                <span className={`large-status status-text-${selectedDevice.status}`}>
                  {statusLabel(selectedDevice.status)}
                </span>
              </div>

              <div className="metric-grid">
                <div className="metric-card"><span>CPU</span><strong>{metrics[0] ? `${metrics[0].cpu_usage.toFixed(1)}%` : "--"}</strong></div>
                <div className="metric-card"><span>Memory</span><strong>{metrics[0] ? `${metrics[0].memory_usage.toFixed(1)}%` : "--"}</strong></div>
                <div className="metric-card"><span>Latency</span><strong>{metrics[0] ? `${metrics[0].latency_ms.toFixed(1)} ms` : "--"}</strong></div>
                <div className="metric-card"><span>Last seen</span><strong>{formatRelativeTime(selectedDevice.last_seen)}</strong></div>
              </div>

              <div className="chart-section">
                <div className="section-heading"><h3>CPU history</h3><span>Latest {metrics.length} checks</span></div>
                <MetricBars metrics={metrics} />
              </div>

              <div className="section-heading"><h3>Recent measurements</h3><span>Newest first</span></div>
              <div className="measurement-table">
                {metrics.slice(0, 6).map((metric) => (
                  <div className="measurement-row" key={metric.id}>
                    <span>{formatDate(metric.recorded_at)}</span>
                    <span>{metric.cpu_usage.toFixed(1)}% CPU</span>
                    <span>{metric.memory_usage.toFixed(1)}% MEM</span>
                    <span>{metric.latency_ms.toFixed(1)} ms</span>
                  </div>
                ))}
                {metrics.length === 0 && <div className="empty-state">No history for this device.</div>}
              </div>
            </>
          ) : (
            <div className="empty-state detail-empty">Select a device to inspect its history.</div>
          )}
        </section>
      </section>

      <section className="panel alerts-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Attention queue</p>
            <h2>Open alerts</h2>
          </div>
          <span className="count-label">{alerts.length} unresolved</span>
        </div>
        {alerts.length === 0 ? (
          <div className="empty-state">No unresolved alerts.</div>
        ) : (
          <div className="alert-list">
            {alerts.map((alert) => (
              <div className="alert-row" key={alert.id}>
                <span className={`alert-severity severity-${alert.severity}`} />
                <span className="alert-copy"><strong>{alert.alert_type.replace(/_/g, " ")}</strong><small>{alert.message}</small></span>
                <span className="muted">Device #{alert.device_id}</span>
                <time>{formatDate(alert.created_at)}</time>
              </div>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export default App;
