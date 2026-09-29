"use client";

import { useEffect, useState } from "react";
import { Boxes, Plus, SlidersHorizontal, AlertCircle, ArrowUpRight, ArrowDownRight, X, Clock } from "lucide-react";
import { apiFetch } from "@/lib/api";

export default function InventoryPage() {
  const [batches, setBatches] = useState<any[]>([]);
  const [medicines, setMedicines] = useState<any[]>([]);
  const [selectedMed, setSelectedMed] = useState<string>("");
  const [loading, setLoading] = useState(true);

  // Adjustment Modal
  const [showAdjustModal, setShowAdjustModal] = useState(false);
  const [adjustBatch, setAdjustBatch] = useState<any | null>(null);
  const [adjustForm, setAdjustForm] = useState({
    adjustment_type: "ADJUSTMENT_IN",
    quantity: "10",
    reason: "Routine inventory count correction",
  });
  const [adjustError, setAdjustError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [invRes, medRes] = await Promise.all([
        apiFetch("/inventory"),
        apiFetch("/medicines"),
      ]);

      setMedicines(medRes?.data?.items || []);

      // If a medicine is selected, fetch its specific batches, or fetch all from first few medicines
      const medList = medRes?.data?.items || [];
      if (selectedMed) {
        const batchRes = await apiFetch(`/inventory/${selectedMed}/batches`);
        setBatches(batchRes?.data?.items || []);
      } else {
        // Collect batches from available medicines
        const allBatches: any[] = [];
        for (const m of medList.slice(0, 10)) {
          try {
            const bRes = await apiFetch(`/inventory/${m.id}/batches`);
            if (bRes?.data?.items) {
              allBatches.push(...bRes.data.items);
            }
          } catch {}
        }
        setBatches(allBatches);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedMed]);

  const handleAdjustSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!adjustBatch) return;
    setSaving(true);
    setAdjustError(null);

    try {
      await apiFetch("/inventory/adjustments", {
        method: "POST",
        body: JSON.stringify({
          batch_id: adjustBatch.id,
          adjustment_type: adjustForm.adjustment_type,
          quantity: parseInt(adjustForm.quantity),
          reason: adjustForm.reason,
        }),
      });
      setShowAdjustModal(false);
      setAdjustBatch(null);
      loadData();
    } catch (err: any) {
      setAdjustError(err.message || "Failed to submit adjustment");
    } finally {
      setSaving(false);
    }
  };

  const getExpiryBadge = (expiryStr: string) => {
    if (!expiryStr) return null;
    const now = new Date();
    const expiry = new Date(expiryStr);
    const diffDays = Math.ceil((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays <= 0) {
      return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800">EXPIRED</span>;
    }
    if (diffDays <= 60) {
      return (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 flex items-center gap-1">
          <Clock className="w-3 h-3" />
          <span>{diffDays}d left</span>
        </span>
      );
    }
    return <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700">Valid</span>;
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Batch Inventory & Expiry</h2>
          <p className="text-xs text-slate-500">Track batch quantities, expiry dates, and execute audit adjustments.</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedMed}
            onChange={(e) => setSelectedMed(e.target.value)}
            className="text-xs py-2 px-3 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-brand-500"
          >
            <option value="">Filter by Medicine...</option>
            {medicines.map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Batches Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200/70 text-slate-500 font-semibold uppercase tracking-wider">
                <th className="py-3 px-5">Batch Number</th>
                <th className="py-3 px-4">Medicine</th>
                <th className="py-3 px-4">Current Stock</th>
                <th className="py-3 px-4">Cost / Selling</th>
                <th className="py-3 px-4">Expiry Date</th>
                <th className="py-3 px-4 text-center">Shelf Status</th>
                <th className="py-3 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">Loading batch records...</td>
                </tr>
              ) : batches.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    No active batches found. Receive a purchase order to populate batches.
                  </td>
                </tr>
              ) : (
                batches.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3.5 px-5 font-mono font-bold text-slate-800">
                      {b.batch_number}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-900">
                      {b.medicine_name || `Medicine #${b.medicine_id}`}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-bold text-slate-900">{b.current_quantity}</span>
                      <span className="text-[11px] text-slate-400 ml-1">/ {b.quantity_received} rcvd</span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-700">
                      ${b.cost_price?.toFixed(2)} / <span className="font-semibold text-emerald-600">${b.selling_price?.toFixed(2)}</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-600">
                      {b.expiry_date || "—"}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      {getExpiryBadge(b.expiry_date)}
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      <button
                        onClick={() => {
                          setAdjustBatch(b);
                          setShowAdjustModal(true);
                        }}
                        className="px-3 py-1.5 rounded-lg border border-slate-200 hover:border-brand-500 hover:text-brand-600 font-semibold text-slate-600 text-xs transition"
                      >
                        Adjust Stock
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Adjustment Modal */}
      {showAdjustModal && adjustBatch && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-bold text-slate-900 text-base">Adjust Batch Stock</h3>
                <p className="text-xs text-slate-500">Batch {adjustBatch.batch_number}</p>
              </div>
              <button onClick={() => setShowAdjustModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {adjustError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-50 text-rose-700 border border-rose-200 text-xs">
                {adjustError}
              </div>
            )}

            <form onSubmit={handleAdjustSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Adjustment Action</label>
                <select
                  value={adjustForm.adjustment_type}
                  onChange={(e) => setAdjustForm({ ...adjustForm, adjustment_type: e.target.value })}
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg bg-white"
                >
                  <option value="ADJUSTMENT_IN">Stock In (Surplus / Recount +)</option>
                  <option value="ADJUSTMENT_OUT">Stock Out (Discrepancy -)</option>
                  <option value="WRITE_OFF">Write Off (Damaged / Broken)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Quantity</label>
                <input
                  type="number"
                  min="1"
                  required
                  value={adjustForm.quantity}
                  onChange={(e) => setAdjustForm({ ...adjustForm, quantity: e.target.value })}
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Current on-hand: <b>{adjustBatch.current_quantity}</b> units
                </span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Reason / Audit Note *</label>
                <textarea
                  required
                  rows={3}
                  value={adjustForm.reason}
                  onChange={(e) => setAdjustForm({ ...adjustForm, reason: e.target.value })}
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
                />
              </div>

              <div className="pt-3 flex items-center justify-end gap-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAdjustModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-500 rounded-lg shadow-md shadow-brand-600/20 disabled:opacity-50"
                >
                  {saving ? "Recording..." : "Record Adjustment"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
