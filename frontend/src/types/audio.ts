export interface AudioUploadResponse {
  upload_id: string;
  filename: string;
  duration_s: number;
  sample_rate: number;
}

export interface AudioResultResponse {
  job_id: string;
  status: string;
  result_url?: string;
  duration_s?: number;
}

export type ProcessingState = "idle" | "uploading" | "processing" | "done" | "error";
