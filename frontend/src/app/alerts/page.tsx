"use client";

import { useEffect, useState } from "react";
import { Bell, ShieldAlert, CheckCircle, RefreshCw, Clock, AlertTriangle } from "lucide-react";
import { apiFetch } from "@/lib/api";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState("ACTIVE");
  const [typeFilter, setTypeFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (statusFilter) params.append("status", statusFilter);
      if (typeFilter) params.append("alert_type", typeFilter);

      const res = await apiFetch(`/alerts?${params.toString()}`);
      setAlerts(res?.data?.items || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [statusFilter, typeFilter]);

  const handleScan = async () => {
    setChecking(true);
    try {
      await apiFetch("/alerts/check", { method: "POST" });
      await loadAlerts();
    } catch (err: any) {
      alert(err.message || "Failed to trigger scan");
    } finally {
      setChecking(false);
    }
  };

  const handleAcknowledge = async (id: number) => {
    try {
      await apiFetch(`/alerts/${id}/acknowledge`, { method: "PATCH" });
      loadAlerts();
    } catch (err: any) {
      alert(err.message || "Failed to acknowledge");
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Alerts & Compliance Center</h2>
          <p className="text-xs text-slate-500">Real-time alerts for medicines below reorder levels and batches approaching expiration.</p>
        </div>
        <button
          onClick={handleScan}
          disabled={checking}
          className="flex items-center gap-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-md shadow-brand-600/20 transition active:scale-95 disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${checking ? "animate-spin" : ""}`} />
          <span>{checking ? "Scanning Inventory..." : "Scan & Trigger Checks"}</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setStatusFilter("ACTIVE")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              statusFilter === "ACTIVE"
                ? "bg-slate-900 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            Active Alerts
          </button>
          <button
            onClick={() => setStatusFilter("ACKNOWLEDGED")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              statusFilter === "ACKNOWLEDGED"
                ? "bg-slate-900 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            Acknowledged
          </button>
          <button
            onClick={() => setStatusFilter("")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              statusFilter === ""
                ? "bg-slate-900 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            All History
          </button>
        </div>

        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="py-1.5 px-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700"
        >
          <option value="">All Alert Types</option>
          <option value="LOW_STOCK">Low Stock</option>
          <option value="NEAR_EXPIRY">Near Expiry</option>
          <option value="EXPIRED">Expired</option>
        </select>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {loading ? (
          <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center text-xs text-slate-400">
            Checking alert system...
          </div>
        ) : alerts.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center text-xs text-slate-400 flex flex-col items-center gap-2">
            <CheckCircle className="w-8 h-8 text-emerald-500" />
            <span className="font-semibold text-slate-700 text-sm">No Active Alerts</span>
            <span className="text-slate-400">All inventory batches and medicine stock levels are currently compliant.</span>
          </div>
        ) : (
          alerts.map((a) => {
            const isLowStock = a.alert_type === "LOW_STOCK";
            return (
              <div
                key={a.id}
                className="bg-white rounded-2xl border border-slate-200/80 p-4 shadow-sm flex items-center justify-between gap-4 hover:border-slate-300 transition"
              >
                <div className="flex items-center gap-3.5">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                      isLowStock ? "bg-amber-50 text-amber-600" : "bg-rose-50 text-rose-600"
                    }`}
                  >
                    {isLowStock ? <AlertTriangle className="w-5 h-5" /> : <Clock className="w-5 h-5" />}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                          isLowStock ? "bg-amber-100 text-amber-800" : "bg-rose-100 text-rose-800"
                        }`}
                      >
                        {a.alert_type.replace("_", " ")}
                      </span>
                      <span className="text-[11px] text-slate-400">
                        {a.created_at ? new Date(a.created_at).toLocaleString() : ""}
                      </span>
                    </div>
                    <p className="text-xs font-semibold text-slate-800 mt-1">{a.message}</p>
                  </div>
                </div>

                <div className="shrink-0">
                  {a.status === "ACTIVE" ? (
                    <button
                      onClick={() => handleAcknowledge(a.id)}
                      className="px-3.5 py-1.5 text-xs font-semibold text-slate-700 hover:text-white bg-slate-100 hover:bg-brand-600 rounded-lg transition"
                    >
                      Acknowledge
                    </button>
                  ) : (
                    <span className="text-[11px] text-slate-400 font-medium px-2 py-1 bg-slate-50 rounded">
                      Acknowledged
                    </span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
