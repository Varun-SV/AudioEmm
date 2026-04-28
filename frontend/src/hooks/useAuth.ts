import { useEffect } from "react";
import { getMe } from "../api/auth";
import { useAuthStore } from "../store/authStore";

export function useAuth() {
  const { accessToken, refreshToken, setTokens, setUser, logout } = useAuthStore();

  useEffect(() => {
    // Handle OAuth callback: tokens arrive as query params
    const params = new URLSearchParams(window.location.search);
    const at = params.get("access_token");
    const rt = params.get("refresh_token");
    if (at && rt) {
      setTokens(at, rt);
      // Clean URL
      window.history.replaceState({}, "", window.location.pathname);
    }
  }, [setTokens]);

  useEffect(() => {
    if (!accessToken) return;
    getMe(accessToken)
      .then(setUser)
      .catch(() => logout()); // Token invalid/expired — clear it
  }, [accessToken, setUser, logout]);

  return useAuthStore((s) => s.user);
}
