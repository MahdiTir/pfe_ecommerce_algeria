import { ArrowUpRight, ArrowDownLeft, ArrowRightLeft, Package } from "lucide-react";
import { useSellerData } from "../data/useSellerData";

const getOperationIcon = (type: string) => {
  if (type === "inbound")  return <ArrowDownLeft  className="w-4 h-4" />;
  if (type === "outbound") return <ArrowUpRight    className="w-4 h-4" />;
  if (type === "transfer") return <ArrowRightLeft  className="w-4 h-4" />;
  return <Package className="w-4 h-4" />;
};

const getOperationColor = (type: string) => {
  if (type === "inbound")  return "bg-emerald-100 text-emerald-700";
  if (type === "outbound") return "bg-blue-100 text-blue-700";
  if (type === "transfer") return "bg-purple-100 text-purple-700";
  return "bg-gray-100 text-gray-700";
};

export function StockOperations() {
  const { mock } = useSellerData();
  const ops = mock.stockOperations;

  const inboundCount  = ops.filter((o) => o.type === "inbound").length;
  const outboundCount = ops.filter((o) => o.type === "outbound").length;
  const transferCount = ops.filter((o) => o.type === "transfer").length;
  const totalMoved    = ops.reduce((s, o) => s + o.quantity, 0);

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
            <div className="p-2 bg-emerald-50 rounded-lg"><ArrowDownLeft className="w-5 h-5 text-emerald-600" /></div>
            <p className="text-sm text-gray-600">Inbound</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{inboundCount}</p>
          <p className="text-xs text-gray-500 mt-1">Recent operations</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-blue-50 rounded-lg"><ArrowUpRight className="w-5 h-5 text-blue-600" /></div>
            <p className="text-sm text-gray-600">Outbound</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{outboundCount}</p>
          <p className="text-xs text-gray-500 mt-1">Recent operations</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-purple-50 rounded-lg"><ArrowRightLeft className="w-5 h-5 text-purple-600" /></div>
            <p className="text-sm text-gray-600">Transfers</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{transferCount}</p>
          <p className="text-xs text-gray-500 mt-1">Between warehouses</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-gray-50 rounded-lg"><Package className="w-5 h-5 text-gray-600" /></div>
            <p className="text-sm text-gray-600">Total Items Moved</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{totalMoved.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-1">All operations</p>
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
            {ops.map((op) => (
              <tr key={op.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-4 px-6 font-semibold text-indigo-600">{op.id}</td>
                <td className="py-4 px-6 text-gray-600">{op.date}</td>
                <td className="py-4 px-6">
                  <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium capitalize ${getOperationColor(op.type)}`}>
                    {getOperationIcon(op.type)}
                    {op.type}
                  </span>
                </td>
                <td className="py-4 px-6">
                  <div>
                    <p className="font-medium text-gray-900">{op.product}</p>
                    <p className="text-xs text-gray-500 font-mono">{op.sku}</p>
                  </div>
                </td>
                <td className="py-4 px-6 text-right font-semibold text-gray-900">{op.quantity}</td>
                <td className="py-4 px-6 text-gray-900 text-sm">{op.warehouse}</td>
                <td className="py-4 px-6">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    op.status === "completed"   ? "bg-emerald-100 text-emerald-700" :
                    op.status === "in_progress" ? "bg-indigo-100 text-indigo-700"   :
                                                  "bg-orange-100 text-orange-700"
                  }`}>
                    {op.status.replace("_", " ")}
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
