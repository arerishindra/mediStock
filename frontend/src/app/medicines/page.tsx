"use client";

import { useEffect, useState } from "react";
import { Pill, Plus, Search, Filter, CheckCircle2, X } from "lucide-react";
import { apiFetch } from "@/lib/api";

export default function MedicinesPage() {
  const [medicines, setMedicines] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [loading, setLoading] = useState(true);

  // New Medicine Modal State
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    generic_name: "",
    category_id: "",
    manufacturer: "",
    dosage_form: "Tablet",
    strength: "500mg",
    unit: "tablet",
    reorder_level: "20",
    description: "",
  });
  const [modalError, setModalError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [medRes, catRes] = await Promise.all([
        apiFetch(`/medicines?search=${encodeURIComponent(search)}${selectedCategory ? `&category_id=${selectedCategory}` : ""}`),
        apiFetch("/categories"),
      ]);
      setMedicines(medRes?.data?.items || []);
      setCategories(catRes?.data?.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [search, selectedCategory]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setModalError(null);

    try {
      await apiFetch("/medicines", {
        method: "POST",
        body: JSON.stringify({
          ...formData,
          category_id: parseInt(formData.category_id),
          reorder_level: parseInt(formData.reorder_level) || 10,
        }),
      });
      setShowModal(false);
      setFormData({
        name: "",
        generic_name: "",
        category_id: "",
        manufacturer: "",
        dosage_form: "Tablet",
        strength: "500mg",
        unit: "tablet",
        reorder_level: "20",
        description: "",
      });
      loadData();
    } catch (err: any) {
      setModalError(err.message || "Failed to create medicine");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Medicine Catalog</h2>
          <p className="text-xs text-slate-500">Manage pharmaceutical inventory items, strengths, and categories.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-sm transition active:scale-95"
        >
          <Plus className="w-4 h-4" />
          <span>Add Medicine</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search medicine by name or generic formula..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition"
          />
        </div>

        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="w-full sm:w-48 py-2 px-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {/* Medicines Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200/70 text-slate-500 font-semibold uppercase tracking-wider">
                <th className="py-3 px-5">Medicine & Generic</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Form & Strength</th>
                <th className="py-3 px-4">Unit</th>
                <th className="py-3 px-4 text-center">Reorder Threshold</th>
                <th className="py-3 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">Loading medicines catalog...</td>
                </tr>
              ) : medicines.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">No medicines found matching criteria.</td>
                </tr>
              ) : (
                medicines.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3.5 px-5">
                      <div className="font-semibold text-slate-900">{m.name}</div>
                      <div className="text-[11px] text-slate-500">{m.generic_name || "—"}</div>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-700">{m.category_name || "General"}</td>
                    <td className="py-3.5 px-4 text-slate-600">{m.dosage_form} • {m.strength}</td>
                    <td className="py-3.5 px-4 text-slate-600 capitalize">{m.unit}</td>
                    <td className="py-3.5 px-4 text-center font-medium text-slate-700">{m.reorder_level}</td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        m.is_active ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-slate-100 text-slate-500"
                      }`}>
                        {m.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Medicine Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-slate-900 text-base">Add New Medicine</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {modalError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-50 text-rose-700 border border-rose-200 text-xs">
                {modalError}
              </div>
            )}

            <form onSubmit={handleCreate} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Brand Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Amoxicillin 500mg"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Generic Name</label>
                <input
                  type="text"
                  placeholder="e.g. Amoxicillin Trihydrate"
                  value={formData.generic_name}
                  onChange={(e) => setFormData({ ...formData, generic_name: e.target.value })}
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Category *</label>
                  <select
                    required
                    value={formData.category_id}
                    onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-lg bg-white"
                  >
                    <option value="">Select Category</option>
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Dosage Form *</label>
                  <input
                    type="text"
                    required
                    placeholder="Tablet, Syrup, Injection"
                    value={formData.dosage_form}
                    onChange={(e) => setFormData({ ...formData, dosage_form: e.target.value })}
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Strength *</label>
                  <input
                    type="text"
                    required
                    placeholder="500mg"
                    value={formData.strength}
                    onChange={(e) => setFormData({ ...formData, strength: e.target.value })}
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Unit *</label>
                  <input
                    type="text"
                    required
                    placeholder="tablet"
                    value={formData.unit}
                    onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Reorder Qty</label>
                  <input
                    type="number"
                    min="1"
                    value={formData.reorder_level}
                    onChange={(e) => setFormData({ ...formData, reorder_level: e.target.value })}
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
                  />
                </div>
              </div>

              <div className="pt-3 flex items-center justify-end gap-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-500 rounded-lg transition shadow-md shadow-brand-600/20 disabled:opacity-50"
                >
                  {saving ? "Saving..." : "Create Medicine"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
