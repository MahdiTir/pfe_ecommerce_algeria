import { AlertCircle } from "lucide-react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useSellerData } from "../data/useSellerData";

const PIE_COLORS = ["#4F46E5", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"];

export function Inventory() {
  const { mock, account } = useSellerData();

  // Derive per-warehouse from inventory data
  const warehouseNames = [...new Set(mock.inventory.map((i) => i.warehouseId))];
  const stockDistributionFromInventory = warehouseNames.map((wid, i) => ({
    name: wid,
    value: mock.inventory
      .filter((item) => item.warehouseId === wid)
      .reduce((sum, item) => sum + item.quantity, 0),
    color: PIE_COLORS[i % PIE_COLORS.length],
  }));

  const turnoverData = mock.products.map((p) => ({
    product: p.name.split(" ").slice(0, 2).join(" "),
    turnover: Math.floor(40 + Math.random() * 55),
  }));

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Inventory</h1>
        <p className="text-gray-600 mt-1">
          Real-time stock levels across {account?.region} warehouses
        </p>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Stock Distribution by Warehouse</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={stockDistributionFromInventory}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                dataKey="value"
              >
                {stockDistributionFromInventory.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Stock Turnover Rate (%)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={turnoverData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="product" tick={{ fontSize: 11 }} />
              <YAxis unit="%" />
              <Tooltip formatter={(v) => `${v}%`} />
              <Bar dataKey="turnover" fill="#4F46E5" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Current Stock Levels</h3>
        </div>
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Warehouse</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Product</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">SKU</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Quantity</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Reserved</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Available</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Threshold</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Status</th>
            </tr>
          </thead>
          <tbody>
            {mock.inventory.map((item, index) => (
              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-4 px-6 text-gray-900 text-sm">{item.warehouse}</td>
                <td className="py-4 px-6 font-medium text-gray-900">{item.product}</td>
                <td className="py-4 px-6 text-gray-500 font-mono text-sm">{item.sku}</td>
                <td className="py-4 px-6 text-right font-semibold text-gray-900">{item.quantity}</td>
                <td className="py-4 px-6 text-right text-gray-500">{item.reserved}</td>
                <td className="py-4 px-6 text-right font-semibold text-indigo-600">{item.quantity - item.reserved}</td>
                <td className="py-4 px-6 text-right text-gray-500">{item.threshold}</td>
                <td className="py-4 px-6">
                  <div className="flex items-center gap-2">
                    {item.status === "critical" && (
                      <>
                        <AlertCircle className="w-4 h-4 text-red-500" />
                        <span className="px-3 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full">Critical</span>
                      </>
                    )}
                    {item.status === "low" && (
                      <>
                        <AlertCircle className="w-4 h-4 text-orange-500" />
                        <span className="px-3 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">Low Stock</span>
                      </>
                    )}
                    {item.status === "healthy" && (
                      <span className="px-3 py-1 bg-emerald-100 text-emerald-700 text-xs font-medium rounded-full">Healthy</span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
