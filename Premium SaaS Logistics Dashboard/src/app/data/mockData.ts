// Per-seller mock data for all pages

export interface Product {
  id: number;
  name: string;
  sku: string;
  category: string;
  subcategory: string;
  stock: number;
  price: string;
  status: "active" | "low_stock" | "out_of_stock";
  variants: number;
  image: string;
}

export interface InventoryItem {
  warehouse: string;
  warehouseId: string;
  product: string;
  sku: string;
  quantity: number;
  reserved: number;
  threshold: number;
  status: "healthy" | "low" | "critical";
}

export interface StorageRequest {
  id: string;
  date: string;
  product: string;
  sku: string;
  quantity: number;
  warehouse: string;
  status: "approved" | "pending" | "processing" | "rejected";
  category: string;
}

export interface StockOperation {
  id: string;
  date: string;
  type: "inbound" | "outbound" | "transfer";
  product: string;
  sku: string;
  quantity: number;
  warehouse: string;
  status: "completed" | "in_progress" | "pending";
}

export interface KPI {
  label: string;
  value: string;
  change: string;
  trend: "up" | "down" | "neutral";
}

export interface Alert {
  type: "warning" | "info" | "success";
  message: string;
  time: string;
}

export interface WarehouseCapacity {
  warehouse: string;
  used: number;
  available: number;
}

export interface SellerMockData {
  kpis: KPI[];
  warehouseCapacity: WarehouseCapacity[];
  alerts: Alert[];
  products: Product[];
  inventory: InventoryItem[];
  storageRequests: StorageRequest[];
  stockOperations: StockOperation[];
}

