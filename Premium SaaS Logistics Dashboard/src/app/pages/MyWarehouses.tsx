import { Package, TrendingUp, AlertCircle } from "lucide-react";

const myWarehouses = [
  {
    id: "W1",
    name: "W1 - Algiers East",
    region: "East",
    capacity: "850 m³",
    used: "720 m³",
    available: "130 m³",
    utilization: 85,
    products: 42,
    monthlyFee: "180,000 DZD",
    status: "active",
  },
  {
    id: "W2",
    name: "W2 - Oran North",
    region: "North",
    capacity: "1200 m³",
    used: "744 m³",
    available: "456 m³",
    utilization: 62,
    products: 28,
    monthlyFee: "158,400 DZD",
    status: "active",
  },
];

export function MyWarehouses() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Warehouses</h1>
        <p className="text-gray-600 mt-1">Manage your subscribed storage facilities</p>
      </div>

      <div className="grid gap-6">
        {myWarehouses.map((warehouse) => (
          <div key={warehouse.id} className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h3 className="text-2xl font-bold text-gray-900">{warehouse.name}</h3>
                <p className="text-gray-600 mt-1">Region: {warehouse.region}</p>
              </div>
              <span className="px-4 py-1.5 bg-emerald-100 text-emerald-700 text-sm font-medium rounded-full capitalize">
                {warehouse.status}
              </span>
            </div>

            <div className="grid grid-cols-5 gap-6 mb-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Total Capacity</p>
                <p className="text-xl font-bold text-gray-900">{warehouse.capacity}</p>
              </div>
              <div className="bg-indigo-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Used Space</p>
                <p className="text-xl font-bold text-indigo-600">{warehouse.used}</p>
              </div>
              <div className="bg-emerald-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Available</p>
                <p className="text-xl font-bold text-emerald-600">{warehouse.available}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Products</p>
                <p className="text-xl font-bold text-gray-900">{warehouse.products}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Monthly Fee</p>
                <p className="text-xl font-bold text-gray-900">{warehouse.monthlyFee}</p>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-gray-700">Space Utilization</p>
                <p className="text-sm font-bold text-gray-900">{warehouse.utilization}%</p>
              </div>
              <div className="bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all ${
                    warehouse.utilization > 80 ? "bg-orange-500" : "bg-indigo-600"
                  }`}
                  style={{ width: `${warehouse.utilization}%` }}
                ></div>
              </div>
              {warehouse.utilization > 80 && (
                <div className="flex items-center gap-2 mt-3 text-orange-600">
                  <AlertCircle className="w-4 h-4" />
                  <p className="text-sm">High utilization - consider expanding storage</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
