import { TrendingUp, TrendingDown, Package, Warehouse, FileText, ShoppingCart, Target, DollarSign, AlertCircle } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { useSellerData } from "../data/useSellerData";

const kpiIcons = [DollarSign, Package, Warehouse, FileText, ShoppingCart, Target, TrendingUp, DollarSign];

export function Dashboard() {
  const { mock, account } = useSellerData();
  const firstName = account?.name.split(" ")[0] ?? "there";

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Welcome back, <span className="font-semibold text-gray-800">{firstName}</span>.
          Here's your <span className="text-indigo-600">{account?.category}</span> business overview.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        {mock.kpis.map((kpi, index) => {
          const Icon = kpiIcons[index % kpiIcons.length];
          return (
            <div key={index} className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="p-2 bg-indigo-50 rounded-lg">
                  <Icon className="w-5 h-5 text-indigo-600" />
                </div>
                <span className={`text-sm font-medium flex items-center gap-1 ${
                  kpi.trend === "up" ? "text-emerald-600" : kpi.trend === "down" ? "text-red-600" : "text-gray-500"
                }`}>
                  {kpi.trend === "up"   && <TrendingUp   className="w-4 h-4" />}
                  {kpi.trend === "down" && <TrendingDown  className="w-4 h-4" />}
                  {kpi.change}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-1">{kpi.label}</p>
              <p className="text-2xl font-bold text-gray-900">{kpi.value}</p>
            </div>
          );
        })}
      </div>

      {/* Warehouse Capacity */}
      <div className="grid grid-cols-1 gap-6 mb-8">
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">Warehouse Capacity Usage</h3>
          <p className="text-sm text-gray-500 mb-4">{account?.region} — {mock.warehouseCapacity.length} warehouses</p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={mock.warehouseCapacity}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="warehouse" />
              <YAxis unit="%" />
              <Tooltip formatter={(v) => `${v}%`} />
              <Legend />
              <Bar dataKey="used"      stackId="a" fill="#4F46E5" name="Used %"      radius={[0, 0, 0, 0]} />
              <Bar dataKey="available" stackId="a" fill="#E0E7FF" name="Available %" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alerts */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-indigo-600" />
          Recent Alerts
        </h3>
        <div className="space-y-4">
          {mock.alerts.map((alert, index) => (
            <div key={index} className={`p-4 rounded-lg border-l-4 ${
              alert.type === "warning" ? "bg-orange-50 border-orange-500" :
              alert.type === "info"    ? "bg-blue-50 border-blue-500" :
                                         "bg-emerald-50 border-emerald-500"
            }`}>
              <p className="text-sm text-gray-900 font-medium">{alert.message}</p>
              <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
