import { Package, Clock, Truck, CheckCircle } from "lucide-react";

const orders = [
  { id: "ORD-5421", date: "2024-05-18", customer: "Mohamed Cherif", product: "Wireless Headphones", quantity: 2, total: "17,000 DZD", status: "delivered", warehouse: "W1 - East", tracking: "TRK-98765" },
  { id: "ORD-5420", date: "2024-05-17", customer: "Fatima Zohra", product: "Cotton T-Shirt", quantity: 5, total: "6,000 DZD", status: "in_transit", warehouse: "W2 - North", tracking: "TRK-98764" },
  { id: "ORD-5419", date: "2024-05-17", customer: "Karim Benali", product: "Coffee Beans 1kg", quantity: 3, total: "8,400 DZD", status: "processing", warehouse: "W2 - North", tracking: "TRK-98763" },
  { id: "ORD-5418", date: "2024-05-16", customer: "Amina Lounis", product: "Yoga Mat", quantity: 1, total: "3,500 DZD", status: "pending", warehouse: "W1 - East", tracking: "TRK-98762" },
  { id: "ORD-5417", date: "2024-05-15", customer: "Yacine Mansour", product: "Art Supplies Set", quantity: 2, total: "8,400 DZD", status: "delivered", warehouse: "W1 - East", tracking: "TRK-98761" },
];

export function Orders() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Orders</h1>
        <p className="text-gray-600 mt-1">Track and manage customer orders</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-orange-50 rounded-lg">
              <Clock className="w-5 h-5 text-orange-600" />
            </div>
            <p className="text-sm text-gray-600">Pending</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">12</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-indigo-50 rounded-lg">
              <Package className="w-5 h-5 text-indigo-600" />
            </div>
            <p className="text-sm text-gray-600">Processing</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">24</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <Truck className="w-5 h-5 text-blue-600" />
            </div>
            <p className="text-sm text-gray-600">In Transit</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">18</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-emerald-50 rounded-lg">
              <CheckCircle className="w-5 h-5 text-emerald-600" />
            </div>
            <p className="text-sm text-gray-600">Delivered</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">1,193</p>
        </div>
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Order ID</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Date</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Customer</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Product</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Qty</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Total</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Warehouse</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Status</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Tracking</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-4 px-6 font-semibold text-indigo-600">{order.id}</td>
                <td className="py-4 px-6 text-gray-600">{order.date}</td>
                <td className="py-4 px-6 text-gray-900">{order.customer}</td>
                <td className="py-4 px-6 font-medium text-gray-900">{order.product}</td>
                <td className="py-4 px-6 text-right text-gray-900">{order.quantity}</td>
                <td className="py-4 px-6 text-right font-semibold text-gray-900">{order.total}</td>
                <td className="py-4 px-6 text-gray-600">{order.warehouse}</td>
                <td className="py-4 px-6">
                  <span className={`px-3 py-1 text-xs font-medium rounded-full capitalize ${
                    order.status === "delivered" ? "bg-emerald-100 text-emerald-700" :
                    order.status === "in_transit" ? "bg-blue-100 text-blue-700" :
                    order.status === "processing" ? "bg-indigo-100 text-indigo-700" :
                    "bg-orange-100 text-orange-700"
                  }`}>
                    {order.status.replace("_", " ")}
                  </span>
                </td>
                <td className="py-4 px-6 text-gray-600 font-mono text-sm">{order.tracking}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
