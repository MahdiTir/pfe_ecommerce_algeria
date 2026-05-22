import { TrendingUp, Sparkles, Target, BarChart3 } from "lucide-react";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const forecastData = [
  { week: "Week 1", actual: 245, forecast: 240 },
  { week: "Week 2", actual: 289, forecast: 280 },
  { week: "Week 3", actual: 312, forecast: 305 },
  { week: "Week 4", actual: 401, forecast: 390 },
  { week: "Week 5", forecast: 385 },
  { week: "Week 6", forecast: 395 },
];

const regionalDistribution = [
  { name: "East", value: 29.4, units: 113, color: "#4F46E5" },
  { name: "North", value: 26.9, units: 103, color: "#10B981" },
  { name: "South", value: 20.8, units: 80, color: "#F59E0B" },
  { name: "West", value: 23.0, units: 88, color: "#EF4444" },
];

const warehouseAllocation = [
  { warehouse: "W1 - Algiers East", current: 145, recommended: 180, difference: 35, efficiency: 92 },
  { warehouse: "W2 - Oran North", current: 85, recommended: 120, difference: 35, efficiency: 88 },
  { warehouse: "W3 - Tamanrasset South", current: 42, recommended: 80, difference: 38, efficiency: 75 },
  { warehouse: "W4 - Tlemcen West", current: 68, recommended: 95, difference: 27, efficiency: 85 },
];

export function ForecastOptimization() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Forecast & Optimization</h1>
        <p className="text-gray-600 mt-1">AI-powered demand forecasting and ILP optimization</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-indigo-50 rounded-lg">
              <TrendingUp className="w-5 h-5 text-indigo-600" />
            </div>
            <p className="text-sm text-gray-600">Forecast Accuracy</p>
          </div>
          <p className="text-3xl font-bold text-indigo-600">94.2%</p>
          <p className="text-xs text-emerald-600 mt-1">R² Score</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-emerald-50 rounded-lg">
              <Target className="w-5 h-5 text-emerald-600" />
            </div>
            <p className="text-sm text-gray-600">Optimization Score</p>
          </div>
          <p className="text-3xl font-bold text-emerald-600">98.5%</p>
          <p className="text-xs text-gray-500 mt-1">Cost efficiency</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-orange-50 rounded-lg">
              <BarChart3 className="w-5 h-5 text-orange-600" />
            </div>
            <p className="text-sm text-gray-600">Next 4 Weeks Demand</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">1,565</p>
          <p className="text-xs text-gray-500 mt-1">units forecast</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-purple-50 rounded-lg">
              <Sparkles className="w-5 h-5 text-purple-600" />
            </div>
            <p className="text-sm text-gray-600">Active Models</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">6</p>
          <p className="text-xs text-gray-500 mt-1">categories tracked</p>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Forecast vs Actual Demand</h3>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={forecastData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="actual" stroke="#10B981" strokeWidth={3} name="Actual Sales" dot={{ fill: "#10B981", r: 6 }} />
              <Line type="monotone" dataKey="forecast" stroke="#4F46E5" strokeWidth={2} strokeDasharray="5 5" name="AI Forecast" />
            </LineChart>
          </ResponsiveContainer>
          <div className="mt-4 p-4 bg-emerald-50 rounded-lg">
            <p className="text-sm text-emerald-800">
              <strong>Insight:</strong> Forecast accuracy is 94.2% over the past 4 weeks. Model suggests preparing for 385-395 units in the coming period.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Regional Demand Distribution</h3>
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie
                data={regionalDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name} ${value.toFixed(1)}%`}
                outerRadius={110}
                fill="#8884d8"
                dataKey="value"
              >
                {regionalDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-3 mt-4">
            {regionalDistribution.map((region, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: region.color }}></div>
                  <span className="text-sm font-medium text-gray-900">{region.name}</span>
                </div>
                <span className="text-sm font-bold text-gray-900">{region.units}u</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Warehouse Allocation Table */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden mb-8">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">AI-Optimized Warehouse Allocation</h3>
          <p className="text-sm text-gray-600 mt-1">Recommendations based on ILP optimization</p>
        </div>
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Warehouse</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Current Stock</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Recommended</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Difference</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Efficiency</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Action</th>
            </tr>
          </thead>
          <tbody>
            {warehouseAllocation.map((warehouse, index) => (
              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-4 px-6 font-medium text-gray-900">{warehouse.warehouse}</td>
                <td className="py-4 px-6 text-right text-gray-900">{warehouse.current}</td>
                <td className="py-4 px-6 text-right font-semibold text-indigo-600">{warehouse.recommended}</td>
                <td className="py-4 px-6 text-right">
                  <span className="font-bold text-emerald-600">+{warehouse.difference}</span>
                </td>
                <td className="py-4 px-6 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full"
                        style={{ width: `${warehouse.efficiency}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold text-gray-900">{warehouse.efficiency}%</span>
                  </div>
                </td>
                <td className="py-4 px-6">
                  <button className="px-4 py-1.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors">
                    Create Request
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* AI Insights Card */}
      <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-8 shadow-lg text-white">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-white/20 rounded-lg backdrop-blur-sm">
            <Sparkles className="w-8 h-8" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold mb-3">AI-Powered Recommendations</h3>
            <div className="space-y-3">
              <p className="text-sm opacity-95">
                ✓ <strong>High Priority:</strong> Increase stock in W3 (Tamanrasset South) by 38 units to meet projected demand spike in South region.
              </p>
              <p className="text-sm opacity-95">
                ✓ <strong>Medium Priority:</strong> Rebalance 35 units between W1 and W2 to optimize distribution costs by 12%.
              </p>
              <p className="text-sm opacity-95">
                ✓ <strong>Long-term:</strong> Consider expanding W2 capacity to accommodate 28% forecasted growth in North region over next quarter.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
