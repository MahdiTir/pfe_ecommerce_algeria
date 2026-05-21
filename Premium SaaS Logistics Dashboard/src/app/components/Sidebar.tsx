import { NavLink } from "react-router";
import {
  LayoutDashboard,
  Store,
  Package,
  ClipboardList,
  FileText,
  ArrowRightLeft,
  BarChart3,
  Users,
  CreditCard,
  Settings,
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Products", href: "/products", icon: Package },
  { name: "Inventory", href: "/inventory", icon: ClipboardList },
  { name: "Storage Requests", href: "/storage-requests", icon: FileText },
  { name: "Stock Operations", href: "/stock-operations", icon: ArrowRightLeft },
  { name: "Reports", href: "/reports", icon: BarChart3 },
  { name: "Team & Roles", href: "/team-roles", icon: Users },
  { name: "Billing", href: "/billing", icon: CreditCard },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-indigo-600">StockFlow</h1>
        <p className="text-sm text-gray-500 mt-1">Seller Dashboard</p>
      </div>
      <nav className="flex-1 overflow-y-auto p-4">
        <ul className="space-y-1">
          {navigation.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.href}
                end={item.href === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-indigo-50 text-indigo-600"
                      : "text-gray-700 hover:bg-gray-50"
                  }`
                }
              >
                <item.icon className="w-5 h-5" />
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
