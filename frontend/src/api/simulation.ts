import { apiClient } from "./client";

export async function startSimulation(
  sessionId: string,
  maxOrder = 6,
  rirDuration = 1.0,
) {
  const { data } = await apiClient.post(`/sessions/${sessionId}/simulate`, {
    max_order: maxOrder,
    rir_duration: rirDuration,
  });
  return data as { job_id: string; status: string };
}

export async function simulatePreview(sessionId: string) {
  const { data } = await apiClient.post(`/sessions/${sessionId}/simulate/preview`);
  return data as {
    rt60_sabine: number;
    rt60_computed: number | null;
    direct_delay_ms: number;
    reflection_count: number;
  };
}

export async function getSimulationStatus(sessionId: string, jobId: string) {
  const { data } = await apiClient.get(
    `/sessions/${sessionId}/simulate/status/${jobId}`,
  );
  return data as {
    job_id: string;
    status: string;
    result?: Record<string, unknown>;
    error?: string;
  };
}

export function createProgressEventSource(sessionId: string, jobId: string): EventSource {
  return new EventSource(`/api/sessions/${sessionId}/simulate/progress/${jobId}`);
}
