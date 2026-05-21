import { Plus, Clock, CheckCircle, XCircle, Eye } from "lucide-react";
import { useNavigate } from "react-router";

const requests = [
  { id: "SR-2024-158", date: "2024-05-15", product: "Wireless Headphones", sku: "SKU-12345", quantity: 150, warehouse: "W2 - Oran North", status: "approved", category: "Arts & Entertainment" },
  { id: "SR-2024-157", date: "2024-05-14", product: "Cotton T-Shirt", sku: "SKU-23456", quantity: 200, warehouse: "W1 - Algiers East", status: "pending", category: "Fashion" },
  { id: "SR-2024-156", date: "2024-05-13", product: "Coffee Beans 1kg", sku: "SKU-34567", quantity: 100, warehouse: "W2 - Oran North", status: "pending", category: "Food & Beverages" },
  { id: "SR-2024-155", date: "2024-05-12", product: "Yoga Mat", sku: "SKU-45678", quantity: 85, warehouse: "W3 - Tamanrasset South", status: "processing", category: "Sports" },
  { id: "SR-2024-154", date: "2024-05-10", product: "Art Supplies Set", sku: "SKU-56789", quantity: 50, warehouse: "W1 - Algiers East", status: "rejected", category: "Arts & Entertainment" },
];

export function StorageRequests() {
  const navigate = useNavigate();

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Storage Requests</h1>
          <p className="text-gray-600 mt-1">Create and track storage allocation requests</p>
        </div>
        <button
          onClick={() => navigate("/storage-requests/new")}
          className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          New Request
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <p className="text-sm text-gray-600 mb-1">Total Requests</p>
          <p className="text-3xl font-bold text-gray-900">24</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <p className="text-sm text-gray-600 mb-1">Pending</p>
          <p className="text-3xl font-bold text-orange-600">12</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <p className="text-sm text-gray-600 mb-1">Approved</p>
          <p className="text-3xl font-bold text-emerald-600">9</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <p className="text-sm text-gray-600 mb-1">Processing</p>
          <p className="text-3xl font-bold text-indigo-600">3</p>
        </div>
      </div>

      {/* Requests Table */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Request ID</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Date</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Product</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Category</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Quantity</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Warehouse</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Status</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Actions</th>
            </tr>
          </thead>
          <tbody>
            {requests.map((request) => (
              <tr key={request.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-4 px-6 font-semibold text-indigo-600">{request.id}</td>
                <td className="py-4 px-6 text-gray-600">{request.date}</td>
                <td className="py-4 px-6">
                  <div>
                    <p className="font-medium text-gray-900">{request.product}</p>
                    <p className="text-xs text-gray-500">{request.sku}</p>
                  </div>
                </td>
                <td className="py-4 px-6 text-gray-600">{request.category}</td>
                <td className="py-4 px-6 text-right font-semibold text-gray-900">{request.quantity}</td>
                <td className="py-4 px-6 text-gray-900">{request.warehouse}</td>
                <td className="py-4 px-6">
                  <div className="flex items-center gap-2">
                    {request.status === "approved" && <CheckCircle className="w-4 h-4 text-emerald-500" />}
                    {request.status === "pending" && <Clock className="w-4 h-4 text-orange-500" />}
                    {request.status === "processing" && <Clock className="w-4 h-4 text-indigo-500" />}
                    {request.status === "rejected" && <XCircle className="w-4 h-4 text-red-500" />}
                    <span className={`px-3 py-1 text-xs font-medium rounded-full capitalize ${
                      request.status === "approved" ? "bg-emerald-100 text-emerald-700" :
                      request.status === "pending" ? "bg-orange-100 text-orange-700" :
                      request.status === "processing" ? "bg-indigo-100 text-indigo-700" :
                      "bg-red-100 text-red-700"
                    }`}>
                      {request.status}
                    </span>
                  </div>
                </td>
                <td className="py-4 px-6">
                  <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                    <Eye className="w-4 h-4 text-gray-600" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
