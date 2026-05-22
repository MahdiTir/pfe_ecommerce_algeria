export interface WarehouseInfo {
  id: string;
  name: string;
  region: string;
  capacity: number;
  stockLevel: number;
  transportCost: number;
  holdingCost: number;
}

export interface CategoryGroup {
  name: string;
  children: string[];
}

export interface RegionGroup {
  id: string;
  name: string;
  wilayas: string[];
}

export interface SellerConfig {
  regions: RegionGroup[];
  categories: CategoryGroup[];
  warehouses: WarehouseInfo[];
}

// All regions — shared for the wilaya departure dropdown
const ALL_REGIONS: RegionGroup[] = [
  {
    id: "NORTH",
    name: "North",
    wilayas: [
      "Alger", "Blida", "Boumerdes", "Tipaza", "Medea",
      "Ain Defla", "Bouira", "Tizi Ouzou", "Bejaia", "Chlef", "M'Sila",
    ],
  },
  {
    id: "EAST",
    name: "East",
    wilayas: [
      "Constantine", "Annaba", "Skikda", "Jijel", "Setif", "Batna",
      "Khenchela", "Oum El Bouaghi", "Tebessa", "Guelma", "Souk Ahras",
      "Mila", "Bordj Bou Arreridj", "El Tarf",
    ],
  },
  {
    id: "WEST",
    name: "West",
    wilayas: [
      "Oran", "Tlemcen", "Sidi Bel Abbes", "Mostaganem", "Mascara",
      "Relizane", "Saida", "Tiaret", "Tissemsilt", "Ain Temouchent", "Naama",
    ],
  },
  {
    id: "SOUTH",
    name: "South",
    wilayas: [
      "Adrar", "Tamanrasset", "Illizi", "Tindouf", "Bechar", "El Oued",
      "Ouargla", "Ghardaia", "Laghouat", "Biskra", "El Bayadh", "Djelfa",
      "Timimoun", "Bordj Badji Mokhtar", "Ouled Djellal", "Beni Abbes",
      "In Salah", "In Guezzam", "Touggourt", "Djanet", "El Mghair", "El Meniaa",
    ],
  },
];

// ── Yasser Brahim — Fashion & Clothing — North ──────────────────────────────
const yasserConfig: SellerConfig = {
  regions: ALL_REGIONS,
  categories: [
    {
      name: "Apparel & Accessories",
      children: ["Clothing", "Clothing Accessories", "Costumes & Accessories", "Handbag & Wallet Accessories", "Handbags, Wallets & Cases", "Jewelry", "Shoe Accessories", "Shoes"],
    },
    {
      name: "Health & Beauty",
      children: ["Cosmetics", "Personal Care", "Health Care"],
    },
    {
      name: "Luggage & Bags",
      children: ["Backpacks", "Briefcases", "Luggage Accessories", "Suitcases"],
    },
    {
      name: "Baby & Toddler",
      children: ["Baby Bathing", "Nursing & Feeding", "Strollers & Accessories"],
    },
  ],
  warehouses: [
    { id: "W1",  name: "W1 - Algiers Central",  region: "NORTH", capacity: 400, stockLevel: 120, transportCost: 2.8, holdingCost: 1.05 },
    { id: "W2",  name: "W2 - Blida Hub",         region: "NORTH", capacity: 300, stockLevel: 40,  transportCost: 2.4, holdingCost: 1.25 },
    { id: "W9",  name: "W9 - Tizi Ouzou",        region: "NORTH", capacity: 260, stockLevel: 60,  transportCost: 3.0, holdingCost: 1.15 },
    { id: "W11", name: "W11 - Bejaia Coastal",   region: "NORTH", capacity: 320, stockLevel: 80,  transportCost: 3.4, holdingCost: 1.1  },
  ],
};

