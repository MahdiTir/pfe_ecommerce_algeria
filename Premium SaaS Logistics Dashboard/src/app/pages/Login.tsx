import { useState } from "react";
import { useNavigate } from "react-router";
import { DEMO_ACCOUNTS, type Account } from "../auth/accounts";
import { useAuth } from "../auth/AuthContext";
import { ChevronRight, MapPin, Tag, Zap } from "lucide-react";

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [selected, setSelected] = useState<string | null>(null);

  const handleSelect = (account: Account) => {
    setSelected(account.id);
    setTimeout(() => {
      login(account);
      navigate("/");
    }, 300);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 flex flex-col items-center justify-center p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-indigo-800/10 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-4xl">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-600 shadow-lg shadow-indigo-900/50 mb-5">
            <span className="text-2xl font-black text-white tracking-tight">W</span>
          </div>
          <h1 className="text-5xl font-black text-white tracking-tight mb-1">
            WASL
          </h1>
          <p className="text-indigo-300 text-lg font-medium tracking-widest mb-3">
            وصل
          </p>
          <p className="text-slate-400 text-base">
            Algeria's Smart Logistics &amp; Warehouse Optimization Platform
          </p>
        </div>

        {/* Account cards */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-4 h-4 text-indigo-400" />
            <p className="text-slate-300 text-sm font-medium">
              Select a seller account to continue
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {DEMO_ACCOUNTS.map((account) => (
              <button
                key={account.id}
                onClick={() => handleSelect(account)}
                disabled={selected !== null}
                className={`group relative text-left rounded-2xl border p-5 transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500
                  ${
                    selected === account.id
                      ? "bg-white/10 border-white/30 scale-[0.98]"
                      : "bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20 hover:scale-[1.01]"
                  }
                  ${selected !== null && selected !== account.id ? "opacity-40" : ""}
                `}
              >
                <div className="flex items-start gap-4">
                  {/* Avatar */}
                  <div
                    className={`flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center text-sm font-bold shadow-sm ${account.avatarBg} ${account.avatarColor}`}
                  >
                    {account.initials}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="font-semibold text-white text-sm">
                        {account.name}
                      </span>
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${account.badgeColor}`}
                      >
                        {account.roleLabel}
                      </span>
                    </div>

                    {/* Category & Region */}
                    <div className="flex flex-wrap gap-x-3 gap-y-1 mb-2">
                      <span className="flex items-center gap-1 text-xs text-slate-400">
                        <Tag className="w-3 h-3" />
                        {account.category}
                      </span>
                      <span className="flex items-center gap-1 text-xs text-slate-400">
                        <MapPin className="w-3 h-3" />
                        {account.region}
                      </span>
                    </div>

                    <p className="text-slate-400 text-xs leading-relaxed">
                      {account.description}
                    </p>
                  </div>

                  <ChevronRight
                    className={`flex-shrink-0 w-4 h-4 mt-1 transition-transform text-slate-500 group-hover:text-slate-300 group-hover:translate-x-0.5 ${
                      selected === account.id ? "text-white translate-x-1" : ""
                    }`}
                  />
                </div>

                {/* Credentials */}
                <div className="mt-3 pt-3 border-t border-white/5 flex items-center gap-4">
                  <span className="text-xs text-slate-500 font-mono">
                    {account.email}
                  </span>
                  <span className="text-xs text-slate-600">·</span>
                  <span className="text-xs text-slate-500 font-mono">
                    {account.password}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-slate-600 text-xs">
          Demo environment · 4 seller profiles across Algeria's regions ·{" "}
          <span className="text-slate-500">PFE 2026</span>
        </p>
      </div>
    </div>
  );
}
