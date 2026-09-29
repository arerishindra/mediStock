"use client";

import { useEffect, useState } from "react";
import { ShoppingCart, Plus, Search, Receipt, CheckCircle2, X, Printer, User } from "lucide-react";
import { apiFetch } from "@/lib/api";

export default function SalesPage() {
  const [sales, setSales] = useState<any[]>([]);
  const [medicines, setMedicines] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // New Sale POS Modal
  const [showModal, setShowModal] = useState(false);
  const [customerName, setCustomerName] = useState("Walk-in Patient");
  const [customerPhone, setCustomerPhone] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("CASH");
  const [discountAmount, setDiscountAmount] = useState("0");
  const [items, setItems] = useState<Array<{ medicine_id: string; quantity: number }>>([
    { medicine_id: "", quantity: 1 },
  ]);
  const [posError, setPosError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Completed Receipt Modal
  const [lastInvoice, setLastInvoice] = useState<any | null>(null);

  const loadSales = async () => {
    try {
      setLoading(true);
      const [salesRes, medRes] = await Promise.all([
        apiFetch("/sales"),
        apiFetch("/medicines"),
      ]);
      setSales(salesRes?.data?.items || []);
      setMedicines(medRes?.data?.items || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSales();
  }, []);

  const addItemRow = () => {
    setItems([...items, { medicine_id: "", quantity: 1 }]);
  };

  const removeItemRow = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: string, value: any) => {
    const next = [...items];
    (next[index] as any)[field] = value;
    setItems(next);
  };

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setPosError(null);

    const validItems = items.filter((i) => i.medicine_id && i.quantity > 0);
    if (validItems.length === 0) {
      setPosError("Please select at least one medicine.");
      setSubmitting(false);
      return;
    }

    try {
      const res = await apiFetch("/sales", {
        method: "POST",
        body: JSON.stringify({
          customer_name: customerName,
          customer_phone: customerPhone || null,
          sale_date: new Date().toISOString().split("T")[0],
          payment_method: paymentMethod,
          discount_amount: parseFloat(discountAmount) || 0,
          items: validItems.map((i) => ({
            medicine_id: parseInt(i.medicine_id),
            quantity: parseInt(i.quantity as any),
          })),
        }),
      });

      setShowModal(false);
      setLastInvoice(res.data);
      setItems([{ medicine_id: "", quantity: 1 }]);
      loadSales();
    } catch (err: any) {
      setPosError(err.message || "Failed to complete transaction");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Point of Sale & Invoices</h2>
          <p className="text-xs text-slate-500">Fast cashier dispensing, automated FIFO batch deductions, and receipts.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-md shadow-brand-600/20 transition active:scale-95"
        >
          <ShoppingCart className="w-4 h-4" />
          <span>New Dispense (Sale)</span>
        </button>
      </div>

      {/* Sales Transactions Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200/70 text-slate-500 font-semibold uppercase tracking-wider">
                <th className="py-3 px-5">Invoice Number</th>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Payment</th>
                <th className="py-3 px-4 text-right">Total Amount</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">Loading sales records...</td>
                </tr>
              ) : sales.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    No sales recorded yet. Click "New Dispense" to start a sale.
                  </td>
                </tr>
              ) : (
                sales.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3.5 px-5 font-mono font-bold text-brand-600">
                      {s.invoice_number}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">{s.sale_date}</td>
                    <td className="py-3.5 px-4 font-medium text-slate-800">
                      {s.customer_name || "Anonymous Patient"}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-md bg-slate-100 font-semibold text-[10px] text-slate-700">
                        {s.payment_method}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right font-bold text-slate-900">
                      ${s.total_amount?.toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {s.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      <button
                        onClick={() => setLastInvoice(s)}
                        className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition"
                        title="View Receipt"
                      >
                        <Receipt className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* POS New Sale Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <ShoppingCart className="w-5 h-5 text-brand-600" />
                <h3 className="font-bold text-slate-900 text-base">New Pharmacy Dispense / POS</h3>
              </div>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {posError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-50 text-rose-700 border border-rose-200 text-xs">
                {posError}
              </div>
            )}

            <form onSubmit={handleCheckout} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Customer Name</label>
                  <input
                    type="text"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Payment Method</label>
                  <select
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-lg bg-white"
                  >
                    <option value="CASH">Cash</option>
                    <option value="CARD">Card</option>
                    <option value="UPI">UPI / Digital</option>
                    <option value="INSURANCE">Insurance</option>
                  </select>
                </div>
              </div>

              {/* Items List */}
              <div className="border border-slate-200 rounded-xl p-3 bg-slate-50 space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-700">Medicines to Dispense (FIFO)</span>
                  <button
                    type="button"
                    onClick={addItemRow}
                    className="text-[11px] font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Item</span>
                  </button>
                </div>

                {items.map((item, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <select
                      required
                      value={item.medicine_id}
                      onChange={(e) => updateItem(idx, "medicine_id", e.target.value)}
                      className="flex-1 text-xs p-2 border border-slate-300 rounded-lg bg-white"
                    >
                      <option value="">Select Medicine...</option>
                      {medicines.map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.name} ({m.dosage_form} - {m.strength})
                        </option>
                      ))}
                    </select>

                    <input
                      type="number"
                      min="1"
                      required
                      placeholder="Qty"
                      value={item.quantity}
                      onChange={(e) => updateItem(idx, "quantity", parseInt(e.target.value) || 1)}
                      className="w-20 text-xs p-2 border border-slate-300 rounded-lg text-center"
                    />

                    {items.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeItemRow(idx)}
                        className="text-slate-400 hover:text-rose-500 p-1"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {/* Discount */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Discount Amount ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={discountAmount}
                  onChange={(e) => setDiscountAmount(e.target.value)}
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
                />
              </div>

              <div className="pt-3 flex items-center justify-end gap-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2.5 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-500 rounded-xl shadow-md shadow-brand-600/20 disabled:opacity-50"
                >
                  {submitting ? "Processing FIFO..." : "Complete & Print Invoice"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Invoice Receipt Modal */}
      {lastInvoice && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-slate-200 text-slate-800">
            <div className="text-center pb-4 border-b border-dashed border-slate-300">
              <div className="w-10 h-10 rounded-full bg-brand-50 text-brand-600 mx-auto flex items-center justify-center mb-2">
                <CheckCircle2 className="w-6 h-6 text-brand-600" />
              </div>
              <h3 className="font-bold text-lg">MediStock Pharmacy</h3>
              <p className="text-[11px] text-slate-500">Official Dispensing Receipt</p>
            </div>

            <div className="py-4 space-y-2 text-xs border-b border-dashed border-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-500">Invoice:</span>
                <span className="font-mono font-bold">{lastInvoice.invoice_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Date:</span>
                <span>{lastInvoice.sale_date}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Patient:</span>
                <span className="font-medium">{lastInvoice.customer_name || "Walk-in"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Payment:</span>
                <span className="font-medium">{lastInvoice.payment_method}</span>
              </div>
            </div>

            <div className="py-4 space-y-2 text-xs">
              <div className="flex justify-between text-slate-500">
                <span>Subtotal:</span>
                <span>${lastInvoice.subtotal?.toFixed(2) || lastInvoice.total_amount?.toFixed(2)}</span>
              </div>
              {lastInvoice.discount_amount > 0 && (
                <div className="flex justify-between text-rose-600">
                  <span>Discount:</span>
                  <span>-${lastInvoice.discount_amount?.toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between text-sm font-bold pt-2 border-t border-slate-200">
                <span>Total Paid:</span>
                <span className="text-brand-600">${lastInvoice.total_amount?.toFixed(2)}</span>
              </div>
            </div>

            <div className="pt-4 flex gap-2">
              <button
                onClick={() => setLastInvoice(null)}
                className="flex-1 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl"
              >
                Close
              </button>
              <button
                onClick={() => window.print()}
                className="flex-1 py-2 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-500 rounded-xl flex items-center justify-center gap-1.5 shadow-sm"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>Print</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