// ── Karim Boudiaf — Electronics — East ──────────────────────────────────────
const karimConfig: SellerConfig = {
  regions: ALL_REGIONS,
  categories: [
    {
      name: "Electronics",
      children: ["Audio", "Communications", "Components", "Computers", "Electronics Accessories", "Networking", "Video"],
    },
    {
      name: "Cameras & Optics",
      children: ["Camera & Optic Accessories", "Cameras", "Optics"],
    },
    {
      name: "Software",
      children: ["Business & Productivity", "Security & Utilities"],
    },
    {
      name: "Office Supplies",
      children: ["General Office Supplies", "Office Equipment", "Presentation Supplies"],
    },
    {
      name: "Media",
      children: ["Books", "DVDs & Videos", "Music"],
    },
  ],
  warehouses: [
    { id: "W5",  name: "W5 - Constantine East", region: "EAST", capacity: 500, stockLevel: 200, transportCost: 3.6, holdingCost: 0.95 },
    { id: "W6",  name: "W6 - Annaba Forward",   region: "EAST", capacity: 260, stockLevel: 30,  transportCost: 3.9, holdingCost: 1.6  },
    { id: "W12", name: "W12 - Setif Inland",    region: "EAST", capacity: 280, stockLevel: 25,  transportCost: 3.0, holdingCost: 1.0  },
  ],
};

// ── Fatima Zerrouki — Home & Furniture — West ────────────────────────────────
const fatimaConfig: SellerConfig = {
  regions: ALL_REGIONS,
  categories: [
    {
      name: "Furniture",
      children: ["Baby & Toddler Furniture", "Beds & Accessories", "Furniture Accessories", "Kitchen & Dining Room Furniture", "Living Room Furniture", "Office Furniture", "Outdoor Furniture"],
    },
    {
      name: "Home & Garden",
      children: ["Bathroom Accessories", "Household Appliances", "Household Supplies", "Kitchen & Dining", "Lawn & Garden", "Lighting", "Linens & Bedding"],
    },
    {
      name: "Hardware",
      children: ["Building Materials", "Fasteners", "Fittings", "Hardware Accessories", "Tools"],
    },
    {
      name: "Business & Industrial",
      children: ["Food Service", "Industrial Storage", "Electrical Equipment"],
    },
  ],
  warehouses: [
    { id: "W3",  name: "W3 - Oran North",        region: "WEST", capacity: 350, stockLevel: 10, transportCost: 3.1, holdingCost: 1.2  },
    { id: "W4",  name: "W4 - Mostaganem Depot",  region: "WEST", capacity: 220, stockLevel: 0,  transportCost: 2.6, holdingCost: 1.4  },
    { id: "W10", name: "W10 - Relizane",          region: "WEST", capacity: 200, stockLevel: 20, transportCost: 2.2, holdingCost: 1.3  },
    { id: "W13", name: "W13 - Tiaret Regional",   region: "WEST", capacity: 240, stockLevel: 15, transportCost: 2.7, holdingCost: 1.35 },
  ],
};

// ── Omar Tebboune — Sports & Leisure — South ────────────────────────────────
const omarConfig: SellerConfig = {
  regions: ALL_REGIONS,
  categories: [
    {
      name: "Sporting Goods",
      children: ["Exercise & Fitness", "Outdoor Recreation", "Sports Equipment"],
    },
    {
      name: "Arts & Entertainment",
      children: ["Hobbies & Creative Arts", "Party & Celebration", "Toys & Games"],
    },
    {
      name: "Animals & Pet Supplies",
      children: ["Pet Supplies"],
    },
    {
      name: "Vehicles & Parts",
      children: ["Vehicle Parts & Accessories", "Vehicles"],
    },
    {
      name: "Food, Beverages & Tobacco",
      children: ["Beverages", "Food Items"],
    },
  ],
  warehouses: [
    { id: "W7",  name: "W7 - Tamanrasset South", region: "SOUTH", capacity: 180, stockLevel: 35, transportCost: 5.2, holdingCost: 1.9  },
    { id: "W8",  name: "W8 - Ouargla Remote",    region: "SOUTH", capacity: 240, stockLevel: 5,  transportCost: 4.8, holdingCost: 1.7  },
    { id: "W14", name: "W14 - Biskra Gateway",   region: "SOUTH", capacity: 260, stockLevel: 50, transportCost: 4.2, holdingCost: 1.6  },
    { id: "W15", name: "W15 - Ghardaia Hub",     region: "SOUTH", capacity: 200, stockLevel: 0,  transportCost: 4.5, holdingCost: 1.45 },
  ],
};

export const SELLER_DATA: Record<string, SellerConfig> = {
  yasser: yasserConfig,
  karim:  karimConfig,
  fatima: fatimaConfig,
  omar:   omarConfig,
};
