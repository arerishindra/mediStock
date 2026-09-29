"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Boxes,
  AlertTriangle,
  Clock,
  TrendingUp,
  ArrowUpRight,
  PlusCircle,
  ShoppingCart,
  Pill,
  ShieldAlert,
  ChevronRight,
} from "lucide-react";
import { apiFetch } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalValue: 0,
    totalItems: 0,
    lowStockCount: 0,
    expiringCount: 0,
  });
  const [inventory, setInventory] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [invRes, alertRes] = await Promise.all([
          apiFetch("/inventory").catch(() => ({ data: { items: [] } })),
          apiFetch("/alerts?status=ACTIVE").catch(() => ({ data: { items: [] } })),
        ]);

        const items = invRes?.data?.items || [];
        const alertList = alertRes?.data?.items || [];

        const totalVal = items.reduce((acc: number, item: any) => acc + (item.total_value || 0), 0);
        const lowStock = alertList.filter((a: any) => a.alert_type === "LOW_STOCK").length;
        const expiring = alertList.filter((a: any) => a.alert_type === "NEAR_EXPIRY").length;

        setStats({
          totalValue: totalVal,
          totalItems: items.length,
          lowStockCount: lowStock,
          expiringCount: expiring,
        });

        setInventory(items.slice(0, 6)); // Top 6
        setAlerts(alertList.slice(0, 4));
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  return (
    <div className="space-y-8">
      {/* Top Banner & Quick Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 to-slate-850 p-6 rounded-2xl border border-slate-800 text-white shadow-sm">
        <div>
          <h2 className="text-xl font-bold tracking-tight">Pharmacy Operations Hub</h2>
          <p className="text-xs text-slate-400 mt-1">Live tracking of batches, dispense workflows, and compliance alerts.</p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/sales"
            className="flex items-center gap-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-md shadow-brand-600/20 transition active:scale-95"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>New Sale (POS)</span>
          </Link>
          <Link
            href="/purchases"
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold px-4 py-2.5 rounded-xl transition active:scale-95"
          >
            <Boxes className="w-4 h-4" />
            <span>Receive Goods</span>
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Valuation */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Inventory Valuation</span>
            <div className="w-8 h-8 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl font-bold text-slate-900">
              ${stats.totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <span className="text-[11px] text-emerald-600 font-medium">Calculated from batch cost prices</span>
          </div>
        </div>

        {/* Medicines Catalog */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Active Medicines</span>
            <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Pill className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl font-bold text-slate-900">{stats.totalItems}</div>
            <span className="text-[11px] text-slate-500">Tracked in database</span>
          </div>
        </div>

        {/* Low Stock Alerts */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Low Stock Warnings</span>
            <div className="w-8 h-8 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl font-bold text-slate-900">{stats.lowStockCount}</div>
            <span className="text-[11px] text-amber-600 font-medium">Below reorder threshold</span>
          </div>
        </div>

        {/* Expiring Batches */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Batches Expiring Soon</span>
            <div className="w-8 h-8 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl font-bold text-slate-900">{stats.expiringCount}</div>
            <span className="text-[11px] text-rose-600 font-medium">Within 30/60 day threshold</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Inventory Table & Critical Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Inventory Summary Table */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="font-bold text-slate-800">Current Stock Levels</h3>
              <p className="text-xs text-slate-500">Grouped by medicine with batch quantities</p>
            </div>
            <Link
              href="/inventory"
              className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
            >
              <span>View All</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider">
                  <th className="pb-3">Medicine</th>
                  <th className="pb-3 text-center">Active Batches</th>
                  <th className="pb-3 text-right">Available Qty</th>
                  <th className="pb-3 text-right">Valuation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {inventory.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="py-8 text-center text-slate-400">
                      No stock data recorded yet. Create or receive batches to see live levels.
                    </td>
                  </tr>
                ) : (
                  inventory.map((item) => (
                    <tr key={item.medicine_id} className="hover:bg-slate-50/70 transition">
                      <td className="py-3.5 font-medium text-slate-800">
                        {item.medicine_name}
                      </td>
                      <td className="py-3.5 text-center">
                        <span className="px-2 py-0.5 rounded-full bg-slate-100 font-medium text-slate-600">
                          {item.batch_count}
                        </span>
                      </td>
                      <td className="py-3.5 text-right font-semibold text-slate-800">
                        {item.total_quantity}
                      </td>
                      <td className="py-3.5 text-right font-medium text-slate-600">
                        ${(item.total_value || 0).toFixed(2)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Priority Alerts Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-rose-500" />
                <h3 className="font-bold text-slate-800">Operational Alerts</h3>
              </div>
              <Link href="/alerts" className="text-xs font-semibold text-brand-600 hover:text-brand-700">
                View All
              </Link>
            </div>

            <div className="space-y-3">
              {alerts.length === 0 ? (
                <div className="py-10 text-center text-xs text-slate-400">
                  No active low-stock or expiry alerts at this time. All batches optimal!
                </div>
              ) : (
                alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className="p-3 rounded-xl border border-slate-100 bg-slate-50/50 flex flex-col gap-1 hover:border-slate-200 transition"
                  >
                    <div className="flex items-center justify-between">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                          alert.alert_type === "LOW_STOCK"
                            ? "bg-amber-100 text-amber-800"
                            : "bg-rose-100 text-rose-800"
                        }`}
                      >
                        {alert.alert_type.replace("_", " ")}
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {alert.created_at ? new Date(alert.created_at).toLocaleDateString() : ""}
                      </span>
                    </div>
                    <p className="text-xs font-medium text-slate-700 mt-1">{alert.message}</p>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100">
            <Link
              href="/reports"
              className="w-full block text-center py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition"
            >
              Export Inventory & Ledger Report
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
