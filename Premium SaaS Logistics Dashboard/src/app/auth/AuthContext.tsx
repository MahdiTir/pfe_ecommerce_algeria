import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { type Account, DEMO_ACCOUNTS } from "./accounts";

interface AuthContextType {
  account: Account | null;
  isAuthenticated: boolean;
  login: (account: Account) => void;
  logout: () => void;
  switchAccount: (accountId: string) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const STORAGE_KEY = "wasl_account_id";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<Account | null>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return DEMO_ACCOUNTS.find((a) => a.id === saved) ?? null;
  });

  const login = useCallback((acc: Account) => {
    setAccount(acc);
    localStorage.setItem(STORAGE_KEY, acc.id);
  }, []);

  const logout = useCallback(() => {
    setAccount(null);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const switchAccount = useCallback(
    (accountId: string) => {
      const acc = DEMO_ACCOUNTS.find((a) => a.id === accountId);
      if (acc) login(acc);
    },
    [login]
  );

  return (
    <AuthContext.Provider
      value={{ account, isAuthenticated: !!account, login, logout, switchAccount }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
