import { NavLink } from "react-router";
import { useAuth } from "../auth/AuthContext";

export function Sidebar() {
  const { account } = useAuth();

  if (!account) return null;

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow-sm">
            <span className="text-base font-black text-white tracking-tight">W</span>
          </div>
          <div>
            <h1 className="text-xl font-black text-gray-900 tracking-tight">WASL</h1>
            <p className="text-xs text-gray-400 mt-0.5">{account.tagline}</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <ul className="space-y-0.5">
          {account.nav.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.href}
                end={item.href === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-indigo-50 text-indigo-600"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  }`
                }
              >
                <item.icon className="w-4 h-4 flex-shrink-0" />
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Current user footer */}
      <div className="p-4 border-t border-gray-100">
        <div className="flex items-center gap-3">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${account.avatarBg} ${account.avatarColor}`}
          >
            {account.initials}
          </div>
          <div className="min-w-0">
            <p className="text-xs font-semibold text-gray-800 truncate">{account.name}</p>
            <p className="text-xs text-gray-400 truncate">{account.category}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
