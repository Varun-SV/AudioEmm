import { apiClient } from "./client";
import type { AudioUploadResponse, AudioResultResponse } from "../types/audio";

export async function uploadAudio(
  sessionId: string,
  file: File,
  onProgress?: (pct: number) => void,
): Promise<AudioUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await apiClient.post(`/sessions/${sessionId}/audio/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {
      if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100));
    },
  });
  return data;
}

export async function processAudio(
  sessionId: string,
  uploadId: string,
  rirId: string,
  eqProfileId?: string,
): Promise<{ job_id: string }> {
  const { data } = await apiClient.post(`/sessions/${sessionId}/audio/process`, {
    upload_id: uploadId,
    rir_id: rirId,
    eq_profile_id: eqProfileId ?? null,
  });
  return data;
}

export async function getAudioResult(
  sessionId: string,
  jobId: string,
): Promise<AudioResultResponse> {
  const { data } = await apiClient.get(`/sessions/${sessionId}/audio/result/${jobId}`);
  return data;
}

export function downloadUrl(sessionId: string, jobId: string): string {
  return `/api/sessions/${sessionId}/audio/download/${jobId}`;
}

export function previewUrl(sessionId: string, uploadId: string): string {
  return `/api/sessions/${sessionId}/audio/preview/${uploadId}`;
}
