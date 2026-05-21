import { createBrowserRouter } from "react-router";
import { Layout } from "./components/Layout";
import { Dashboard } from "./pages/Dashboard";
import { WarehousesMarketplace } from "./pages/WarehousesMarketplace";
import { Products } from "./pages/Products";
import { Inventory } from "./pages/Inventory";
import { StorageRequests } from "./pages/StorageRequests";
import { StorageRequestWizard } from "./pages/StorageRequestWizard";
import { StockOperations } from "./pages/StockOperations";
import { Reports } from "./pages/Reports";
import { TeamRoles } from "./pages/TeamRoles";
import { Billing } from "./pages/Billing";
import { Settings } from "./pages/Settings";
import { NotFound } from "./pages/NotFound";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Dashboard },
      { path: "warehouses-marketplace", Component: WarehousesMarketplace },
      { path: "products", Component: Products },
      { path: "inventory", Component: Inventory },
      { path: "storage-requests", Component: StorageRequests },
      { path: "storage-requests/new", Component: StorageRequestWizard },
      { path: "stock-operations", Component: StockOperations },
      { path: "reports", Component: Reports },
      { path: "team-roles", Component: TeamRoles },
      { path: "billing", Component: Billing },
      { path: "settings", Component: Settings },
      { path: "*", Component: NotFound },
    ],
  },
]);
