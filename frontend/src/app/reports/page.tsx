"use client";

import { useEffect, useState } from "react";
import { BarChart3, TrendingUp, History, Clock, FileDown, ShieldCheck } from "lucide-react";
import { apiFetch } from "@/lib/api";

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState<"inventory" | "expiry" | "ledger">("inventory");
  const [invReport, setInvReport] = useState<any[]>([]);
  const [expiryReport, setExpiryReport] = useState<any[]>([]);
  const [movements, setMovements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadReports() {
      try {
        setLoading(true);
        if (activeTab === "inventory") {
          const res = await apiFetch("/reports/inventory");
          setInvReport(res?.data?.items || []);
        } else if (activeTab === "expiry") {
          const res = await apiFetch("/reports/expiry?days=90");
          setExpiryReport(res?.data?.items || []);
        } else if (activeTab === "ledger") {
          const res = await apiFetch("/stock-movements?page_size=50");
          setMovements(res?.data?.items || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    loadReports();
  }, [activeTab]);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Reports & Movement Ledger</h2>
          <p className="text-xs text-slate-500">Full audit traceability, valuation reports, and expiration forecasting.</p>
        </div>
        <button
          onClick={() => window.print()}
          className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-sm transition active:scale-95"
        >
          <FileDown className="w-4 h-4" />
          <span>Export / Print Report</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-3">
        <button
          onClick={() => setActiveTab("inventory")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
            activeTab === "inventory"
              ? "bg-brand-600 text-white shadow-sm shadow-brand-600/20"
              : "text-slate-600 hover:bg-slate-100"
          }`}
        >
          <TrendingUp className="w-4 h-4" />
          <span>Inventory Valuation</span>
        </button>
        <button
          onClick={() => setActiveTab("expiry")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
            activeTab === "expiry"
              ? "bg-brand-600 text-white shadow-sm shadow-brand-600/20"
              : "text-slate-600 hover:bg-slate-100"
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>Expiry Risk (90 Days)</span>
        </button>
        <button
          onClick={() => setActiveTab("ledger")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
            activeTab === "ledger"
              ? "bg-brand-600 text-white shadow-sm shadow-brand-600/20"
              : "text-slate-600 hover:bg-slate-100"
          }`}
        >
          <History className="w-4 h-4" />
          <span>Stock Movement Ledger</span>
        </button>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-sm">
        {loading ? (
          <div className="py-16 text-center text-xs text-slate-400">Loading audit data...</div>
        ) : activeTab === "inventory" ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200/70 text-slate-500 font-semibold uppercase tracking-wider">
                  <th className="py-3 px-5">Medicine</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4 text-center">Batch Count</th>
                  <th className="py-3 px-4 text-right">Units on Hand</th>
                  <th className="py-3 px-5 text-right">Total Valuation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {invReport.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-slate-400">No inventory valuation records found.</td>
                  </tr>
                ) : (
                  invReport.map((r, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/70 transition">
                      <td className="py-3.5 px-5 font-semibold text-slate-900">{r.medicine_name || r.name}</td>
                      <td className="py-3.5 px-4 text-slate-600">{r.category_name || "General"}</td>
                      <td className="py-3.5 px-4 text-center font-medium text-slate-700">{r.batch_count || 1}</td>
                      <td className="py-3.5 px-4 text-right font-bold text-slate-900">{r.total_stock || r.total_quantity}</td>
                      <td className="py-3.5 px-5 text-right font-bold text-brand-600">
                        ${(r.total_value || 0).toFixed(2)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        ) : activeTab === "expiry" ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200/70 text-slate-500 font-semibold uppercase tracking-wider">
                  <th className="py-3 px-5">Batch Number</th>
                  <th className="py-3 px-4">Medicine</th>
                  <th className="py-3 px-4">Expiry Date</th>
                  <th className="py-3 px-4 text-center">Days Remaining</th>
                  <th className="py-3 px-5 text-right">Units at Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {expiryReport.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-slate-400">
                      No batches expiring within the next 90 days.
                    </td>
                  </tr>
                ) : (
                  expiryReport.map((b, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/70 transition">
                      <td className="py-3.5 px-5 font-mono font-bold text-slate-800">{b.batch_number}</td>
                      <td className="py-3.5 px-4 font-medium text-slate-900">{b.medicine_name}</td>
                      <td className="py-3.5 px-4 font-mono text-rose-600 font-semibold">{b.expiry_date}</td>
                      <td className="py-3.5 px-4 text-center">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
                          {b.days_until_expiry || "Soon"} days
                        </span>
                      </td>
                      <td className="py-3.5 px-5 text-right font-bold text-slate-900">{b.current_quantity}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200/70 text-slate-500 font-semibold uppercase tracking-wider">
                  <th className="py-3 px-5">Timestamp</th>
                  <th className="py-3 px-4">Movement Type</th>
                  <th className="py-3 px-4">Batch ID</th>
                  <th className="py-3 px-4 text-right">Signed Qty</th>
                  <th className="py-3 px-4 text-right">Qty After</th>
                  <th className="py-3 px-5">Notes / Reference</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {movements.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-400">No stock movements recorded yet.</td>
                  </tr>
                ) : (
                  movements.map((m) => (
                    <tr key={m.id} className="hover:bg-slate-50/70 transition">
                      <td className="py-3.5 px-5 text-slate-500">
                        {m.created_at ? new Date(m.created_at).toLocaleString() : "—"}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="font-semibold text-slate-800">{m.movement_type}</span>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-slate-600">#{m.batch_id}</td>
                      <td
                        className={`py-3.5 px-4 text-right font-bold ${
                          m.quantity > 0 ? "text-emerald-600" : "text-rose-600"
                        }`}
                      >
                        {m.quantity > 0 ? `+${m.quantity}` : m.quantity}
                      </td>
                      <td className="py-3.5 px-4 text-right font-semibold text-slate-800">{m.quantity_after}</td>
                      <td className="py-3.5 px-5 text-slate-500 truncate max-w-xs">{m.notes || m.reference_type}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
