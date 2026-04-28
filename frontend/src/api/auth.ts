import { apiClient } from "./client";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserRead {
  id: string;
  email: string;
  display_name: string | null;
  is_verified: boolean;
}

export async function register(
  email: string,
  password: string,
  displayName?: string,
): Promise<TokenResponse> {
  const { data } = await apiClient.post("/auth/register", {
    email,
    password,
    display_name: displayName ?? null,
  });
  return data;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post("/auth/login", { email, password });
  return data;
}

export async function refreshTokens(refreshToken: string): Promise<TokenResponse> {
  const { data } = await apiClient.post("/auth/refresh", { refresh_token: refreshToken });
  return data;
}

export async function getMe(accessToken: string): Promise<UserRead> {
  const { data } = await apiClient.get("/auth/me", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return data;
}

export function googleLoginUrl(): string {
  return "/api/auth/google/redirect";
}

export function githubLoginUrl(): string {
  return "/api/auth/github/redirect";
}
