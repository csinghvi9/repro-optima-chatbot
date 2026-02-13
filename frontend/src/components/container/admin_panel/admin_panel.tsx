"use client";
import React, { useEffect, useState } from "react";

// Your Screens/Components
import Dashboard from "@/components/container/dashboard/dashboard";
import Login from "@/components/container/login/login";
import admin from "@/components/admin_auth/auth";

// Your token expiry checker
const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split(".")[1])) as { expires: number };
    const exp = payload.expires; // expiry timestamp in seconds
    const now = Math.floor(Date.now() / 1000);
    return now >= exp;
  } catch {
    return true;
  }
};



const AdminPanel: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const { refreshAccessToken } = admin();

  useEffect(() => {
    const verifyToken = async () => {
      const accessToken = sessionStorage.getItem("admin_access_token");
      const refreshToken = sessionStorage.getItem("admin_refresh_token");

      if (!accessToken || !refreshToken) {
        setIsAuthenticated(false);
        return;
      }

      // Check access token expiry
      if (isTokenExpired(accessToken)) {
        try {
          const data = await refreshAccessToken(refreshToken);

          sessionStorage.setItem("admin_access_token", data.accessToken);
          sessionStorage.setItem("admin_refresh_token", data.refreshToken);

          setIsAuthenticated(true);
        } catch (error) {
          // Refresh failed → logout
          sessionStorage.removeItem("admin_access_token");
          sessionStorage.removeItem("admin_refresh_token");
          setIsAuthenticated(false);
        }
      } else {
        setIsAuthenticated(true);
      }
    };

    verifyToken();
  }, []);

  // Show loader while checking tokens
  if (isAuthenticated === null) return <div>Loading...</div>;

  return isAuthenticated ? <Dashboard /> : <Login />;
};

export default AdminPanel;
