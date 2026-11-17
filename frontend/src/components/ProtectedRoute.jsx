import { Navigate, Outlet, useLocation } from "react-router-dom";

import { homeForRole, useAuth } from "../context/AuthContext";
import { FullPageLoader } from "./Loading";

/**
 * Blocks a route until the user is logged in with one of the allowed roles.
 * `role` may be a single role string or an array of roles.
 */
export default function ProtectedRoute({ role }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <FullPageLoader label="Checking your session..." />;

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  const allowed = Array.isArray(role) ? role : role ? [role] : null;
  if (allowed && !allowed.includes(user.role)) {
    return <Navigate to={homeForRole(user.role)} replace />;
  }

  return <Outlet />;
}
