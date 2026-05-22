import { FileText, Download, Calendar } from "lucide-react";
import { useSellerData } from "../data/useSellerData";

export function Reports() {
  const { account } = useSellerData();
  const name = account?.name ?? "Seller";
  const cat  = account?.category ?? "Products";
  const region = account?.region?.split("—")[0].trim() ?? "Region";

  const reports = [
    { name: `Monthly Inventory Report — ${cat}`,       type: "Inventory",  date: "2026-05-01", size: "2.4 MB", format: "PDF"   },
    { name: `Sales Performance May 2026 — ${name}`,    type: "Sales",      date: "2026-05-15", size: "1.8 MB", format: "Excel" },
    { name: `Warehouse Utilisation — ${region}`,        type: "Operations", date: "2026-05-10", size: "950 KB", format: "PDF"   },
    { name: "SARIMAX Forecast Accuracy Report",         type: "Analytics",  date: "2026-05-08", size: "1.2 MB", format: "PDF"   },
    { name: `Order Fulfillment Analysis — ${cat}`,     type: "Operations", date: "2026-05-05", size: "3.1 MB", format: "Excel" },
    { name: `ILP Optimisation Comparison`,             type: "Analytics",  date: "2026-04-28", size: "870 KB", format: "PDF"   },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-600 mt-1">
          Generate and download reports for your <span className="font-medium">{cat}</span> business
        </p>
      </div>

      {/* Generate New Report */}
      <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Generate New Report</h2>
        <div className="grid grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Report Type</label>
            <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option>Inventory Summary</option>
              <option>Sales Performance</option>
              <option>Warehouse Utilization</option>
              <option>SARIMAX Forecast Accuracy</option>
              <option>ILP Optimization Comparison</option>
              <option>Order Fulfillment</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Select date range"
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Format</label>
            <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option>PDF</option>
              <option>Excel</option>
              <option>CSV</option>
            </select>
          </div>
        </div>
        <button className="mt-6 px-8 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors">
          Generate Report
        </button>
      </div>

      {/* Recent Reports */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Recent Reports</h2>
        </div>
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Report Name</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Type</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Generated</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Size</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Format</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Actions</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((report, index) => (
              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-4 px-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-50 rounded-lg">
                      <FileText className="w-5 h-5 text-indigo-600" />
                    </div>
                    <span className="font-medium text-gray-900">{report.name}</span>
                  </div>
                </td>
                <td className="py-4 px-6">
                  <span className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">{report.type}</span>
                </td>
                <td className="py-4 px-6 text-gray-600">{report.date}</td>
                <td className="py-4 px-6 text-gray-600">{report.size}</td>
                <td className="py-4 px-6 text-gray-600">{report.format}</td>
                <td className="py-4 px-6">
                  <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors">
                    <Download className="w-4 h-4" />
                    Download
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
