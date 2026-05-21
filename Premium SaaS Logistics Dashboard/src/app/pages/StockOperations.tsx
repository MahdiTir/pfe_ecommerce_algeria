import { ArrowUpRight, ArrowDownLeft, ArrowRightLeft, Package } from "lucide-react";

const operations = [
  { id: "OP-1245", date: "2024-05-18", type: "inbound", product: "Wireless Headphones", sku: "SKU-12345", quantity: 100, warehouse: "W1 - Algiers East", status: "completed" },
  { id: "OP-1244", date: "2024-05-17", type: "outbound", product: "Cotton T-Shirt", sku: "SKU-23456", quantity: 50, warehouse: "W2 - Oran North", status: "in_progress" },
  { id: "OP-1243", date: "2024-05-17", type: "transfer", product: "Coffee Beans 1kg", sku: "SKU-34567", quantity: 30, warehouse: "W1 → W2", status: "completed" },
  { id: "OP-1242", date: "2024-05-16", type: "inbound", product: "Yoga Mat", sku: "SKU-45678", quantity: 75, warehouse: "W3 - Tamanrasset South", status: "pending" },
  { id: "OP-1241", date: "2024-05-15", type: "outbound", product: "Art Supplies Set", sku: "SKU-56789", quantity: 25, warehouse: "W1 - Algiers East", status: "completed" },
];

const getOperationIcon = (type: string) => {
  switch (type) {
    case "inbound": return <ArrowDownLeft className="w-4 h-4" />;
    case "outbound": return <ArrowUpRight className="w-4 h-4" />;
    case "transfer": return <ArrowRightLeft className="w-4 h-4" />;
    default: return <Package className="w-4 h-4" />;
  }
};

const getOperationColor = (type: string) => {
  switch (type) {
    case "inbound": return "bg-emerald-100 text-emerald-700";
    case "outbound": return "bg-blue-100 text-blue-700";
    case "transfer": return "bg-purple-100 text-purple-700";
    default: return "bg-gray-100 text-gray-700";
  }
};

export function StockOperations() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Stock Operations</h1>
        <p className="text-gray-600 mt-1">Track inbound, outbound, and transfer operations</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-emerald-50 rounded-lg">
              <ArrowDownLeft className="w-5 h-5 text-emerald-600" />
            </div>
            <p className="text-sm text-gray-600">Inbound</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">24</p>
          <p className="text-xs text-gray-500 mt-1">This month</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <ArrowUpRight className="w-5 h-5 text-blue-600" />
            </div>
            <p className="text-sm text-gray-600">Outbound</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">156</p>
          <p className="text-xs text-gray-500 mt-1">This month</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-purple-50 rounded-lg">
              <ArrowRightLeft className="w-5 h-5 text-purple-600" />
            </div>
            <p className="text-sm text-gray-600">Transfers</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">18</p>
          <p className="text-xs text-gray-500 mt-1">This month</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-gray-50 rounded-lg">
              <Package className="w-5 h-5 text-gray-600" />
            </div>
            <p className="text-sm text-gray-600">Total Items Moved</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">2,847</p>
          <p className="text-xs text-gray-500 mt-1">This month</p>
        </div>
      </div>

      {/* Operations Table */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Operation ID</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Date</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Type</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Product</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Quantity</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Warehouse</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Status</th>
            </tr>
          </thead>
          <tbody>
            {operations.map((operation) => (
              <tr key={operation.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-4 px-6 font-semibold text-indigo-600">{operation.id}</td>
                <td className="py-4 px-6 text-gray-600">{operation.date}</td>
                <td className="py-4 px-6">
                  <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium capitalize ${getOperationColor(operation.type)}`}>
                    {getOperationIcon(operation.type)}
                    {operation.type}
                  </span>
                </td>
                <td className="py-4 px-6">
                  <div>
                    <p className="font-medium text-gray-900">{operation.product}</p>
                    <p className="text-xs text-gray-500">{operation.sku}</p>
                  </div>
                </td>
                <td className="py-4 px-6 text-right font-semibold text-gray-900">{operation.quantity}</td>
                <td className="py-4 px-6 text-gray-900">{operation.warehouse}</td>
                <td className="py-4 px-6">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${
                    operation.status === "completed" ? "bg-emerald-100 text-emerald-700" :
                    operation.status === "in_progress" ? "bg-indigo-100 text-indigo-700" :
                    "bg-orange-100 text-orange-700"
                  }`}>
                    {operation.status.replace("_", " ")}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
