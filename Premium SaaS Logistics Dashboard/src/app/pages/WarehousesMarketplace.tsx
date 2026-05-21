import { MapPin, Star, Package, TrendingUp, Filter } from "lucide-react";

const warehouses = [
  {
    id: 1,
    name: "LogiHub Algiers",
    company: "LogiHub SA",
    location: "Algiers, East",
    region: "East",
    image: "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400&h=250&fit=crop",
    categories: ["Electronics", "Fashion", "Home & Garden"],
    services: ["Climate Control", "Security 24/7", "Fast Shipping"],
    pricing: "2,500 DZD/month per m³",
    capacity: "850 m³",
    available: "230 m³",
    rating: 4.8,
    reviews: 124,
  },
  {
    id: 2,
    name: "Oran Storage Pro",
    company: "Storage Solutions",
    location: "Oran, North",
    region: "North",
    image: "https://images.unsplash.com/photo-1553413077-190dd305871c?w=400&h=250&fit=crop",
    categories: ["Food & Beverages", "Electronics", "Sports"],
    services: ["Refrigeration", "Loading Dock", "Insurance"],
    pricing: "2,200 DZD/month per m³",
    capacity: "1200 m³",
    available: "450 m³",
    rating: 4.6,
    reviews: 98,
  },
  {
    id: 3,
    name: "Desert Logistics Hub",
    company: "Sahara Freight",
    location: "Tamanrasset, South",
    region: "South",
    image: "https://images.unsplash.com/photo-1565514391032-1ad92e6ea7f5?w=400&h=250&fit=crop",
    categories: ["Construction", "Mining Equipment", "General"],
    services: ["Heavy Equipment", "Outdoor Storage", "Security"],
    pricing: "1,800 DZD/month per m³",
    capacity: "2000 m³",
    available: "1100 m³",
    rating: 4.5,
    reviews: 67,
  },
  {
    id: 4,
    name: "West Coast Warehouse",
    company: "Atlantic Storage Co",
    location: "Tlemcen, West",
    region: "West",
    image: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=250&fit=crop",
    categories: ["Fashion", "Arts & Entertainment", "Home Goods"],
    services: ["Climate Control", "Fulfillment", "Returns Processing"],
    pricing: "2,400 DZD/month per m³",
    capacity: "950 m³",
    available: "320 m³",
    rating: 4.7,
    reviews: 156,
  },
];

export function WarehousesMarketplace() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Warehouses Marketplace</h1>
        <p className="text-gray-600 mt-1">Find and subscribe to storage facilities across Algeria</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6 shadow-sm">
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-600" />
          <select className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option>All Regions</option>
            <option>East</option>
            <option>North</option>
            <option>South</option>
            <option>West</option>
          </select>
          <select className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option>All Categories</option>
            <option>Electronics</option>
            <option>Fashion</option>
            <option>Food & Beverages</option>
          </select>
          <input
            type="text"
            placeholder="Search warehouses..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Map Placeholder */}
      <div className="bg-white rounded-2xl border border-gray-200 p-8 mb-8 shadow-sm">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl h-80 flex items-center justify-center">
          <div className="text-center">
            <MapPin className="w-16 h-16 text-indigo-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-700">Interactive Algeria Map</p>
            <p className="text-sm text-gray-500 mt-1">Warehouse locations across all regions</p>
          </div>
        </div>
      </div>

      {/* Warehouse Cards */}
      <div className="grid grid-cols-2 gap-6">
        {warehouses.map((warehouse) => (
          <div key={warehouse.id} className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-lg transition-shadow">
            <img src={warehouse.image} alt={warehouse.name} className="w-full h-48 object-cover" />
            <div className="p-6">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{warehouse.name}</h3>
                  <p className="text-sm text-gray-600">{warehouse.company}</p>
                </div>
                <div className="flex items-center gap-1 bg-yellow-50 px-2 py-1 rounded-lg">
                  <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                  <span className="text-sm font-semibold text-gray-900">{warehouse.rating}</span>
                  <span className="text-xs text-gray-500">({warehouse.reviews})</span>
                </div>
              </div>

              <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                <MapPin className="w-4 h-4" />
                <span>{warehouse.location}</span>
              </div>

              <div className="mb-4">
                <p className="text-xs font-semibold text-gray-700 mb-2">Accepted Categories:</p>
                <div className="flex flex-wrap gap-2">
                  {warehouse.categories.map((cat, index) => (
                    <span key={index} className="px-2 py-1 bg-indigo-50 text-indigo-700 text-xs rounded-md">
                      {cat}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mb-4">
                <p className="text-xs font-semibold text-gray-700 mb-2">Services:</p>
                <div className="flex flex-wrap gap-2">
                  {warehouse.services.map((service, index) => (
                    <span key={index} className="px-2 py-1 bg-emerald-50 text-emerald-700 text-xs rounded-md">
                      {service}
                    </span>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4 py-4 border-y border-gray-200">
                <div>
                  <p className="text-xs text-gray-600">Pricing</p>
                  <p className="text-sm font-bold text-gray-900">{warehouse.pricing}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Available</p>
                  <p className="text-sm font-bold text-emerald-600">{warehouse.available}</p>
                </div>
              </div>

              <button className="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition-colors">
                Subscribe
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
