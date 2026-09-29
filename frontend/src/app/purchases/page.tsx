"use client";

import { useEffect, useState } from "react";
import { Truck, Plus, PackageCheck, X, CheckCircle2, AlertCircle } from "lucide-react";
import { apiFetch } from "@/lib/api";

export default function PurchasesPage() {
  const [purchases, setPurchases] = useState<any[]>([]);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [medicines, setMedicines] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // New PO Modal
  const [showPOModal, setShowPOModal] = useState(false);
  const [supplierId, setSupplierId] = useState("");
  const [notes, setNotes] = useState("");
  const [poItems, setPoItems] = useState<Array<{ medicine_id: string; quantity: number; unit_cost: number }>>([
    { medicine_id: "", quantity: 50, unit_cost: 2.0 },
  ]);
  const [poError, setPoError] = useState<string | null>(null);
  const [creatingPO, setCreatingPO] = useState(false);

  // Receive PO Modal
  const [receiveTarget, setReceiveTarget] = useState<any | null>(null);
  const [receiveData, setReceiveData] = useState<any[]>([]);
  const [receiveError, setReceiveError] = useState<string | null>(null);
  const [receiving, setReceiving] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [pRes, sRes, mRes] = await Promise.all([
        apiFetch("/purchases"),
        apiFetch("/suppliers"),
        apiFetch("/medicines"),
      ]);
      setPurchases(pRes?.data?.items || []);
      setSuppliers(sRes?.data?.items || []);
      setMedicines(mRes?.data?.items || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const addPORow = () => {
    setPoItems([...poItems, { medicine_id: "", quantity: 50, unit_cost: 2.0 }]);
  };

  const removePORow = (index: number) => {
    setPoItems(poItems.filter((_, i) => i !== index));
  };

  const updatePOItem = (index: number, field: string, value: any) => {
    const next = [...poItems];
    (next[index] as any)[field] = value;
    setPoItems(next);
  };

  const handleCreatePO = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreatingPO(true);
    setPoError(null);

    const validItems = poItems.filter((i) => i.medicine_id && i.quantity > 0 && i.unit_cost > 0);
    if (validItems.length === 0) {
      setPoError("Please add at least one valid item.");
      setCreatingPO(false);
      return;
    }

    try {
      await apiFetch("/purchases", {
        method: "POST",
        body: JSON.stringify({
          supplier_id: parseInt(supplierId),
          purchase_date: new Date().toISOString().split("T")[0],
          notes,
          items: validItems.map((i) => ({
            medicine_id: parseInt(i.medicine_id),
            quantity: parseInt(i.quantity as any),
            unit_cost: parseFloat(i.unit_cost as any),
          })),
        }),
      });

      setShowPOModal(false);
      setPoItems([{ medicine_id: "", quantity: 50, unit_cost: 2.0 }]);
      loadData();
    } catch (err: any) {
      setPoError(err.message || "Failed to create PO");
    } finally {
      setCreatingPO(false);
    }
  };

  const openReceiveModal = (po: any) => {
    setReceiveTarget(po);
    // Initialize receive fields for each item
    const futureDate = new Date();
    futureDate.setFullYear(futureDate.getFullYear() + 1);

    setReceiveData(
      po.items.map((pi: any) => ({
        purchase_item_id: pi.id,
        quantity_received: pi.quantity - (pi.quantity_received || 0),
        batch_number: `BATCH-${Date.now().toString().slice(-6)}`,
        expiry_date: futureDate.toISOString().split("T")[0],
        selling_price: (pi.unit_cost * 1.5).toFixed(2),
      }))
    );
    setReceiveError(null);
  };

  const handleReceiveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!receiveTarget) return;
    setReceiving(true);
    setReceiveError(null);

    try {
      await apiFetch(`/purchases/${receiveTarget.id}/receive`, {
        method: "POST",
        body: JSON.stringify({
          items: receiveData.map((r) => ({
            purchase_item_id: r.purchase_item_id,
            quantity_received: parseInt(r.quantity_received),
            batch_number: r.batch_number,
            expiry_date: r.expiry_date,
            selling_price: parseFloat(r.selling_price),
          })),
        }),
      });

      setReceiveTarget(null);
      loadData();
    } catch (err: any) {
      setReceiveError(err.message || "Failed to receive goods");
    } finally {
      setReceiving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Purchase Orders & Receiving</h2>
          <p className="text-xs text-slate-500">Create procurement orders and receive batches with automated stock updates.</p>
        </div>
        <button
          onClick={() => setShowPOModal(true)}
          className="flex items-center gap-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-md shadow-brand-600/20 transition active:scale-95"
        >
          <Plus className="w-4 h-4" />
          <span>New Purchase Order</span>
        </button>
      </div>

      {/* PO Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200/70 text-slate-500 font-semibold uppercase tracking-wider">
                <th className="py-3 px-5">PO Number</th>
                <th className="py-3 px-4">Supplier</th>
                <th className="py-3 px-4">Order Date</th>
                <th className="py-3 px-4 text-right">Total Amount</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">Loading purchase orders...</td>
                </tr>
              ) : purchases.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    No purchase orders found. Click "New Purchase Order" to procure inventory.
                  </td>
                </tr>
              ) : (
                purchases.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3.5 px-5 font-mono font-bold text-slate-900">
                      {p.purchase_number}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-800">
                      {p.supplier_name || `Supplier #${p.supplier_id}`}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">{p.purchase_date}</td>
                    <td className="py-3.5 px-4 text-right font-bold text-slate-900">
                      ${p.total_amount?.toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          p.status === "RECEIVED"
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                            : p.status === "ORDERED"
                            ? "bg-blue-50 text-blue-700 border border-blue-200"
                            : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {p.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      {p.status !== "RECEIVED" && p.status !== "CANCELLED" && (
                        <button
                          onClick={() => openReceiveModal(p)}
                          className="flex items-center gap-1.5 ml-auto px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold transition"
                        >
                          <PackageCheck className="w-3.5 h-3.5" />
                          <span>Receive Goods</span>
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* New Purchase Order Modal */}
      {showPOModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">New Procurement Order (PO)</h3>
              <button onClick={() => setShowPOModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {poError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-50 text-rose-700 border border-rose-200 text-xs">
                {poError}
              </div>
            )}

            <form onSubmit={handleCreatePO} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Select Supplier *</label>
                <select
                  required
                  value={supplierId}
                  onChange={(e) => setSupplierId(e.target.value)}
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg bg-white"
                >
                  <option value="">Choose Supplier...</option>
                  {suppliers.map((s) => (
                    <option key={s.id} value={s.id}>{s.name} ({s.contact_person || "Contact"})</option>
                  ))}
                </select>
              </div>

              {/* Items */}
              <div className="border border-slate-200 rounded-xl p-3 bg-slate-50 space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-700">Order Items</span>
                  <button
                    type="button"
                    onClick={addPORow}
                    className="text-[11px] font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Item</span>
                  </button>
                </div>

                {poItems.map((item, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <select
                      required
                      value={item.medicine_id}
                      onChange={(e) => updatePOItem(idx, "medicine_id", e.target.value)}
                      className="flex-1 text-xs p-2 border border-slate-300 rounded-lg bg-white"
                    >
                      <option value="">Select Medicine...</option>
                      {medicines.map((m) => (
                        <option key={m.id} value={m.id}>{m.name}</option>
                      ))}
                    </select>

                    <input
                      type="number"
                      min="1"
                      required
                      placeholder="Qty"
                      value={item.quantity}
                      onChange={(e) => updatePOItem(idx, "quantity", parseInt(e.target.value) || 1)}
                      className="w-20 text-xs p-2 border border-slate-300 rounded-lg text-center"
                    />

                    <input
                      type="number"
                      step="0.01"
                      min="0.01"
                      required
                      placeholder="Cost $"
                      value={item.unit_cost}
                      onChange={(e) => updatePOItem(idx, "unit_cost", parseFloat(e.target.value) || 0)}
                      className="w-24 text-xs p-2 border border-slate-300 rounded-lg text-right"
                    />

                    {poItems.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removePORow(idx)}
                        className="text-slate-400 hover:text-rose-500 p-1"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Procurement Notes</label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Standard monthly replenishment"
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
                />
              </div>

              <div className="pt-3 flex items-center justify-end gap-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowPOModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creatingPO}
                  className="px-5 py-2.5 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-500 rounded-xl shadow-md shadow-brand-600/20 disabled:opacity-50"
                >
                  {creatingPO ? "Creating PO..." : "Issue Purchase Order"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Receive PO Modal */}
      {receiveTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-bold text-slate-900 text-base">Receive Shipment into Batches</h3>
                <p className="text-xs text-slate-500">Order: {receiveTarget.purchase_number}</p>
              </div>
              <button onClick={() => setReceiveTarget(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {receiveError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-50 text-rose-700 border border-rose-200 text-xs">
                {receiveError}
              </div>
            )}

            <form onSubmit={handleReceiveSubmit} className="space-y-4">
              <div className="space-y-3">
                {receiveData.map((item, idx) => (
                  <div key={idx} className="p-3 border border-slate-200 rounded-xl bg-slate-50 space-y-2">
                    <div className="text-xs font-bold text-slate-800">
                      Receiving Item #{item.purchase_item_id}
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 mb-1">Batch Code *</label>
                        <input
                          type="text"
                          required
                          value={item.batch_number}
                          onChange={(e) => {
                            const next = [...receiveData];
                            next[idx].batch_number = e.target.value;
                            setReceiveData(next);
                          }}
                          className="w-full p-1.5 border border-slate-300 rounded bg-white text-xs"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 mb-1">Qty Received *</label>
                        <input
                          type="number"
                          min="1"
                          required
                          value={item.quantity_received}
                          onChange={(e) => {
                            const next = [...receiveData];
                            next[idx].quantity_received = e.target.value;
                            setReceiveData(next);
                          }}
                          className="w-full p-1.5 border border-slate-300 rounded bg-white text-xs text-center"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 mb-1">Expiry Date *</label>
                        <input
                          type="date"
                          required
                          value={item.expiry_date}
                          onChange={(e) => {
                            const next = [...receiveData];
                            next[idx].expiry_date = e.target.value;
                            setReceiveData(next);
                          }}
                          className="w-full p-1.5 border border-slate-300 rounded bg-white text-xs"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 mb-1">Retail Price ($) *</label>
                        <input
                          type="number"
                          step="0.01"
                          min="0.01"
                          required
                          value={item.selling_price}
                          onChange={(e) => {
                            const next = [...receiveData];
                            next[idx].selling_price = e.target.value;
                            setReceiveData(next);
                          }}
                          className="w-full p-1.5 border border-slate-300 rounded bg-white text-xs text-right"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-3 flex items-center justify-end gap-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setReceiveTarget(null)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={receiving}
                  className="px-5 py-2.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-xl shadow-md shadow-emerald-600/20 disabled:opacity-50"
                >
                  {receiving ? "Processing Receiving..." : "Confirm & Update Inventory"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
