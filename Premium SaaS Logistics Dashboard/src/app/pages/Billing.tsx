import { CreditCard, Download, CheckCircle } from "lucide-react";

const subscriptions = [
  { warehouse: "W1 - Algiers East", plan: "Premium", space: "720 m³", price: "180,000 DZD/month", nextBilling: "2024-06-01", status: "active" },
  { warehouse: "W2 - Oran North", plan: "Standard", space: "744 m³", price: "158,400 DZD/month", nextBilling: "2024-06-05", status: "active" },
];

const invoices = [
  { id: "INV-2024-05", date: "2024-05-01", description: "Monthly Storage - May 2024", amount: "338,400 DZD", status: "paid" },
  { id: "INV-2024-04", date: "2024-04-01", description: "Monthly Storage - April 2024", amount: "338,400 DZD", status: "paid" },
  { id: "INV-2024-03", date: "2024-03-01", description: "Monthly Storage - March 2024", amount: "280,000 DZD", status: "paid" },
];

const services = [
  "Secure 24/7 warehouse access",
  "Real-time inventory tracking",
  "Climate-controlled storage",
  "Insurance coverage up to 5M DZD",
  "Order fulfillment & shipping",
  "Returns processing",
  "Dedicated account manager",
  "Priority customer support",
];

export function Billing() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Billing</h1>
        <p className="text-gray-600 mt-1">Manage subscriptions, invoices, and payment methods</p>
      </div>

      {/* Active Subscriptions */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Active Subscriptions</h2>
        <div className="grid gap-6">
          {subscriptions.map((sub, index) => (
            <div key={index} className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{sub.warehouse}</h3>
                  <p className="text-sm text-gray-600 mt-1">{sub.plan} Plan</p>
                </div>
                <span className="px-4 py-1.5 bg-emerald-100 text-emerald-700 text-sm font-medium rounded-full">
                  Active
                </span>
              </div>
              <div className="grid grid-cols-3 gap-6 mb-4">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Storage Space</p>
                  <p className="text-lg font-bold text-gray-900">{sub.space}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Monthly Cost</p>
                  <p className="text-lg font-bold text-indigo-600">{sub.price}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Next Billing</p>
                  <p className="text-lg font-bold text-gray-900">{sub.nextBilling}</p>
                </div>
              </div>
              <button className="text-sm text-indigo-600 font-medium hover:text-indigo-700">
                Manage Subscription →
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Services Included */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Included Logistics Services</h2>
        <div className="grid grid-cols-2 gap-4">
          {services.map((service, index) => (
            <div key={index} className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0" />
              <span className="text-sm text-gray-700">{service}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Invoices */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden mb-8">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Invoice History</h2>
        </div>
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Invoice ID</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Date</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Description</th>
              <th className="text-right py-4 px-6 text-sm font-semibold text-gray-900">Amount</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Status</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Actions</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((invoice) => (
              <tr key={invoice.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-4 px-6 font-semibold text-indigo-600">{invoice.id}</td>
                <td className="py-4 px-6 text-gray-600">{invoice.date}</td>
                <td className="py-4 px-6 text-gray-900">{invoice.description}</td>
                <td className="py-4 px-6 text-right font-semibold text-gray-900">{invoice.amount}</td>
                <td className="py-4 px-6">
                  <span className="px-3 py-1 bg-emerald-100 text-emerald-700 text-xs font-medium rounded-full capitalize">
                    {invoice.status}
                  </span>
                </td>
                <td className="py-4 px-6">
                  <button className="flex items-center gap-2 text-sm text-indigo-600 font-medium hover:text-indigo-700">
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Payment Methods */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Payment Methods</h2>
        <div className="flex items-center gap-4 p-4 border border-gray-200 rounded-lg">
          <div className="p-3 bg-indigo-50 rounded-lg">
            <CreditCard className="w-6 h-6 text-indigo-600" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-gray-900">Visa ending in 4242</p>
            <p className="text-sm text-gray-600">Expires 12/2027</p>
          </div>
          <button className="text-sm text-indigo-600 font-medium hover:text-indigo-700">
            Edit
          </button>
        </div>
        <button className="mt-4 w-full px-6 py-3 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors">
          Add Payment Method
        </button>
      </div>
    </div>
  );
}
