import type { LucideIcon } from "lucide-react";
import {
  LayoutDashboard,
  Package,
  ClipboardList,
  FileText,
  ArrowRightLeft,
  BarChart3,
  CreditCard,
  Settings,
} from "lucide-react";

export type Role = "seller";

export interface NavItem {
  name: string;
  href: string;
  icon: LucideIcon;
}

export interface Account {
  id: string;
  name: string;
  email: string;
  password: string;
  role: Role;
  roleLabel: string;
  tagline: string;
  description: string;
  category: string;
  region: string;
  initials: string;
  avatarColor: string;
  avatarBg: string;
  badgeColor: string;
  nav: NavItem[];
}

const sellerNav: NavItem[] = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Products", href: "/products", icon: Package },
  { name: "Inventory", href: "/inventory", icon: ClipboardList },
  { name: "Storage Requests", href: "/storage-requests", icon: FileText },
  { name: "Stock Operations", href: "/stock-operations", icon: ArrowRightLeft },
  { name: "Reports", href: "/reports", icon: BarChart3 },
  { name: "Billing", href: "/billing", icon: CreditCard },
  { name: "Settings", href: "/settings", icon: Settings },
];

export const DEMO_ACCOUNTS: Account[] = [
  {
    id: "yasser",
    name: "Yasser Brahim",
    email: "yasser@wasl.dz",
    password: "yasser123",
    role: "seller",
    roleLabel: "Seller",
    tagline: "Fashion & Clothing",
    category: "Fashion & Clothing",
    region: "North — Algiers",
    description:
      "Fashion seller based in Algiers. Manages seasonal clothing lines with high Ramadan & Eid demand peaks across the North region.",
    initials: "YB",
    avatarColor: "text-indigo-600",
    avatarBg: "bg-indigo-100",
    badgeColor:
      "bg-indigo-100 text-indigo-700 ring-1 ring-inset ring-indigo-200",
    nav: sellerNav,
  },
  {
    id: "karim",
    name: "Karim Boudiaf",
    email: "karim@wasl.dz",
    password: "karim123",
    role: "seller",
    roleLabel: "Seller",
    tagline: "Electronics",
    category: "Electronics",
    region: "East — Constantine",
    description:
      "Electronics seller operating from Constantine. Distributes smartphones and appliances across the East region with tight stock control.",
    initials: "KB",
    avatarColor: "text-emerald-600",
    avatarBg: "bg-emerald-100",
    badgeColor:
      "bg-emerald-100 text-emerald-700 ring-1 ring-inset ring-emerald-200",
    nav: sellerNav,
  },
  {
    id: "fatima",
    name: "Fatima Zerrouki",
    email: "fatima@wasl.dz",
    password: "fatima123",
    role: "seller",
    roleLabel: "Seller",
    tagline: "Home & Furniture",
    category: "Home & Furniture",
    region: "West — Oran",
    description:
      "Home goods seller in Oran. Handles bulky furniture and household items requiring warehouse space optimization in the West region.",
    initials: "FZ",
    avatarColor: "text-rose-600",
    avatarBg: "bg-rose-100",
    badgeColor: "bg-rose-100 text-rose-700 ring-1 ring-inset ring-rose-200",
    nav: sellerNav,
  },
  {
    id: "omar",
    name: "Omar Tebboune",
    email: "omar@wasl.dz",
    password: "omar123",
    role: "seller",
    roleLabel: "Seller",
    tagline: "Sports & Leisure",
    category: "Sports & Leisure",
    region: "South — Ouargla",
    description:
      "Sports equipment seller covering the South region from Ouargla. Manages low-frequency high-volume restocking with AI forecasting.",
    initials: "OT",
    avatarColor: "text-amber-600",
    avatarBg: "bg-amber-100",
    badgeColor: "bg-amber-100 text-amber-700 ring-1 ring-inset ring-amber-200",
    nav: sellerNav,
  },
];
