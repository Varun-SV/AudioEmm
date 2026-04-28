import { apiClient } from "./client";

export async function createSession() {
  const { data } = await apiClient.post("/sessions");
  return data as { session_id: string; created_at: string; expires_at: string };
}

export async function getSession(sessionId: string) {
  const { data } = await apiClient.get(`/sessions/${sessionId}`);
  return data;
}

export async function deleteSession(sessionId: string) {
  await apiClient.delete(`/sessions/${sessionId}`);
}
