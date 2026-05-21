import { useState, useEffect, useMemo } from "react";
import { ChevronRight, ChevronLeft, Check, MapPin, TrendingUp, FileCheck, Sparkles } from "lucide-react";
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { useNavigate } from "react-router";
import appConfigData from "../../../../app_config.json";

const steps = [
  { id: 1, name: "Request Details", icon: MapPin },
  { id: 2, name: "Forecast Parameters", icon: TrendingUp },
  { id: 3, name: "AI Forecast & Optimization", icon: Sparkles },
  { id: 4, name: "Review & Submit", icon: FileCheck },
];

type CategoryGroup = {
  name: string;
  children: string[];
};

type RegionGroup = {
  id: string;
  name: string;
  wilayas: string[];
};

type WarehouseInfo = {
  id: string;
  name: string;
  region: string;
  capacity: number;
  stockLevel: number;
  transportCost: number;
  holdingCost: number;
};

type ForecastItem = {
  week_start: string;
  region: string;
  sarimax_forecast: number;
};

type OptimizationMethodResult = {
  method: string;
  total_cost: number;
  service_level: number;
  runtime_seconds: number;
  mt: number;
};

type ForecastResponse = {
  parent_category: string;
  cat_group: string;
  period_weeks: number;
  forecast: ForecastItem[];
  region_percentages: Record<string, number>;
  allocation_by_region: Record<string, number>;
  allocation_by_warehouse: Record<string, number>;
  final_stock_by_warehouse: Record<string, number>;
  genetic: Record<string, unknown>;
  optimization_methods: OptimizationMethodResult[];
};

type AppConfig = {
  regions: RegionGroup[];
  categories: CategoryGroup[];
  warehouses: WarehouseInfo[];
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const regionColors: Record<string, string> = {
  east: "#4F46E5",
  north: "#10B981",
  south: "#F59E0B",
  west: "#EF4444",
};

const appConfig = appConfigData as AppConfig;
const regions = appConfig.regions;
const categoryGroups = appConfig.categories;
const warehouses = appConfig.warehouses;

const formatRegionLabel = (value: string) =>
  value
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());

const normalizeRegionKey = (value: string) => value.trim().toLowerCase();


