import { TrendingUp, TrendingDown, Package, Warehouse, FileText, ShoppingCart, Target, DollarSign, AlertCircle } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const kpiData = [
  { label: "Total Inventory Value", value: "2,450,000 DZD", change: "+12.5%", trend: "up", icon: DollarSign },
  { label: "Units in Stock", value: "15,842", change: "+8.3%", trend: "up", icon: Package },
  { label: "Active Warehouses", value: "8", change: "0%", trend: "neutral", icon: Warehouse },
  { label: "Pending Requests", value: "12", change: "-4", trend: "down", icon: FileText },
  { label: "Orders This Month", value: "1,247", change: "+18.2%", trend: "up", icon: ShoppingCart },
  { label: "Forecast Accuracy (R²)", value: "94.2%", change: "+2.1%", trend: "up", icon: Target },
  { label: "Stock Health Score", value: "87/100", change: "+5", trend: "up", icon: TrendingUp },
  { label: "Monthly Logistics Cost", value: "185,000 DZD", change: "-3.2%", trend: "down", icon: DollarSign },
];

const warehouseCapacity = [
  { warehouse: "W1-East", used: 85, available: 15 },
  { warehouse: "W2-North", used: 62, available: 38 },
  { warehouse: "W3-South", used: 45, available: 55 },
  { warehouse: "W4-West", used: 73, available: 27 },
];

const alerts = [
  { type: "warning", message: "Low stock alert: Product SKU-12345 in W2-North (8 units remaining)", time: "2 hours ago" },
  { type: "info", message: "Pending approval: Storage request #SR-2024-156 awaiting confirmation", time: "5 hours ago" },
  { type: "success", message: "AI recommends restocking 150 units of SKU-67890 to W1-East", time: "1 day ago" },
];

export function Dashboard() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome back, Ahmed. Here's your business overview.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        {kpiData.map((kpi, index) => (
          <div key={index} className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="p-2 bg-indigo-50 rounded-lg">
                <kpi.icon className="w-5 h-5 text-indigo-600" />
              </div>
              <span className={`text-sm font-medium flex items-center gap-1 ${
                kpi.trend === "up" ? "text-emerald-600" : kpi.trend === "down" ? "text-red-600" : "text-gray-600"
              }`}>
                {kpi.trend === "up" && <TrendingUp className="w-4 h-4" />}
                {kpi.trend === "down" && <TrendingDown className="w-4 h-4" />}
                {kpi.change}
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-1">{kpi.label}</p>
            <p className="text-2xl font-bold text-gray-900">{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Warehouse Capacity Usage */}
      <div className="grid grid-cols-1 gap-6 mb-8">
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Warehouse Capacity Usage</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={warehouseCapacity}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="warehouse" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="used" stackId="a" fill="#4F46E5" name="Used %" radius={[0, 0, 0, 0]} />
              <Bar dataKey="available" stackId="a" fill="#E0E7FF" name="Available %" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alerts */}
      <div className="grid grid-cols-1 gap-6">
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-indigo-600" />
            Recent Alerts
          </h3>
          <div className="space-y-4">
            {alerts.map((alert, index) => (
              <div key={index} className={`p-4 rounded-lg border-l-4 ${
                alert.type === "warning" ? "bg-orange-50 border-orange-500" :
                alert.type === "info" ? "bg-blue-50 border-blue-500" :
                "bg-emerald-50 border-emerald-500"
              }`}>
                <p className="text-sm text-gray-900 font-medium">{alert.message}</p>
                <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
