import { apiClient } from "./client";
import type { EQProfile } from "../types/eq";

export async function uploadEQProfile(
  sessionId: string,
  file: File,
  name: string,
): Promise<EQProfile> {
  const form = new FormData();
  form.append("file", file);
  form.append("name", name);
  const { data } = await apiClient.post(`/sessions/${sessionId}/eq/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listEQProfiles(sessionId: string): Promise<{ profile_id: string; name: string }[]> {
  const { data } = await apiClient.get(`/sessions/${sessionId}/eq`);
  return data;
}

export async function getEQProfile(sessionId: string, profileId: string): Promise<EQProfile> {
  const { data } = await apiClient.get(`/sessions/${sessionId}/eq/${profileId}`);
  return data;
}

export async function deleteEQProfile(sessionId: string, profileId: string): Promise<void> {
  await apiClient.delete(`/sessions/${sessionId}/eq/${profileId}`);
}
