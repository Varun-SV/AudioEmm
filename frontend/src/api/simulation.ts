import { apiClient } from "./client";

export async function startSimulation(
  sessionId: string,
  maxOrder = 3,
  rirDuration = 1.0,
) {
  const { data } = await apiClient.post(`/sessions/${sessionId}/simulate`, {
    max_order: maxOrder,
    rir_duration: rirDuration,
  });
  return data as { job_id: string; status: string };
}

export async function getSimulationStatus(sessionId: string, jobId: string) {
  const { data } = await apiClient.get(
    `/sessions/${sessionId}/simulate/status/${jobId}`,
  );
  return data as { job_id: string; status: string; result?: Record<string, unknown>; error?: string };
}
