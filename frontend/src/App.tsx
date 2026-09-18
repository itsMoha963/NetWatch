import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity, ArrowRight, Check, CheckCircle2, ChevronDown, Clock3,
  Cpu, HardDrive, Moon, Network, Plus, RefreshCw, Router, Search,
  Server, Sun, TriangleAlert, Wifi, X,
} from "lucide-react";

import { createDevice, getAlerts, getDevices, getMetrics } from "./api";
import type { Alert, Device, DeviceCreate, Metric } from "./types";

const emptyDevice: DeviceCreate = {
  name: "", hostname: "", ip_address: "", device_type: "router",
};

function formatRelativeTime(value: string | null): string {
  if (!value) return "Never seen";
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 1000));
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString([], { dateStyle: "short", timeStyle: "short" });
}

function formatTime(value: string): string {
  return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function DeviceIcon({ type }: { type: Device["device_type"] }) {
  const Icon = type === "server" ? Server : type === "switch" ? Network : Router;
  return <Icon size={18} aria-hidden="true" />;
}

function Status({ status }: { status: Device["status"] }) {
  return <span className={`device-status status-${status}`}><span className="status-dot" />{status}</span>;
}

function MetricHistory({ metrics, loading }: { metrics: Metric[]; loading: boolean }) {
  const [view, setView] = useState<"cpu_usage" | "memory_usage">("cpu_usage");
  const ordered = [...metrics].reverse();

  return (
    <section className="history-section" aria-label="Metric history">
      <div className="section-heading">
        <h3>Performance</h3>
        <div className="segmented-control" aria-label="History metric">
          <button type="button" aria-pressed={view === "cpu_usage"} onClick={() => setView("cpu_usage")}>CPU</button>
          <button type="button" aria-pressed={view === "memory_usage"} onClick={() => setView("memory_usage")}>Memory</button>
        </div>
      </div>
      <div className="chart-caption"><span>Usage, %</span><span>Latest {metrics.length} measurements</span></div>
      <div className="chart-layout">
        <div className="chart-axis" aria-hidden="true"><span>100</span><span>50</span><span>0</span></div>
        <div className="metric-chart" role="img" aria-label={`${view === "cpu_usage" ? "CPU" : "Memory"} usage history, from oldest to newest`} aria-busy={loading}>
          <div className="chart-grid" aria-hidden="true"><span /><span /><span /></div>
          {loading || ordered.length === 0 ? (
            <div className="empty-chart">{loading ? "Loading measurements..." : "No measurements yet"}</div>
          ) : ordered.map((metric) => (
            <div className="chart-column" key={metric.id}>
              <div className="bar-fill" style={{ height: `${metric[view]}%` }} />
              <span className="chart-tooltip">{formatTime(metric.recorded_at)} · {metric[view].toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
      <div className="chart-times" aria-hidden="true">
        <span>{ordered[0] ? formatTime(ordered[0].recorded_at) : "--"}</span>
        <span>{ordered.length > 1 ? formatTime(ordered[ordered.length - 1].recorded_at) : "--"}</span>
      </div>
    </section>
  );
}

function App() {
  const [theme, setTheme] = useState<"dark" | "light">(() =>
    document.documentElement.dataset.theme === "light" ? "light" : "dark",
  );
  const [devices, setDevices] = useState<Device[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [metricsDeviceId, setMetricsDeviceId] = useState<number | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [form, setForm] = useState<DeviceCreate>(emptyDevice);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [metricsLoading, setMetricsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute(
      "content", theme === "dark" ? "#151515" : "#ffffff",
    );
    try {
      localStorage.setItem("netwatch-theme", theme);
    } catch {
      // Switching still works when the browser blocks storage.
    }
  }, [theme]);

  const selectedDevice = useMemo(
    () => devices.find((device) => device.id === selectedId) ?? devices[0],
    [devices, selectedId],
  );
  const visibleMetrics = selectedDevice?.id === metricsDeviceId ? metrics : [];
  const visibleDevices = devices.filter((device) =>
    [device.name, device.hostname, device.ip_address].some((value) => value.toLowerCase().includes(query.toLowerCase())),
  );

  const loadOverview = useCallback(async () => {
    setRefreshing(true);
    setError(null);
    try {
      const [nextDevices, nextAlerts] = await Promise.all([getDevices(), getAlerts()]);
      setDevices(nextDevices);
      setAlerts(nextAlerts);
      setSelectedId((current) => current ?? nextDevices[0]?.id ?? null);
      setConnected(true);
      setUpdatedAt(new Date());
    } catch (loadError) {
      setConnected(false);
      setError(loadError instanceof Error ? loadError.message : "Unable to load dashboard");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { void loadOverview(); }, [loadOverview]);

  useEffect(() => {
    if (!selectedDevice) return;
    let cancelled = false;
    const deviceId = selectedDevice.id;
    setMetricsLoading(true);
    setMetricsDeviceId(null);
    getMetrics(deviceId).then((nextMetrics) => {
      if (!cancelled) {
        setMetrics(nextMetrics);
        setMetricsDeviceId(deviceId);
      }
    }).catch((loadError: unknown) => {
      if (!cancelled) setError(loadError instanceof Error ? loadError.message : "Unable to load metrics");
    }).finally(() => { if (!cancelled) setMetricsLoading(false); });
    return () => { cancelled = true; };
  }, [selectedDevice]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      const created = await createDevice(form);
      setForm(emptyDevice);
      setQuery("");
      setSelectedId(created.id);
      setShowForm(false);
      await loadOverview();
    } catch (submitError) {
      setFormError(submitError instanceof Error ? submitError.message : "Unable to create device");
    } finally {
      setSubmitting(false);
    }
  }

  const onlineCount = devices.filter((device) => device.status === "online").length;
  const offlineCount = devices.filter((device) => device.status === "offline").length;
  const latest = visibleMetrics[0];

  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand"><span className="brand-mark"><Network size={21} strokeWidth={1.6} aria-hidden="true" /></span><span>NetWatch</span><span className="brand-divider" /><span className="workspace-label">Workspace</span></div>
          <div className="topbar-actions">
            <div className="connection-state" role="status"><span className={`connection-dot ${connected ? "connected" : ""}`} />{loading ? "Connecting" : connected ? "API connected" : "API unavailable"}</div>
            <button
              className="icon-button"
              type="button"
              role="switch"
              aria-label="Dark mode"
              aria-checked={theme === "dark"}
              title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              {theme === "dark" ? <Sun size={17} aria-hidden="true" /> : <Moon size={17} aria-hidden="true" />}
            </button>
          </div>
        </div>
      </header>

      <main className="app-shell">
        <div className="page-heading">
          <div><p className="eyebrow">Monitoring</p><h1>Network overview</h1></div>
          <div className="page-actions">
            {updatedAt && <span className="updated-at">Updated {updatedAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>}
            <button className="icon-button" type="button" title="Refresh data" aria-label="Refresh data" disabled={refreshing} onClick={() => void loadOverview()}><RefreshCw size={17} className={refreshing ? "spinning" : ""} /></button>
            <button className="button button-primary" type="button" aria-expanded={showForm} aria-controls="register-device" onClick={() => { setShowForm(!showForm); setFormError(null); }}><Plus size={16} />Add device</button>
          </div>
        </div>

        {error && <div className="error-banner" role="alert"><TriangleAlert size={17} /><span>{error}</span></div>}

        <section className="summary-grid" aria-label="Network summary">
          <div className="summary-item"><span><Server size={15} />Total devices</span><strong>{loading ? "--" : devices.length}</strong></div>
          <div className="summary-item"><span><span className="small-dot dot-online" />Online</span><strong>{loading ? "--" : onlineCount}</strong></div>
          <div className="summary-item"><span><span className="small-dot dot-offline" />Offline</span><strong>{loading ? "--" : offlineCount}</strong></div>
          <div className="summary-item"><span><TriangleAlert size={15} />Open alerts</span><strong>{loading ? "--" : `${alerts.length}${alerts.length === 50 ? "+" : ""}`}</strong></div>
        </section>

        {showForm && (
          <form id="register-device" className="device-form" onSubmit={handleSubmit}>
            <div className="section-heading"><h2>Register device</h2><button className="icon-button" aria-label="Close registration" title="Close registration" type="button" disabled={submitting} onClick={() => setShowForm(false)}><X size={17} /></button></div>
            <div className="form-grid">
              <label>Name<input autoFocus required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="Router-Fulda" /></label>
              <label>Hostname<input required value={form.hostname} onChange={(event) => setForm({ ...form, hostname: event.target.value })} placeholder="router-fulda" /></label>
              <label>IP address<input required value={form.ip_address} onChange={(event) => setForm({ ...form, ip_address: event.target.value })} placeholder="10.0.0.10" /></label>
              <label>Type<span className="select-wrapper"><select aria-label="Type" value={form.device_type} onChange={(event) => setForm({ ...form, device_type: event.target.value as DeviceCreate["device_type"] })}><option value="router">Router</option><option value="server">Server</option><option value="switch">Switch</option></select><ChevronDown size={15} /></span></label>
            </div>
            {formError && <p className="form-error" role="alert">{formError}</p>}
            <div className="form-actions"><button type="button" className="button button-secondary" disabled={submitting} onClick={() => setShowForm(false)}>Cancel</button><button className="button button-primary" disabled={submitting} type="submit"><Check size={16} />{submitting ? "Registering..." : "Register device"}</button></div>
          </form>
        )}

        <div className="workspace-grid">
          <section className="device-panel" aria-label="Device inventory">
            <div className="section-heading"><h2>Devices <span className="count-label">{devices.length}</span></h2><Network size={17} className="muted" /></div>
            <label className="search-field"><Search size={16} aria-hidden="true" /><input aria-label="Search devices" type="search" placeholder="Search devices..." value={query} onChange={(event) => setQuery(event.target.value)} /></label>
            {loading ? <div className="empty-state">Loading devices...</div> : visibleDevices.length === 0 ? <div className="empty-state">{devices.length ? "No matching devices." : "No devices registered."}</div> : (
              <div className="device-list">{visibleDevices.map((device) => (
                <button className={`device-row ${selectedDevice?.id === device.id ? "selected" : ""}`} type="button" key={device.id} aria-pressed={selectedDevice?.id === device.id} onClick={() => setSelectedId(device.id)}>
                  <span className="device-icon"><DeviceIcon type={device.device_type} /></span>
                  <span className="device-row-main"><strong>{device.name}</strong><small>{device.ip_address}</small></span>
                  <span className={`inventory-dot dot-${device.status}`} title={device.status}><span className="sr-only">{device.status}</span></span>
                </button>
              ))}</div>
            )}
          </section>

          <section className="detail-panel" aria-label="Device details">
            {selectedDevice ? (
              <>
                <div className="detail-heading">
                  <div><div className="device-meta"><span>{selectedDevice.device_type}</span><span>/</span><span>{selectedDevice.ip_address}</span></div><h2>{selectedDevice.name}</h2><p className="hostname">{selectedDevice.hostname}</p></div>
                  <Status status={selectedDevice.status} />
                </div>
                <div className="metric-grid">
                  <div className="metric-item"><span><Cpu size={14} />CPU</span><strong>{latest ? latest.cpu_usage.toFixed(1) : "--"}<small>{latest && "%"}</small></strong></div>
                  <div className="metric-item"><span><HardDrive size={14} />Memory</span><strong>{latest ? latest.memory_usage.toFixed(1) : "--"}<small>{latest && "%"}</small></strong></div>
                  <div className="metric-item"><span><Wifi size={14} />Latency</span><strong>{latest ? latest.latency_ms.toFixed(1) : "--"}<small>{latest && "ms"}</small></strong></div>
                  <div className="metric-item"><span><Clock3 size={14} />Last seen</span><strong className="last-seen">{formatRelativeTime(selectedDevice.last_seen)}</strong></div>
                </div>
                <MetricHistory metrics={visibleMetrics} loading={metricsLoading} />
                <section className="measurements-section">
                  <div className="section-heading"><h3>Recent measurements</h3><span className="table-note"><Clock3 size={13} />Newest first</span></div>
                  <div className="table-scroll"><table><thead><tr><th scope="col">Time</th><th scope="col">CPU</th><th scope="col">Memory</th><th scope="col">Latency</th></tr></thead><tbody>{visibleMetrics.slice(0, 5).map((metric) => <tr key={metric.id}><td>{formatDate(metric.recorded_at)}</td><td>{metric.cpu_usage.toFixed(1)}<span className="unit">%</span></td><td>{metric.memory_usage.toFixed(1)}<span className="unit">%</span></td><td>{metric.latency_ms.toFixed(1)}<span className="unit">ms</span></td></tr>)}</tbody></table></div>
                  {visibleMetrics.length === 0 && <div className="empty-state">{metricsLoading ? "Loading history..." : "No history for this device."}</div>}
                </section>
              </>
            ) : <div className="empty-state detail-empty"><Activity size={26} /><span>No device selected</span></div>}
          </section>
        </div>

        <section className="alerts-section" aria-label="Open alerts">
          <div className="section-heading"><h2>Open alerts <span className="count-label">{alerts.length}{alerts.length === 50 ? "+" : ""}</span></h2><span className="muted">Unresolved</span></div>
          {loading ? <div className="empty-state">Loading alerts...</div> : alerts.length === 0 ? <div className="alerts-empty"><CheckCircle2 size={21} /><div><strong>{connected ? "All clear" : "Alerts unavailable"}</strong><p>{connected ? "No unresolved alerts." : "Refresh to try again."}</p></div></div> : (
            <div className="alert-list">{alerts.map((alert) => (
              <div className="alert-row" key={alert.id}>
                <span className={`severity-label severity-${alert.severity}`}><TriangleAlert size={13} />{alert.severity}</span>
                <span className="alert-copy"><strong>{alert.alert_type.replace(/_/g, " ")}</strong><small>{alert.message}</small></span>
                <button className="alert-device" type="button" onClick={() => { setQuery(""); setSelectedId(alert.device_id); document.querySelector(".detail-panel")?.scrollIntoView({ behavior: "smooth", block: "start" }); }}>{devices.find((device) => device.id === alert.device_id)?.name ?? `Device #${alert.device_id}`}<ArrowRight size={14} /></button>
                <time dateTime={alert.created_at}>{formatDate(alert.created_at)}</time>
              </div>
            ))}</div>
          )}
        </section>
        <footer className="page-footer"><span>NetWatch</span><span><Activity size={13} />Simulated monitoring</span></footer>
      </main>
    </>
  );
}

export default App;
