import { apiClient } from "./client";
import type { RoomConfig } from "../types/room";

export interface RoomSaveRead {
  id: string;
  name: string;
  config: RoomConfig;
  created_at: string;
  updated_at: string;
}

export interface AudioUploadRead {
  id: string;
  filename: string;
  duration_s: number;
  sample_rate: number;
  created_at: string;
}

export interface ProcessedResultRead {
  id: string;
  upload_id: string;
  room_save_id: string | null;
  duration_s: number;
  download_url: string;
  created_at: string;
}

export async function listRooms(): Promise<RoomSaveRead[]> {
  const { data } = await apiClient.get("/library/rooms");
  return data;
}

export async function saveRoom(name: string, config: RoomConfig): Promise<RoomSaveRead> {
  const { data } = await apiClient.post("/library/rooms", { name, config });
  return data;
}

export async function deleteRoom(id: string): Promise<void> {
  await apiClient.delete(`/library/rooms/${id}`);
}

export async function listAudio(): Promise<AudioUploadRead[]> {
  const { data } = await apiClient.get("/library/audio");
  return data;
}

export async function listResults(): Promise<ProcessedResultRead[]> {
  const { data } = await apiClient.get("/library/results");
  return data;
}

export async function deleteResult(id: string): Promise<void> {
  await apiClient.delete(`/library/results/${id}`);
}
