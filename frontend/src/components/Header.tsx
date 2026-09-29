"use client";

import { usePathname } from "next/navigation";
import { Bell } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

const titles: Record<string, { title: string; subtitle: string }> = {
  "/": { title: "Operations Overview", subtitle: "Real-time stock indicators, valuation, and sales" },
  "/medicines": { title: "Medicines Directory", subtitle: "Pharmaceutical catalog, dosages, and reorder levels" },
  "/inventory": { title: "Batch Inventory", subtitle: "Expiry monitoring, quantities, and stock adjustments" },
  "/sales": { title: "Point of Sale & Invoicing", subtitle: "Dispensing, customer billing, and receipt generation" },
  "/purchases": { title: "Purchases & Receiving", subtitle: "Procurement orders and batch receiving workflow" },
  "/suppliers": { title: "Suppliers & Distributors", subtitle: "Vendor contact directory and order partnerships" },
  "/alerts": { title: "Alerts & Notifications", subtitle: "Actionable low-stock thresholds and expiration notices" },
  "/reports": { title: "Audit & Movement Reports", subtitle: "Valuation, transaction logs, and movement ledger" },
};

export function Header() {
  const pathname = usePathname();
  const [alertCount, setAlertCount] = useState(0);

  useEffect(() => {
    async function fetchAlerts() {
      try {
        const res = await apiFetch("/alerts?status=ACTIVE");
        if (res?.data?.items) {
          setAlertCount(res.data.items.length);
        }
      } catch {}
    }
    fetchAlerts();
  }, [pathname]);

  if (pathname === "/login") return null;

  const current = titles[pathname] || { title: "Pharmacy Management", subtitle: "MediStock Central System" };

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-lg font-bold text-slate-800 tracking-tight">{current.title}</h1>
        <p className="text-xs text-slate-500">{current.subtitle}</p>
      </div>

      <div className="flex items-center gap-4">
        {/* System Health Indicator */}
        <div className="flex items-center gap-2 px-3 py-1 bg-emerald-50 border border-emerald-200 rounded-full text-xs font-medium text-emerald-700">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Core API Connected</span>
        </div>

        {/* Notifications Icon with Badge */}
        <Link
          href="/alerts"
          className="relative p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition"
        >
          <Bell className="w-5 h-5" />
          {alertCount > 0 && (
            <span className="absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-rose-500 text-[10px] font-bold text-white flex items-center justify-center animate-bounce">
              {alertCount}
            </span>
          )}
        </Link>
      </div>
    </header>
  );
}
