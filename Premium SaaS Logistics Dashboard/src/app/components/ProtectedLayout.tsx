import { Navigate } from "react-router";
import { useAuth } from "../auth/AuthContext";
import { Layout } from "./Layout";

export function ProtectedLayout() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Layout />;
}
