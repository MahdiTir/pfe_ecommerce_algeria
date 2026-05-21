import { AlertCircle, Package, TrendingUp } from "lucide-react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

const inventory = [
  { warehouse: "W1 - Algiers East", product: "Wireless Headphones", sku: "SKU-12345", quantity: 145, reserved: 20, threshold: 50, status: "healthy" },
  { warehouse: "W1 - Algiers East", product: "Cotton T-Shirt", sku: "SKU-23456", quantity: 320, reserved: 45, threshold: 100, status: "healthy" },
  { warehouse: "W2 - Oran North", product: "Coffee Beans 1kg", sku: "SKU-34567", quantity: 42, reserved: 8, threshold: 50, status: "low" },
  { warehouse: "W2 - Oran North", product: "Yoga Mat", sku: "SKU-45678", quantity: 85, reserved: 12, threshold: 30, status: "healthy" },
  { warehouse: "W1 - Algiers East", product: "Art Supplies Set", sku: "SKU-56789", quantity: 18, reserved: 5, threshold: 25, status: "critical" },
];

const stockDistribution = [
  { name: "W1 - East", value: 483, color: "#4F46E5" },
  { name: "W2 - North", value: 127, color: "#10B981" },
];

const turnoverData = [
  { product: "Headphones", turnover: 85 },
  { product: "T-Shirts", turnover: 72 },
  { product: "Coffee", turnover: 95 },
  { product: "Yoga Mat", turnover: 65 },
  { product: "Art Supplies", turnover: 58 },
];

export function Inventory() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Inventory</h1>
        <p className="text-gray-600 mt-1">Real-time stock levels across all warehouses</p>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Stock Distribution by Warehouse</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={stockDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {stockDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Stock Turnover Rate</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={turnoverData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="product" />
              <YAxis />
              <Tooltip />
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
            {inventory.map((item, index) => (
              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-4 px-6 text-gray-900">{item.warehouse}</td>
                <td className="py-4 px-6 font-medium text-gray-900">{item.product}</td>
                <td className="py-4 px-6 text-gray-600">{item.sku}</td>
                <td className="py-4 px-6 text-right font-semibold text-gray-900">{item.quantity}</td>
                <td className="py-4 px-6 text-right text-gray-600">{item.reserved}</td>
                <td className="py-4 px-6 text-right font-semibold text-indigo-600">{item.quantity - item.reserved}</td>
                <td className="py-4 px-6 text-right text-gray-600">{item.threshold}</td>
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
