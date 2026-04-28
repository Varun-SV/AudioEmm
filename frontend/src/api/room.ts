import { apiClient } from "./client";
import type { RoomConfig } from "../types/room";

export async function getRoom(sessionId: string): Promise<RoomConfig> {
  const { data } = await apiClient.get(`/sessions/${sessionId}/room`);
  return data;
}

export async function putRoom(sessionId: string, config: RoomConfig): Promise<RoomConfig> {
  const { data } = await apiClient.put(`/sessions/${sessionId}/room`, config);
  return data;
}

export async function getPresets(): Promise<string[]> {
  const { data } = await apiClient.get("/sessions/_/room/presets");
  return data;
}

export async function getPreset(sessionId: string, name: string): Promise<RoomConfig> {
  const { data } = await apiClient.get(`/sessions/${sessionId}/room/presets/${name}`);
  return data;
}