// ── Yasser Brahim — Fashion & Clothing — North ──────────────────────────────
const yasserData: SellerMockData = {
  kpis: [
    { label: "Total Inventory Value", value: "3,180,000 DZD", change: "+14.2%", trend: "up" },
    { label: "Units in Stock", value: "8,640", change: "+11.4%", trend: "up" },
    { label: "Active Warehouses", value: "4", change: "0%", trend: "neutral" },
    { label: "Pending Requests", value: "7", change: "-3", trend: "down" },
    { label: "Orders This Month", value: "1,842", change: "+22.8%", trend: "up" },
    { label: "Forecast Accuracy (R²)", value: "93.6%", change: "+1.8%", trend: "up" },
    { label: "Stock Health Score", value: "89/100", change: "+6", trend: "up" },
    { label: "Monthly Logistics Cost", value: "142,000 DZD", change: "-2.4%", trend: "down" },
  ],
  warehouseCapacity: [
    { warehouse: "W1 - Algiers", used: 78, available: 22 },
    { warehouse: "W2 - Blida",   used: 53, available: 47 },
    { warehouse: "W9 - Tizi",    used: 69, available: 31 },
    { warehouse: "W11 - Bejaia", used: 81, available: 19 },
  ],
  alerts: [
    { type: "warning", message: "Low stock: Sneakers Atlas (SKU-F003) in W2-Blida — 14 units left", time: "1 hour ago" },
    { type: "success", message: "AI recommends restocking 200 units of Robe Été Sahara to W1-Algiers (Ramadan peak approaching)", time: "3 hours ago" },
    { type: "info",    message: "Storage request #SR-2026-041 approved — 300 units of Kaftan Festival queued for W11", time: "1 day ago" },
  ],
  products: [
    { id: 1, name: "Kaftan Festival",       sku: "SKU-F001", category: "Apparel & Accessories", subcategory: "Clothing",               stock: 420, price: "4,500 DZD",  status: "active",    variants: 8,  image: "https://images.unsplash.com/photo-1591130901921-b6c5c6e7de64?w=80&h=80&fit=crop" },
    { id: 2, name: "Robe Été Sahara",        sku: "SKU-F002", category: "Apparel & Accessories", subcategory: "Clothing",               stock: 310, price: "3,200 DZD",  status: "active",    variants: 6,  image: "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=80&h=80&fit=crop" },
    { id: 3, name: "Sneakers Atlas",          sku: "SKU-F003", category: "Apparel & Accessories", subcategory: "Shoes",                  stock: 14,  price: "6,800 DZD",  status: "low_stock", variants: 5,  image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=80&h=80&fit=crop" },
    { id: 4, name: "Sac Casbah Cuir",        sku: "SKU-F004", category: "Apparel & Accessories", subcategory: "Handbags, Wallets & Cases", stock: 185, price: "8,200 DZD", status: "active",   variants: 4,  image: "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=80&h=80&fit=crop" },
    { id: 5, name: "Bijoux Touareg Or",       sku: "SKU-F005", category: "Apparel & Accessories", subcategory: "Jewelry",                stock: 96,  price: "12,500 DZD", status: "active",    variants: 3,  image: "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=80&h=80&fit=crop" },
    { id: 6, name: "Parfum Nuit d'Alger",    sku: "SKU-F006", category: "Health & Beauty",        subcategory: "Cosmetics",              stock: 230, price: "3,800 DZD",  status: "active",    variants: 2,  image: "https://images.unsplash.com/photo-1541643600914-78b084683702?w=80&h=80&fit=crop" },
    { id: 7, name: "Sac à dos Urbain",        sku: "SKU-F007", category: "Luggage & Bags",         subcategory: "Backpacks",              stock: 142, price: "5,100 DZD",  status: "active",    variants: 4,  image: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=80&h=80&fit=crop" },
    { id: 8, name: "Valise Voyage Premium",   sku: "SKU-F008", category: "Luggage & Bags",         subcategory: "Suitcases",              stock: 0,   price: "14,000 DZD", status: "out_of_stock", variants: 3, image: "https://images.unsplash.com/photo-1565026057447-bc90a3dceb87?w=80&h=80&fit=crop" },
  ],
  inventory: [
    { warehouse: "W1 - Algiers Central", warehouseId: "W1",  product: "Kaftan Festival",     sku: "SKU-F001", quantity: 180, reserved: 30, threshold: 50, status: "healthy"  },
    { warehouse: "W1 - Algiers Central", warehouseId: "W1",  product: "Robe Été Sahara",      sku: "SKU-F002", quantity: 130, reserved: 20, threshold: 60, status: "healthy"  },
    { warehouse: "W2 - Blida Hub",       warehouseId: "W2",  product: "Sneakers Atlas",        sku: "SKU-F003", quantity: 14,  reserved: 4,  threshold: 30, status: "critical" },
    { warehouse: "W2 - Blida Hub",       warehouseId: "W2",  product: "Sac Casbah Cuir",       sku: "SKU-F004", quantity: 72,  reserved: 12, threshold: 40, status: "healthy"  },
    { warehouse: "W9 - Tizi Ouzou",      warehouseId: "W9",  product: "Bijoux Touareg Or",     sku: "SKU-F005", quantity: 45,  reserved: 8,  threshold: 25, status: "healthy"  },
    { warehouse: "W9 - Tizi Ouzou",      warehouseId: "W9",  product: "Parfum Nuit d'Alger",   sku: "SKU-F006", quantity: 38,  reserved: 6,  threshold: 40, status: "low"      },
    { warehouse: "W11 - Bejaia Coastal", warehouseId: "W11", product: "Sac à dos Urbain",       sku: "SKU-F007", quantity: 95,  reserved: 15, threshold: 30, status: "healthy"  },
    { warehouse: "W11 - Bejaia Coastal", warehouseId: "W11", product: "Valise Voyage Premium",  sku: "SKU-F008", quantity: 0,   reserved: 0,  threshold: 20, status: "critical" },
  ],
  storageRequests: [
    { id: "SR-2026-041", date: "2026-05-18", product: "Kaftan Festival",     sku: "SKU-F001", quantity: 300, warehouse: "W11 - Bejaia Coastal", status: "approved",   category: "Apparel & Accessories" },
    { id: "SR-2026-040", date: "2026-05-16", product: "Robe Été Sahara",      sku: "SKU-F002", quantity: 200, warehouse: "W1 - Algiers Central",  status: "processing", category: "Apparel & Accessories" },
    { id: "SR-2026-039", date: "2026-05-14", product: "Sneakers Atlas",        sku: "SKU-F003", quantity: 150, warehouse: "W2 - Blida Hub",         status: "pending",    category: "Apparel & Accessories" },
    { id: "SR-2026-038", date: "2026-05-12", product: "Sac Casbah Cuir",       sku: "SKU-F004", quantity: 80,  warehouse: "W9 - Tizi Ouzou",        status: "approved",   category: "Apparel & Accessories" },
    { id: "SR-2026-037", date: "2026-05-10", product: "Parfum Nuit d'Alger",   sku: "SKU-F006", quantity: 120, warehouse: "W1 - Algiers Central",   status: "rejected",   category: "Health & Beauty" },
  ],
  stockOperations: [
    { id: "OP-2026-081", date: "2026-05-20", type: "inbound",  product: "Kaftan Festival",    sku: "SKU-F001", quantity: 300, warehouse: "W11 - Bejaia",      status: "completed"  },
    { id: "OP-2026-080", date: "2026-05-19", type: "outbound", product: "Robe Été Sahara",     sku: "SKU-F002", quantity: 80,  warehouse: "W1 - Algiers",      status: "in_progress" },
    { id: "OP-2026-079", date: "2026-05-18", type: "transfer", product: "Sac Casbah Cuir",     sku: "SKU-F004", quantity: 40,  warehouse: "W9 → W2",           status: "completed"  },
    { id: "OP-2026-078", date: "2026-05-17", type: "inbound",  product: "Sneakers Atlas",       sku: "SKU-F003", quantity: 50,  warehouse: "W2 - Blida",        status: "pending"    },
    { id: "OP-2026-077", date: "2026-05-16", type: "outbound", product: "Bijoux Touareg Or",    sku: "SKU-F005", quantity: 22,  warehouse: "W9 - Tizi Ouzou",   status: "completed"  },
  ],
};

// ── Karim Boudiaf — Electronics — East ──────────────────────────────────────
const karimData: SellerMockData = {
  kpis: [
    { label: "Total Inventory Value", value: "8,920,000 DZD", change: "+9.7%",  trend: "up" },
    { label: "Units in Stock", value: "4,255", change: "+5.2%",  trend: "up" },
    { label: "Active Warehouses", value: "3", change: "0%",    trend: "neutral" },
    { label: "Pending Requests", value: "4", change: "-2",     trend: "down" },
    { label: "Orders This Month", value: "623", change: "+13.1%", trend: "up" },
    { label: "Forecast Accuracy (R²)", value: "95.1%", change: "+0.9%", trend: "up" },
    { label: "Stock Health Score", value: "82/100", change: "+3",    trend: "up" },
    { label: "Monthly Logistics Cost", value: "215,000 DZD", change: "-1.8%", trend: "down" },
  ],
  warehouseCapacity: [
    { warehouse: "W5 - Constantine", used: 88, available: 12 },
    { warehouse: "W6 - Annaba",      used: 44, available: 56 },
    { warehouse: "W12 - Setif",      used: 61, available: 39 },
  ],
  alerts: [
    { type: "warning", message: "W5-Constantine near full capacity (88%) — consider transferring laptops to W12-Setif", time: "30 min ago" },
    { type: "success", message: "AI forecast: +35% demand spike for Smartphones in EAST region next 4 weeks", time: "2 hours ago" },
    { type: "info",    message: "Pending approval: Storage request #SR-2026-055 for 80 units of Caméra HD", time: "6 hours ago" },
  ],
  products: [
    { id: 1, name: "Laptop Lenovo IdeaPad",    sku: "SKU-E001", category: "Electronics",      subcategory: "Computers",               stock: 142, price: "89,000 DZD", status: "active",    variants: 3, image: "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=80&h=80&fit=crop" },
    { id: 2, name: "Smartphone Samsung A55",   sku: "SKU-E002", category: "Electronics",      subcategory: "Communications",          stock: 310, price: "52,000 DZD", status: "active",    variants: 4, image: "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=80&h=80&fit=crop" },
    { id: 3, name: "Écouteurs Bluetooth Pro",  sku: "SKU-E003", category: "Electronics",      subcategory: "Audio",                   stock: 28,  price: "12,500 DZD", status: "low_stock", variants: 2, image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=80&h=80&fit=crop" },
    { id: 4, name: "Caméra Surveillance HD",   sku: "SKU-E004", category: "Cameras & Optics", subcategory: "Cameras",                 stock: 95,  price: "28,000 DZD", status: "active",    variants: 2, image: "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=80&h=80&fit=crop" },
    { id: 5, name: "Batterie Externe 20000mAh",sku: "SKU-E005", category: "Electronics",      subcategory: "Electronics Accessories", stock: 460, price: "4,200 DZD",  status: "active",    variants: 1, image: "https://images.unsplash.com/photo-1609592424745-b2e7a1c5c571?w=80&h=80&fit=crop" },
    { id: 6, name: "Switch Réseau 8 ports",    sku: "SKU-E006", category: "Electronics",      subcategory: "Networking",              stock: 74,  price: "9,800 DZD",  status: "active",    variants: 2, image: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=80&h=80&fit=crop" },
    { id: 7, name: "Imprimante HP LaserJet",   sku: "SKU-E007", category: "Office Supplies",  subcategory: "Office Equipment",        stock: 38,  price: "34,000 DZD", status: "active",    variants: 1, image: "https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?w=80&h=80&fit=crop" },
    { id: 8, name: "Disque Dur Externe 2To",   sku: "SKU-E008", category: "Electronics",      subcategory: "Components",              stock: 0,   price: "18,500 DZD", status: "out_of_stock", variants: 2, image: "https://images.unsplash.com/photo-1531492746076-161ca9bcad58?w=80&h=80&fit=crop" },
  ],
  inventory: [
    { warehouse: "W5 - Constantine East", warehouseId: "W5",  product: "Laptop Lenovo IdeaPad",     sku: "SKU-E001", quantity: 95,  reserved: 18, threshold: 20, status: "healthy"  },
    { warehouse: "W5 - Constantine East", warehouseId: "W5",  product: "Smartphone Samsung A55",    sku: "SKU-E002", quantity: 210, reserved: 40, threshold: 50, status: "healthy"  },
    { warehouse: "W6 - Annaba Forward",   warehouseId: "W6",  product: "Écouteurs Bluetooth Pro",   sku: "SKU-E003", quantity: 28,  reserved: 6,  threshold: 30, status: "low"      },
    { warehouse: "W6 - Annaba Forward",   warehouseId: "W6",  product: "Caméra Surveillance HD",    sku: "SKU-E004", quantity: 55,  reserved: 10, threshold: 25, status: "healthy"  },
    { warehouse: "W12 - Setif Inland",    warehouseId: "W12", product: "Batterie Externe 20000mAh", sku: "SKU-E005", quantity: 180, reserved: 22, threshold: 40, status: "healthy"  },
    { warehouse: "W12 - Setif Inland",    warehouseId: "W12", product: "Switch Réseau 8 ports",     sku: "SKU-E006", quantity: 42,  reserved: 5,  threshold: 20, status: "healthy"  },
    { warehouse: "W5 - Constantine East", warehouseId: "W5",  product: "Imprimante HP LaserJet",    sku: "SKU-E007", quantity: 22,  reserved: 3,  threshold: 10, status: "healthy"  },
    { warehouse: "W12 - Setif Inland",    warehouseId: "W12", product: "Disque Dur Externe 2To",    sku: "SKU-E008", quantity: 0,   reserved: 0,  threshold: 15, status: "critical" },
  ],
  storageRequests: [
    { id: "SR-2026-055", date: "2026-05-19", product: "Caméra Surveillance HD",    sku: "SKU-E004", quantity: 80,  warehouse: "W12 - Setif Inland",    status: "pending",    category: "Cameras & Optics" },
    { id: "SR-2026-054", date: "2026-05-17", product: "Smartphone Samsung A55",    sku: "SKU-E002", quantity: 200, warehouse: "W5 - Constantine East", status: "approved",   category: "Electronics" },
    { id: "SR-2026-053", date: "2026-05-15", product: "Laptop Lenovo IdeaPad",     sku: "SKU-E001", quantity: 50,  warehouse: "W6 - Annaba Forward",   status: "processing", category: "Electronics" },
    { id: "SR-2026-052", date: "2026-05-13", product: "Batterie Externe 20000mAh", sku: "SKU-E005", quantity: 300, warehouse: "W12 - Setif Inland",    status: "approved",   category: "Electronics" },
    { id: "SR-2026-051", date: "2026-05-10", product: "Disque Dur Externe 2To",    sku: "SKU-E008", quantity: 60,  warehouse: "W5 - Constantine East", status: "rejected",   category: "Electronics" },
  ],
  stockOperations: [
    { id: "OP-2026-091", date: "2026-05-21", type: "inbound",  product: "Smartphone Samsung A55",    sku: "SKU-E002", quantity: 200, warehouse: "W5 - Constantine",  status: "completed"   },
    { id: "OP-2026-090", date: "2026-05-20", type: "outbound", product: "Laptop Lenovo IdeaPad",     sku: "SKU-E001", quantity: 30,  warehouse: "W6 - Annaba",       status: "in_progress" },
    { id: "OP-2026-089", date: "2026-05-19", type: "transfer", product: "Batterie Externe 20000mAh", sku: "SKU-E005", quantity: 100, warehouse: "W5 → W12",          status: "completed"   },
    { id: "OP-2026-088", date: "2026-05-18", type: "inbound",  product: "Caméra Surveillance HD",    sku: "SKU-E004", quantity: 40,  warehouse: "W12 - Setif",       status: "pending"     },
    { id: "OP-2026-087", date: "2026-05-17", type: "outbound", product: "Switch Réseau 8 ports",     sku: "SKU-E006", quantity: 15,  warehouse: "W6 - Annaba",       status: "completed"   },
  ],
};

// ── Fatima Zerrouki — Home & Furniture — West ────────────────────────────────
const fatimaData: SellerMockData = {
  kpis: [
    { label: "Total Inventory Value", value: "5,640,000 DZD", change: "+7.3%",  trend: "up" },
    { label: "Units in Stock", value: "2,180", change: "+4.1%",  trend: "up" },
    { label: "Active Warehouses", value: "4", change: "0%",    trend: "neutral" },
    { label: "Pending Requests", value: "9", change: "+2",     trend: "up" },
    { label: "Orders This Month", value: "389", change: "+8.5%",  trend: "up" },
    { label: "Forecast Accuracy (R²)", value: "91.8%", change: "+1.2%", trend: "up" },
    { label: "Stock Health Score", value: "76/100", change: "-2",    trend: "down" },
    { label: "Monthly Logistics Cost", value: "198,000 DZD", change: "+4.1%", trend: "up" },
  ],
  warehouseCapacity: [
    { warehouse: "W3 - Oran",        used: 62, available: 38 },
    { warehouse: "W4 - Mostaganem", used: 18, available: 82 },
    { warehouse: "W10 - Relizane",  used: 74, available: 26 },
    { warehouse: "W13 - Tiaret",    used: 55, available: 45 },
  ],
  alerts: [
    { type: "warning", message: "Machine à laver (SKU-H004) in W4-Mostaganem — only 8 units, reorder urgently", time: "45 min ago" },
    { type: "info",    message: "9 storage requests pending approval — W3 and W10 have available capacity", time: "3 hours ago" },
    { type: "success", message: "AI optimized logistics cost: shifting Canapé Velours to W10-Relizane saves 12,000 DZD/month", time: "2 days ago" },
  ],
  products: [
    { id: 1, name: "Canapé L Velours Gris",    sku: "SKU-H001", category: "Furniture",    subcategory: "Living Room Furniture",     stock: 48,  price: "62,000 DZD",  status: "active",    variants: 4, image: "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=80&h=80&fit=crop" },
    { id: 2, name: "Lit King + Matelas",        sku: "SKU-H002", category: "Furniture",    subcategory: "Beds & Accessories",        stock: 35,  price: "48,000 DZD",  status: "active",    variants: 3, image: "https://images.unsplash.com/photo-1505693314120-0d443867891c?w=80&h=80&fit=crop" },
    { id: 3, name: "Cuisine Équipée Bois",      sku: "SKU-H003", category: "Furniture",    subcategory: "Kitchen & Dining Room Furniture", stock: 22, price: "120,000 DZD", status: "active", variants: 2, image: "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=80&h=80&fit=crop" },
    { id: 4, name: "Machine à Laver 8kg",       sku: "SKU-H004", category: "Home & Garden", subcategory: "Household Appliances",     stock: 8,   price: "58,000 DZD",  status: "low_stock", variants: 1, image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=80&h=80&fit=crop" },
    { id: 5, name: "Lampe Salon LED Arc",        sku: "SKU-H005", category: "Home & Garden", subcategory: "Lighting",                stock: 165, price: "8,500 DZD",   status: "active",    variants: 5, image: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=80&h=80&fit=crop" },
    { id: 6, name: "Parasol Jardin 3m",          sku: "SKU-H006", category: "Home & Garden", subcategory: "Lawn & Garden",           stock: 74,  price: "15,000 DZD",  status: "active",    variants: 3, image: "https://images.unsplash.com/photo-1600607688969-a5bfcd646154?w=80&h=80&fit=crop" },
    { id: 7, name: "Perceuse Visseuse Bosch",    sku: "SKU-H007", category: "Hardware",      subcategory: "Tools",                   stock: 92,  price: "18,000 DZD",  status: "active",    variants: 2, image: "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=80&h=80&fit=crop" },
    { id: 8, name: "Armoire Bureau Métal",       sku: "SKU-H008", category: "Furniture",    subcategory: "Office Furniture",         stock: 0,   price: "32,000 DZD",  status: "out_of_stock", variants: 2, image: "https://images.unsplash.com/photo-1594620302200-9a762244a156?w=80&h=80&fit=crop" },
  ],
  inventory: [
    { warehouse: "W3 - Oran North",       warehouseId: "W3",  product: "Canapé L Velours Gris",  sku: "SKU-H001", quantity: 28,  reserved: 6,  threshold: 10, status: "healthy"  },
    { warehouse: "W3 - Oran North",       warehouseId: "W3",  product: "Cuisine Équipée Bois",    sku: "SKU-H003", quantity: 12,  reserved: 2,  threshold: 5,  status: "healthy"  },
    { warehouse: "W4 - Mostaganem Depot", warehouseId: "W4",  product: "Machine à Laver 8kg",     sku: "SKU-H004", quantity: 8,   reserved: 2,  threshold: 10, status: "critical" },
    { warehouse: "W4 - Mostaganem Depot", warehouseId: "W4",  product: "Lit King + Matelas",      sku: "SKU-H002", quantity: 18,  reserved: 4,  threshold: 8,  status: "healthy"  },
    { warehouse: "W10 - Relizane",        warehouseId: "W10", product: "Lampe Salon LED Arc",     sku: "SKU-H005", quantity: 95,  reserved: 15, threshold: 20, status: "healthy"  },
    { warehouse: "W10 - Relizane",        warehouseId: "W10", product: "Parasol Jardin 3m",       sku: "SKU-H006", quantity: 38,  reserved: 5,  threshold: 15, status: "healthy"  },
    { warehouse: "W13 - Tiaret Regional", warehouseId: "W13", product: "Perceuse Visseuse Bosch", sku: "SKU-H007", quantity: 55,  reserved: 8,  threshold: 20, status: "healthy"  },
    { warehouse: "W13 - Tiaret Regional", warehouseId: "W13", product: "Armoire Bureau Métal",    sku: "SKU-H008", quantity: 0,   reserved: 0,  threshold: 5,  status: "critical" },
  ],
  storageRequests: [
    { id: "SR-2026-072", date: "2026-05-20", product: "Machine à Laver 8kg",    sku: "SKU-H004", quantity: 40,  warehouse: "W4 - Mostaganem Depot",  status: "pending",    category: "Home & Garden" },
    { id: "SR-2026-071", date: "2026-05-18", product: "Canapé L Velours Gris",  sku: "SKU-H001", quantity: 20,  warehouse: "W3 - Oran North",        status: "approved",   category: "Furniture" },
    { id: "SR-2026-070", date: "2026-05-16", product: "Lampe Salon LED Arc",    sku: "SKU-H005", quantity: 100, warehouse: "W10 - Relizane",         status: "processing", category: "Home & Garden" },
    { id: "SR-2026-069", date: "2026-05-14", product: "Perceuse Visseuse Bosch",sku: "SKU-H007", quantity: 60,  warehouse: "W13 - Tiaret Regional",  status: "approved",   category: "Hardware" },
    { id: "SR-2026-068", date: "2026-05-11", product: "Armoire Bureau Métal",   sku: "SKU-H008", quantity: 15,  warehouse: "W3 - Oran North",        status: "rejected",   category: "Furniture" },
  ],
  stockOperations: [
    { id: "OP-2026-101", date: "2026-05-21", type: "inbound",  product: "Canapé L Velours Gris",  sku: "SKU-H001", quantity: 20,  warehouse: "W3 - Oran",      status: "completed"   },
    { id: "OP-2026-100", date: "2026-05-20", type: "outbound", product: "Machine à Laver 8kg",    sku: "SKU-H004", quantity: 6,   warehouse: "W4 - Mostaganem", status: "in_progress" },
    { id: "OP-2026-099", date: "2026-05-19", type: "transfer", product: "Lampe Salon LED Arc",    sku: "SKU-H005", quantity: 50,  warehouse: "W13 → W10",       status: "completed"   },
    { id: "OP-2026-098", date: "2026-05-18", type: "inbound",  product: "Perceuse Visseuse Bosch",sku: "SKU-H007", quantity: 30,  warehouse: "W13 - Tiaret",    status: "pending"     },
    { id: "OP-2026-097", date: "2026-05-17", type: "outbound", product: "Parasol Jardin 3m",      sku: "SKU-H006", quantity: 18,  warehouse: "W10 - Relizane",  status: "completed"   },
  ],
};

// ── Omar Tebboune — Sports & Leisure — South ────────────────────────────────
const omarData: SellerMockData = {
  kpis: [
    { label: "Total Inventory Value", value: "2,810,000 DZD", change: "+18.6%", trend: "up" },
    { label: "Units in Stock", value: "3,420", change: "+15.3%", trend: "up" },
    { label: "Active Warehouses", value: "4", change: "0%",     trend: "neutral" },
    { label: "Pending Requests", value: "5", change: "-1",      trend: "down" },
    { label: "Orders This Month", value: "748", change: "+28.4%", trend: "up" },
    { label: "Forecast Accuracy (R²)", value: "90.4%", change: "+3.2%", trend: "up" },
    { label: "Stock Health Score", value: "84/100", change: "+8",     trend: "up" },
    { label: "Monthly Logistics Cost", value: "310,000 DZD", change: "+6.5%", trend: "up" },
  ],
  warehouseCapacity: [
    { warehouse: "W7 - Tamanrasset", used: 72, available: 28 },
    { warehouse: "W8 - Ouargla",     used: 34, available: 66 },
    { warehouse: "W14 - Biskra",     used: 65, available: 35 },
    { warehouse: "W15 - Ghardaia",   used: 12, available: 88 },
  ],
  alerts: [
    { type: "warning", message: "Vélo VTT Sahara (SKU-S003) — 11 units remaining in W14-Biskra, reorder before summer peak", time: "2 hours ago" },
    { type: "success", message: "AI detected +42% demand surge for camping gear across SOUTH region (summer season)", time: "4 hours ago" },
    { type: "info",    message: "Transfer completed: 60 tapis yoga from W7-Tamanrasset to W14-Biskra for faster fulfilment", time: "1 day ago" },
  ],
  products: [
    { id: 1, name: "Tapis Yoga Premium",      sku: "SKU-S001", category: "Sporting Goods",       subcategory: "Exercise & Fitness",    stock: 380, price: "3,500 DZD",  status: "active",    variants: 4, image: "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=80&h=80&fit=crop" },
    { id: 2, name: "Tente Camping 4 places",  sku: "SKU-S002", category: "Sporting Goods",       subcategory: "Outdoor Recreation",    stock: 145, price: "22,000 DZD", status: "active",    variants: 2, image: "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=80&h=80&fit=crop" },
    { id: 3, name: "Vélo VTT Sahara 27.5\"",  sku: "SKU-S003", category: "Sporting Goods",       subcategory: "Sports Equipment",      stock: 11,  price: "35,000 DZD", status: "low_stock", variants: 3, image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=80&h=80&fit=crop" },
    { id: 4, name: "Haltères Réglables 20kg", sku: "SKU-S004", category: "Sporting Goods",       subcategory: "Exercise & Fitness",    stock: 220, price: "12,000 DZD", status: "active",    variants: 1, image: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=80&h=80&fit=crop" },
    { id: 5, name: "Ballon Football Officiel",sku: "SKU-S005", category: "Sporting Goods",       subcategory: "Sports Equipment",      stock: 540, price: "2,800 DZD",  status: "active",    variants: 2, image: "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=80&h=80&fit=crop" },
    { id: 6, name: "Set Peinture Artiste",    sku: "SKU-S006", category: "Arts & Entertainment", subcategory: "Hobbies & Creative Arts",stock: 168, price: "4,200 DZD",  status: "active",    variants: 3, image: "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=80&h=80&fit=crop" },
    { id: 7, name: "Kit Survie Désert",       sku: "SKU-S007", category: "Sporting Goods",       subcategory: "Outdoor Recreation",    stock: 62,  price: "8,500 DZD",  status: "active",    variants: 1, image: "https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?w=80&h=80&fit=crop" },
    { id: 8, name: "Kayak Gonflable 2P",      sku: "SKU-S008", category: "Sporting Goods",       subcategory: "Outdoor Recreation",    stock: 0,   price: "48,000 DZD", status: "out_of_stock", variants: 1, image: "https://images.unsplash.com/photo-1587920617856-3b2d3a5f72c0?w=80&h=80&fit=crop" },
  ],
  inventory: [
    { warehouse: "W7 - Tamanrasset South", warehouseId: "W7",  product: "Tapis Yoga Premium",      sku: "SKU-S001", quantity: 120, reserved: 20, threshold: 30, status: "healthy"  },
    { warehouse: "W7 - Tamanrasset South", warehouseId: "W7",  product: "Kit Survie Désert",       sku: "SKU-S007", quantity: 40,  reserved: 8,  threshold: 15, status: "healthy"  },
    { warehouse: "W8 - Ouargla Remote",    warehouseId: "W8",  product: "Haltères Réglables 20kg", sku: "SKU-S004", quantity: 95,  reserved: 10, threshold: 25, status: "healthy"  },
    { warehouse: "W8 - Ouargla Remote",    warehouseId: "W8",  product: "Ballon Football Officiel",sku: "SKU-S005", quantity: 260, reserved: 30, threshold: 50, status: "healthy"  },
    { warehouse: "W14 - Biskra Gateway",   warehouseId: "W14", product: "Vélo VTT Sahara 27.5\"",  sku: "SKU-S003", quantity: 11,  reserved: 3,  threshold: 15, status: "critical" },
    { warehouse: "W14 - Biskra Gateway",   warehouseId: "W14", product: "Tente Camping 4 places",  sku: "SKU-S002", quantity: 85,  reserved: 12, threshold: 20, status: "healthy"  },
    { warehouse: "W15 - Ghardaia Hub",     warehouseId: "W15", product: "Set Peinture Artiste",    sku: "SKU-S006", quantity: 95,  reserved: 8,  threshold: 20, status: "healthy"  },
    { warehouse: "W15 - Ghardaia Hub",     warehouseId: "W15", product: "Kayak Gonflable 2P",      sku: "SKU-S008", quantity: 0,   reserved: 0,  threshold: 5,  status: "critical" },
  ],
  storageRequests: [
    { id: "SR-2026-063", date: "2026-05-21", product: "Vélo VTT Sahara 27.5\"",  sku: "SKU-S003", quantity: 50,  warehouse: "W14 - Biskra Gateway",    status: "pending",    category: "Sporting Goods" },
    { id: "SR-2026-062", date: "2026-05-19", product: "Tente Camping 4 places",  sku: "SKU-S002", quantity: 80,  warehouse: "W7 - Tamanrasset South",  status: "approved",   category: "Sporting Goods" },
    { id: "SR-2026-061", date: "2026-05-17", product: "Tapis Yoga Premium",      sku: "SKU-S001", quantity: 200, warehouse: "W8 - Ouargla Remote",     status: "processing", category: "Sporting Goods" },
    { id: "SR-2026-060", date: "2026-05-14", product: "Haltères Réglables 20kg", sku: "SKU-S004", quantity: 100, warehouse: "W15 - Ghardaia Hub",      status: "approved",   category: "Sporting Goods" },
    { id: "SR-2026-059", date: "2026-05-11", product: "Kayak Gonflable 2P",      sku: "SKU-S008", quantity: 10,  warehouse: "W14 - Biskra Gateway",    status: "rejected",   category: "Sporting Goods" },
  ],
  stockOperations: [
    { id: "OP-2026-111", date: "2026-05-21", type: "inbound",  product: "Tente Camping 4 places",  sku: "SKU-S002", quantity: 80,  warehouse: "W7 - Tamanrasset",  status: "completed"   },
    { id: "OP-2026-110", date: "2026-05-20", type: "transfer", product: "Tapis Yoga Premium",      sku: "SKU-S001", quantity: 60,  warehouse: "W7 → W14",          status: "completed"   },
    { id: "OP-2026-109", date: "2026-05-19", type: "outbound", product: "Ballon Football Officiel",sku: "SKU-S005", quantity: 120, warehouse: "W8 - Ouargla",      status: "in_progress" },
    { id: "OP-2026-108", date: "2026-05-18", type: "inbound",  product: "Haltères Réglables 20kg", sku: "SKU-S004", quantity: 100, warehouse: "W15 - Ghardaia",    status: "pending"     },
    { id: "OP-2026-107", date: "2026-05-17", type: "outbound", product: "Set Peinture Artiste",    sku: "SKU-S006", quantity: 45,  warehouse: "W15 - Ghardaia",    status: "completed"   },
  ],
};

export const SELLER_MOCK_DATA: Record<string, SellerMockData> = {
  yasser: yasserData,
  karim:  karimData,
  fatima: fatimaData,
  omar:   omarData,
};