export function StorageRequestWizard() {
  const [currentStep, setCurrentStep] = useState(1);
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    departureWilaya: "",
    subcategory: "",
    quantity: "",
    reorderThreshold: "",
    forecastDate: "",
    forecastPeriod: 4,
  });

  const [forecastResult, setForecastResult] = useState<ForecastResponse | null>(null);
  const [forecastError, setForecastError] = useState<string | null>(null);
  const [forecastLoading, setForecastLoading] = useState(false);

  const selectedWarehouses = useMemo(() => warehouses, []);
  const selectedWarehouseNames = "All available warehouses";

  const forecastView = useMemo(() => {
    if (!forecastResult) {
      return null;
    }

    const regionKeys = Object.keys(forecastResult.region_percentages ?? {}).sort((a, b) =>
      a.localeCompare(b),
    );
    const regionalDemand = regionKeys.map((region) => {
      const normalized = normalizeRegionKey(region);
      return {
        regionKey: region,
        name: formatRegionLabel(region),
        value: forecastResult.region_percentages[region] ?? 0,
        units: forecastResult.allocation_by_region[region] ?? 0,
        color: regionColors[normalized] ?? "#94A3B8",
      };
    });

    const weeklyMap: Record<string, { week: string; [key: string]: number | string }> = {};
    forecastResult.forecast.forEach((item) => {
      if (!weeklyMap[item.week_start]) {
        weeklyMap[item.week_start] = { week: item.week_start };
      }
      weeklyMap[item.week_start][item.region] = Math.round(item.sarimax_forecast);
    });

    const weeklyForecast = Object.values(weeklyMap).sort((a, b) =>
      String(a.week).localeCompare(String(b.week)),
    );

    const warehouseAllocation = selectedWarehouses.map((warehouse) => ({
      warehouse: warehouse.id,
      name: warehouse.name,
      region: formatRegionLabel(warehouse.region),
      current: warehouse.stockLevel,
      add: forecastResult.allocation_by_warehouse[warehouse.id] ?? 0,
      final: forecastResult.final_stock_by_warehouse[warehouse.id] ?? warehouse.stockLevel,
    }));

    const totalDemand = Object.values(forecastResult.allocation_by_region).reduce(
      (sum, value) => sum + value,
      0,
    );
    const stockNeeded = Object.values(forecastResult.allocation_by_warehouse).reduce(
      (sum, value) => sum + value,
      0,
    );
    const recommended = warehouseAllocation
      .filter((row) => row.add > 0)
      .sort((a, b) => b.add - a.add);
    const topWarehouse = recommended[0]?.name ?? "No additional stock";

    return {
      regionKeys,
      regionalDemand,
      weeklyForecast,
      warehouseAllocation,
      totalDemand,
      stockNeeded,
      recommendedCount: recommended.length,
      topWarehouse,
      periodWeeks: forecastResult.period_weeks,
      optimizationMethods: forecastResult.optimization_methods ?? [],
    };
  }, [forecastResult, selectedWarehouses]);

  useEffect(() => {
    if (currentStep !== 3) {
      return;
    }

    const quantityValue = Number(formData.quantity);
    if (!formData.subcategory || !Number.isFinite(quantityValue) || quantityValue <= 0) {
      setForecastResult(null);
      setForecastError("Enter a valid quantity and select a sub-category to run the forecast.");
      return;
    }

    if (!formData.forecastDate) {
      setForecastResult(null);
      setForecastError("Select a forecast start date to run the forecast.");
      return;
    }

    if (selectedWarehouses.length === 0) {
      setForecastResult(null);
      setForecastError("No warehouses are configured to run the forecast.");
      return;
    }

    const warehousesPayload = Object.fromEntries(
      selectedWarehouses.map((warehouse) => [
        warehouse.id,
        {
          capacity: warehouse.capacity,
          stock_level: warehouse.stockLevel,
          region: warehouse.region,
        },
      ]),
    );

    const transportCost = Object.fromEntries(
      selectedWarehouses.map((warehouse) => [warehouse.id, warehouse.transportCost]),
    );
    const holdingCost = Object.fromEntries(
      selectedWarehouses.map((warehouse) => [warehouse.id, warehouse.holdingCost]),
    );

    const payload = {
      countity: Math.round(quantityValue),
      warehouses: warehousesPayload,
      transport_cost: transportCost,
      holding_cost: holdingCost,
      category: formData.subcategory,
      forecast_date: formData.forecastDate,
      period: formData.forecastPeriod,
    };

    const controller = new AbortController();
    setForecastLoading(true);
    setForecastError(null);

    fetch(`${API_BASE_URL}/forecast/genetic`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const errorBody = await response.json().catch(() => null);
          throw new Error(errorBody?.detail ?? "Forecast request failed.");
        }
        return response.json();
      })
      .then((data: ForecastResponse) => {
        setForecastResult(data);
      })
      .catch((error) => {
        if (error.name === "AbortError") {
          return;
        }
        setForecastResult(null);
        setForecastError(error.message || "Forecast request failed.");
      })
      .finally(() => {
        setForecastLoading(false);
      });

    return () => controller.abort();
  }, [
    currentStep,
    formData.forecastPeriod,
    formData.forecastDate,
    formData.quantity,
    formData.subcategory,
    selectedWarehouses,
  ]);

  const handleNext = () => {
    if (currentStep < 4) setCurrentStep(currentStep + 1);
  };

  const handlePrev = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const handleSubmit = () => {
    navigate("/storage-requests");
  };

  return (
    <div className="min-h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        <h1 className="text-2xl font-bold text-gray-900">New Storage Request</h1>
        <p className="text-gray-600 mt-1">Create a storage request with AI-powered demand forecasting</p>
      </div>

      {/* Steps */}
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center flex-1">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-colors ${
                  currentStep > step.id
                    ? "bg-emerald-500 text-white"
                    : currentStep === step.id
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-200 text-gray-600"
                }`}>
                  {currentStep > step.id ? <Check className="w-5 h-5" /> : <step.icon className="w-5 h-5" />}
                </div>
                <div>
                  <p className="text-xs text-gray-500">Step {step.id}</p>
                  <p className={`text-sm font-medium ${currentStep >= step.id ? "text-gray-900" : "text-gray-500"}`}>
                    {step.name}
                  </p>
                </div>
              </div>
              {index < steps.length - 1 && (
                <div className={`flex-1 h-0.5 mx-4 ${currentStep > step.id ? "bg-emerald-500" : "bg-gray-200"}`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-8">
        <div className="max-w-5xl mx-auto">
          {currentStep === 1 && <Step1 formData={formData} setFormData={setFormData} />}
          {currentStep === 2 && <Step2 formData={formData} setFormData={setFormData} />}
          {currentStep === 3 && (
            <Step3
              forecastView={forecastView}
              forecastLoading={forecastLoading}
              forecastError={forecastError}
            />
          )}
          {currentStep === 4 && (
            <Step4
              formData={formData}
              forecastView={forecastView}
              selectedWarehouseNames={selectedWarehouseNames}
            />
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="fixed bottom-0 left-64 right-0 bg-white border-t border-gray-200 px-8 py-4">
        <div className="max-w-5xl mx-auto flex justify-between">
          <button
            onClick={handlePrev}
            disabled={currentStep === 1}
            className="flex items-center gap-2 px-6 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </button>
          {currentStep < 4 ? (
            <button
              onClick={handleNext}
              className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              className="flex items-center gap-2 px-8 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors"
            >
              <Check className="w-4 h-4" />
              Submit Request
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function Step1({ formData, setFormData }: any) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm mb-20">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-indigo-50 rounded-lg">
          <MapPin className="w-6 h-6 text-indigo-600" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Request Details</h2>
          <p className="text-sm text-gray-600">Specify your storage requirements and destination</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Departure Wilaya *</label>
          <select
            value={formData.departureWilaya}
            onChange={(e) => setFormData({ ...formData, departureWilaya: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Select wilaya</option>
            {regions.map((region) => (
              <optgroup key={region.id} label={region.name}>
                {region.wilayas.map((wilaya) => (
                  <option key={wilaya} value={wilaya}>{wilaya}</option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Sub-category *</label>
          <select
            value={formData.subcategory}
            onChange={(e) => setFormData({ ...formData, subcategory: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Select sub-category</option>
            {categoryGroups.map((group) => (
              <optgroup key={group.name} label={group.name}>
                {group.children.map((child) => (
                  <option key={`${group.name}-${child}`} value={child}>{child}</option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Quantity *</label>
          <input
            type="number"
            value={formData.quantity}
            onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
            placeholder="Enter quantity"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Reorder Threshold</label>
          <input
            type="number"
            value={formData.reorderThreshold}
            onChange={(e) => setFormData({ ...formData, reorderThreshold: e.target.value })}
            placeholder="Minimum stock level"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

      </div>
    </div>
  );
}

function Step2({ formData, setFormData }: any) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm mb-20">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-indigo-50 rounded-lg">
          <TrendingUp className="w-6 h-6 text-indigo-600" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Forecast Parameters</h2>
          <p className="text-sm text-gray-600">Configure AI forecasting settings</p>
        </div>
      </div>

      <div className="mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-2">Forecast Start Date *</label>
        <input
          type="date"
          value={formData.forecastDate}
          onChange={(e) => setFormData({ ...formData, forecastDate: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <p className="text-xs text-gray-500 mt-2">Forecasts will start from the week of this date.</p>
      </div>

      <div className="mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-2">Forecast Period (weeks)</label>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="1"
            max="12"
            value={formData.forecastPeriod}
            onChange={(e) => setFormData({ ...formData, forecastPeriod: parseInt(e.target.value) })}
            className="flex-1"
          />
          <span className="text-2xl font-bold text-indigo-600 w-16 text-right">{formData.forecastPeriod}</span>
        </div>
        <p className="text-xs text-gray-500 mt-2">AI will analyze historical data and forecast demand for the next {formData.forecastPeriod} weeks</p>
      </div>
    </div>
  );
}

function Step3({ forecastView, forecastLoading, forecastError }: any) {
  const optimizationMethods = forecastView?.optimizationMethods ?? [];
  const formatCost = (value: number) => new Intl.NumberFormat("en-US").format(Math.round(value));
  const formatPercent = (value: number) => `${Math.round(value * 100)}%`;
  const formatRuntime = (value: number) => `${value < 1 ? value.toFixed(2) : value.toFixed(1)} s`;

  return (
    <div className="space-y-6 mb-20">
      {/* Header with Timeline */}
      <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">AI Forecast & Genetic Optimization Results</h2>
            <p className="text-sm text-gray-600">Advanced analytics and stock allocation recommendations</p>
          </div>
        </div>

        {/* Timeline */}
        <div className="flex items-center justify-between mt-8">
          {["Forecast", "Regional Distribution", "Optimization", "Recommendation"].map((step, index) => (
            <div key={index} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </div>
                <p className="text-xs font-medium text-gray-900 mt-2">{step}</p>
              </div>
              {index < 3 && <div className="flex-1 h-0.5 bg-indigo-600 mx-2" />}
            </div>
          ))}
        </div>
      </div>

      {forecastLoading && (
        <div className="bg-indigo-50 border border-indigo-100 text-indigo-700 rounded-xl px-6 py-4">
          Running forecast and optimization...
        </div>
      )}

      {forecastError && (
        <div className="bg-red-50 border border-red-100 text-red-700 rounded-xl px-6 py-4">
          {forecastError}
        </div>
      )}

      {!forecastView && !forecastLoading && !forecastError && (
        <div className="bg-gray-50 border border-gray-200 text-gray-700 rounded-xl px-6 py-4">
          Complete the request details to generate forecast results.
        </div>
      )}

      {forecastView && (
        <>
          {/* KPI Cards */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
              <p className="text-sm text-gray-600 mb-1">Total Forecast Demand</p>
              <p className="text-3xl font-bold text-gray-900">
                {forecastView.totalDemand} <span className="text-lg text-gray-500">units</span>
              </p>
              <p className="text-xs text-emerald-600 mt-1">{forecastView.periodWeeks}-week period</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
              <p className="text-sm text-gray-600 mb-1">Additional Stock Needed</p>
              <p className="text-3xl font-bold text-indigo-600">
                {forecastView.stockNeeded} <span className="text-lg text-gray-500">units</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">Optimized allocation</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
              <p className="text-sm text-gray-600 mb-1">Recommended Warehouses</p>
              <p className="text-3xl font-bold text-gray-900">
                {forecastView.recommendedCount} <span className="text-lg text-gray-500">warehouse</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">{forecastView.topWarehouse}</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
              <p className="text-sm text-gray-600 mb-1">Forecast Accuracy (R²)</p>
              <p className="text-3xl font-bold text-emerald-600">94.2%</p>
              <p className="text-xs text-gray-500 mt-1">High confidence</p>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-2 gap-6">
            {/* Regional Demand Distribution */}
            <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Regional Demand Distribution</h3>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={forecastView.regionalDemand}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name} ${value.toFixed(1)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {forecastView.regionalDemand.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="grid grid-cols-2 gap-3 mt-4">
                {forecastView.regionalDemand.map((region, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: region.color }}></div>
                      <span className="text-sm font-medium text-gray-900">{region.name}</span>
                    </div>
                    <span className="text-sm font-bold text-gray-900">{region.units}u</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Weekly Forecast by Region */}
            <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Forecast by Region</h3>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={forecastView.weeklyForecast}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="week" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  {forecastView.regionKeys.map((regionKey) => (
                    <Line
                      key={regionKey}
                      type="monotone"
                      dataKey={regionKey}
                      name={formatRegionLabel(regionKey)}
                      stroke={regionColors[normalizeRegionKey(regionKey)] ?? "#94A3B8"}
                      strokeWidth={2}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Region Target Cards */}
          <div className="grid grid-cols-4 gap-4">
            {forecastView.regionalDemand.map((region, index) => (
              <div key={index} className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-semibold text-gray-900">{region.name} Region</h4>
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: region.color }}></div>
                </div>
                <p className="text-2xl font-bold text-gray-900">{region.units}</p>
                <p className="text-xs text-gray-500">units target</p>
                <div className="mt-3 bg-gray-100 rounded-full h-2">
                  <div
                    className="h-2 rounded-full transition-all"
                    style={{ backgroundColor: region.color, width: `${Math.min(region.value, 100)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>

          {/* Warehouse Allocation Table */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimized Warehouse Allocation</h3>
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Warehouse</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Region</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Current Stock</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Add</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Final Stock</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Status</th>
                </tr>
              </thead>
              <tbody>
                {forecastView.warehouseAllocation.map((warehouse, index) => (
                  <tr key={index} className="border-b border-gray-100">
                    <td className="py-4 px-4 font-medium text-gray-900">{warehouse.name}</td>
                    <td className="py-4 px-4 text-gray-600">{warehouse.region}</td>
                    <td className="py-4 px-4 text-right font-semibold text-gray-900">{warehouse.current}</td>
                    <td className="py-4 px-4 text-right">
                      <span className={`font-bold ${warehouse.add > 0 ? "text-emerald-600" : "text-gray-400"}`}>
                        +{warehouse.add}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-right font-bold text-indigo-600">{warehouse.final}</td>
                    <td className="py-4 px-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        warehouse.add > 0 ? "bg-emerald-100 text-emerald-800" : "bg-gray-100 text-gray-800"
                      }`}>
                        {warehouse.add > 0 ? "Action Required" : "Sufficient"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {optimizationMethods.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimization Method Comparison</h3>
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Method</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Total Cost</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Service Level</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Runtime</th>
                  </tr>
                </thead>
                <tbody>
                  {optimizationMethods.map((row: OptimizationMethodResult) => (
                    <tr key={row.method} className="border-b border-gray-100">
                      <td className="py-4 px-4 font-medium text-gray-900">{row.method}</td>
                      <td className="py-4 px-4 text-right font-semibold text-gray-900">{formatCost(row.total_cost)} DZD</td>
                      <td className="py-4 px-4 text-right text-gray-900">{formatPercent(row.service_level)}</td>
                      <td className="py-4 px-4 text-right text-gray-900">{formatRuntime(row.runtime_seconds)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function Step4({ formData, forecastView, selectedWarehouseNames }: any) {
  const fallbackUnits = Number(formData.quantity) || 0;
  const storageUnits = forecastView?.stockNeeded ?? fallbackUnits;
  const storageFee = storageUnits * formData.forecastPeriod * 20;
  const handlingFee = storageUnits > 0 ? 500 : 0;
  const totalCost = storageFee + handlingFee;
  const formatNumber = (value: number) => new Intl.NumberFormat("en-US").format(Math.round(value));

  return (
    <div className="space-y-6 mb-20">
      <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-emerald-50 rounded-lg">
            <FileCheck className="w-6 h-6 text-emerald-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Review & Submit</h2>
            <p className="text-sm text-gray-600">Please review your storage request before submission</p>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          <div className="border border-gray-200 rounded-xl p-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Request Details</h3>
            <dl className="space-y-3">
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Departure Wilaya:</dt>
                <dd className="text-sm font-medium text-gray-900">{formData.departureWilaya || "Not set"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Sub-category:</dt>
                <dd className="text-sm font-medium text-gray-900">{formData.subcategory || "Not set"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Warehouse Selection:</dt>
                <dd className="text-sm font-medium text-gray-900">{selectedWarehouseNames}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Quantity:</dt>
                <dd className="text-sm font-medium text-gray-900">{formData.quantity || "0"} units</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Reorder Threshold:</dt>
                <dd className="text-sm font-medium text-gray-900">{formData.reorderThreshold || "Not set"}</dd>
              </div>
            </dl>
          </div>

          <div className="border border-gray-200 rounded-xl p-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-4">AI Optimization Summary</h3>
            <dl className="space-y-3">
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Forecast Period:</dt>
                <dd className="text-sm font-medium text-gray-900">{formData.forecastPeriod} weeks</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Forecast Start Date:</dt>
                <dd className="text-sm font-medium text-gray-900">{formData.forecastDate || "Not set"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Total Demand:</dt>
                <dd className="text-sm font-medium text-gray-900">{forecastView?.totalDemand ?? 0} units</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Stock Needed:</dt>
                <dd className="text-sm font-medium text-emerald-600">
                  {forecastView ? `+${forecastView.stockNeeded} units` : "Not available"}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Target Warehouse:</dt>
                <dd className="text-sm font-medium text-gray-900">{forecastView?.topWarehouse || "Not available"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Accuracy:</dt>
                <dd className="text-sm font-medium text-gray-900">94.2% R²</dd>
              </div>
            </dl>
          </div>
        </div>

        {/* Cost Estimate */}
        <div className="bg-indigo-50 rounded-xl p-6 mb-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Estimated Cost</h3>
          <div className="space-y-2 mb-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Storage fee ({storageUnits} units × {formData.forecastPeriod} weeks):</span>
              <span className="font-medium text-gray-900">{formatNumber(storageFee)} DZD</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Handling fee:</span>
              <span className="font-medium text-gray-900">{formatNumber(handlingFee)} DZD</span>
            </div>
          </div>
          <div className="border-t border-indigo-200 pt-3 flex justify-between">
            <span className="text-base font-semibold text-gray-900">Total Estimated Cost:</span>
            <span className="text-xl font-bold text-indigo-600">{formatNumber(totalCost)} DZD</span>
          </div>
        </div>

        {/* Services Included */}
        <div className="bg-gray-50 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Services Included</h3>
          <div className="grid grid-cols-2 gap-3">
            {["Secure Storage", "Inventory Tracking", "24/7 Monitoring", "Insurance Coverage", "Online Dashboard", "Order Fulfillment"].map((service, index) => (
              <div key={index} className="flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-600" />
                <span className="text-sm text-gray-700">{service}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
