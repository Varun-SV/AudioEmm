import { apiClient } from "./client";

export interface ModelUploadResponse {
  model_id: string;
  filename: string;
  url: string;
  size_bytes: number;
}

export async function uploadModel(
  sessionId: string,
  file: File,
): Promise<ModelUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await apiClient.post<ModelUploadResponse>(
    `/sessions/${sessionId}/models/upload`,
    form,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return data;
}
