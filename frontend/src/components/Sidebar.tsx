"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Pill,
  Boxes,
  ShoppingCart,
  Truck,
  Building2,
  Bell,
  BarChart3,
  LogOut,
  ShieldCheck,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/medicines", label: "Medicines", icon: Pill },
  { href: "/inventory", label: "Inventory & Batches", icon: Boxes },
  { href: "/sales", label: "Sales & Billing", icon: ShoppingCart },
  { href: "/purchases", label: "Purchases", icon: Truck },
  { href: "/suppliers", label: "Suppliers", icon: Building2 },
  { href: "/alerts", label: "Alerts Center", icon: Bell },
  { href: "/reports", label: "Reports & Ledger", icon: BarChart3 },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  if (pathname === "/login") return null;

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between h-screen sticky top-0 shrink-0 text-slate-300">
      <div>
        {/* Brand Logo */}
        <div className="h-16 flex items-center px-6 gap-3 border-b border-slate-800">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-teal-400 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg text-white tracking-tight">MediStock</span>
            <span className="block text-[10px] text-teal-400 uppercase tracking-widest font-semibold">Pharmacy OS</span>
          </div>
        </div>

        {/* Navigation items */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-brand-600 text-white shadow-sm shadow-brand-600/30"
                    : "text-slate-400 hover:text-white hover:bg-slate-800/60"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-slate-400"}`} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* User profile & Logout */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40">
        {user ? (
          <div className="flex items-center justify-between">
            <div className="flex flex-col min-w-0 pr-2">
              <span className="text-xs font-semibold text-white truncate">{user.full_name}</span>
              <span className="text-[11px] text-brand-400 truncate">{user.roles?.[0] || "User"}</span>
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <Link
            href="/login"
            className="w-full block text-center py-2 px-3 text-xs font-semibold text-brand-400 bg-slate-800/80 rounded-lg hover:bg-slate-800"
          >
            Sign In
          </Link>
        )}
      </div>
    </aside>
  );
}
