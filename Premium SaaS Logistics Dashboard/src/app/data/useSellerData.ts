import { useAuth } from "../auth/AuthContext";
import { SELLER_MOCK_DATA } from "./mockData";
import { SELLER_DATA } from "./sellerData";

export function useSellerData() {
  const { account } = useAuth();
  const id = account?.id ?? "yasser";
  return {
    mock: SELLER_MOCK_DATA[id] ?? SELLER_MOCK_DATA.yasser,
    config: SELLER_DATA[id] ?? SELLER_DATA.yasser,
    account,
  };
}
