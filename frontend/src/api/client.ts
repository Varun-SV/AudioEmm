import axios from "axios";

export const apiClient = axios.create({
  baseURL: "/api",
  timeout: 30000,
});

// Inject Bearer token from localStorage if present
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("audioemm_access_token");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});
