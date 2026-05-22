import { Search, Bell, Globe, LogOut, RefreshCw, Check } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "../auth/AuthContext";
import { DEMO_ACCOUNTS } from "../auth/accounts";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";

export function TopBar() {
  const [language, setLanguage] = useState("EN");
  const { account, logout, switchAccount } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleSwitch = (accountId: string) => {
    if (accountId !== account?.id) {
      switchAccount(accountId);
      navigate("/");
    }
  };

  const others = DEMO_ACCOUNTS.filter((a) => a.id !== account?.id);

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3.5">
      <div className="flex items-center justify-between">
        {/* Search */}
        <div className="flex-1 max-w-2xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search products, orders, warehouses..."
              className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-gray-50"
            />
          </div>
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-2 ml-6">
          {/* Notifications */}
          <button className="relative p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-rose-500 rounded-full" />
          </button>

          {/* Language toggle */}
          <button
            onClick={() =>
              setLanguage(
                language === "EN" ? "FR" : language === "FR" ? "AR" : "EN"
              )
            }
            className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Globe className="w-4 h-4" />
            <span className="font-medium">{language}</span>
          </button>

          <div className="w-px h-6 bg-gray-200 mx-1" />

          {/* Account switcher */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2.5 px-2 py-1.5 rounded-lg hover:bg-gray-100 transition-colors focus:outline-none">
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-semibold text-gray-900 leading-tight">
                    {account?.name}
                  </p>
                  <p className="text-xs text-gray-500 leading-tight">
                    {account?.category}
                  </p>
                </div>
                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${account?.avatarBg} ${account?.avatarColor}`}
                >
                  {account?.initials}
                </div>
              </button>
            </DropdownMenuTrigger>

            <DropdownMenuContent align="end" className="w-64">
              {/* Current account */}
              <DropdownMenuLabel className="font-normal">
                <div className="flex items-center gap-3 py-1">
                  <div
                    className={`w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${account?.avatarBg} ${account?.avatarColor}`}
                  >
                    {account?.initials}
                  </div>
                  <div>
                    <p className="font-semibold text-sm text-gray-900">
                      {account?.name}
                    </p>
                    <p className="text-xs text-gray-500">{account?.email}</p>
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium mt-1 ${account?.badgeColor}`}
                    >
                      {account?.roleLabel}
                    </span>
                  </div>
                </div>
              </DropdownMenuLabel>

              <DropdownMenuSeparator />

              {/* Switch account section */}
              <DropdownMenuLabel className="text-xs text-gray-400 font-medium uppercase tracking-wider flex items-center gap-1.5">
                <RefreshCw className="w-3 h-3" />
                Switch Account
              </DropdownMenuLabel>

              {others.map((acc) => (
                <DropdownMenuItem
                  key={acc.id}
                  onClick={() => handleSwitch(acc.id)}
                  className="flex items-center gap-3 cursor-pointer"
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${acc.avatarBg} ${acc.avatarColor}`}
                  >
                    {acc.initials}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">
                      {acc.name}
                    </p>
                    <p className="text-xs text-gray-500">{acc.category}</p>
                  </div>
                  {acc.id === account?.id && (
                    <Check className="w-3.5 h-3.5 text-indigo-600" />
                  )}
                </DropdownMenuItem>
              ))}

              <DropdownMenuSeparator />

              <DropdownMenuItem
                onClick={handleLogout}
                className="flex items-center gap-2 cursor-pointer text-rose-600 focus:text-rose-600 focus:bg-rose-50"
              >
                <LogOut className="w-4 h-4" />
                <span className="text-sm font-medium">Sign out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
