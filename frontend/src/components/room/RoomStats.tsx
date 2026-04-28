import { useState, useEffect, useRef, useCallback } from "react";
import { useRoomStore } from "../../store/roomStore";
import { useSessionStore } from "../../store/sessionStore";
import {
  startSimulation,
  simulatePreview,
  createProgressEventSource,
  getSimulationStatus,
} from "../../api/simulation";

const DEEP_SIM_IDLE_MS = 5000;

export function RoomStats() {
  const { length: L, width: W, height: H, rt60_preview, speakers } = useRoomStore();
  const { sessionId, setRirId } = useSessionStore();

  const [simStatus, setSimStatus] = useState<"idle" | "running" | "done" | "error">("idle");
  const [simResult, setSimResult] = useState<Record<string, unknown> | null>(null);
  const [previewResult, setPreviewResult] = useState<{
    rt60_sabine: number;
    rt60_computed: number | null;
    direct_delay_ms: number;
    reflection_count: number;
  } | null>(null);
  const [progress, setProgress] = useState(0);
  const [errMsg, setErrMsg] = useState("");

  const deepSimTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const esRef = useRef<EventSource | null>(null);
  const prevRoomKey = useRef("");

  const volume = L * W * H;

  // Key that changes whenever the room layout changes (triggers preview + deep sim timer)
  const roomKey = `${L}_${W}_${H}_${speakers.map(s => `${s.x},${s.y},${s.z}`).join("|")}`;

  const runPreview = useCallback(async () => {
    if (!sessionId) return;
    try {
      const result = await simulatePreview(sessionId);
      setPreviewResult(result);
    } catch {
      // silent — preview is best-effort
    }
  }, [sessionId]);

  const runDeepSimulation = useCallback(async () => {
    if (!sessionId) return;
    setSimStatus("running");
    setErrMsg("");
    setProgress(5);
    try {
      const { job_id } = await startSimulation(sessionId);

      // Close any existing SSE connection
      esRef.current?.close();
      const es = createProgressEventSource(sessionId, job_id);
      esRef.current = es;

      es.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.status === "running") setProgress((p) => Math.min(p + 10, 85));
        if (data.status === "done") {
          es.close();
          setSimResult(data.result ?? null);
          if (data.result?.rir_id) setRirId(data.result.rir_id as string);
          setSimStatus("done");
          setProgress(100);
        }
        if (data.status === "error") {
          es.close();
          setErrMsg(data.error ?? "Simulation failed");
          setSimStatus("error");
          setProgress(0);
        }
      };
      es.onerror = () => {
        es.close();
        // Fall back to polling if SSE fails
        pollFallback(sessionId, job_id);
      };
    } catch {
      setSimStatus("error");
      setErrMsg("Failed to start simulation");
      setProgress(0);
    }
  }, [sessionId, setRirId]);

  async function pollFallback(sid: string, jobId: string) {
    const interval = setInterval(async () => {
      const s = await getSimulationStatus(sid, jobId);
      if (s.status === "done") {
        clearInterval(interval);
        setSimResult(s.result ?? null);
        if (s.result?.rir_id) setRirId(s.result.rir_id as string);
        setSimStatus("done");
        setProgress(100);
      } else if (s.status === "error") {
        clearInterval(interval);
        setErrMsg(s.error ?? "Simulation failed");
        setSimStatus("error");
      }
    }, 2000);
  }

  // On room change: run fast preview, then schedule deep simulation after 5 s of no further changes
  useEffect(() => {
    if (!sessionId || roomKey === prevRoomKey.current) return;
    prevRoomKey.current = roomKey;

    runPreview();

    if (deepSimTimer.current) clearTimeout(deepSimTimer.current);
    deepSimTimer.current = setTimeout(() => {
      if (simStatus !== "running") runDeepSimulation();
    }, DEEP_SIM_IDLE_MS);

    return () => {
      if (deepSimTimer.current) clearTimeout(deepSimTimer.current);
    };
  }, [roomKey, sessionId]);

  return (
    <div className="flex flex-col gap-3">
      <h3 className="font-semibold text-white text-base">Room Stats</h3>

      <div className="grid grid-cols-2 gap-2 text-sm">
        <Stat label="Dimensions" value={`${L}×${W}×${H} m`} />
        <Stat label="Volume" value={`${volume.toFixed(1)} m³`} />
        <Stat
          label="RT60 (Sabine)"
          value={
            previewResult?.rt60_sabine != null
              ? `${previewResult.rt60_sabine.toFixed(2)} s`
              : rt60_preview
              ? `${rt60_preview.toFixed(2)} s`
              : "—"
          }
        />
        <Stat label="Speakers" value={String(speakers.length)} />
      </div>

      {previewResult && (
        <div className="grid grid-cols-2 gap-2 text-sm">
          <Stat label="Direct delay" value={`${previewResult.direct_delay_ms.toFixed(1)} ms`} />
          <Stat label="Reflections (est.)" value={String(previewResult.reflection_count)} />
        </div>
      )}

      {simResult && (
        <div className="grid grid-cols-2 gap-2 text-sm mt-1">
          <Stat
            label="RT60 (measured)"
            value={simResult.rt60_computed ? `${(simResult.rt60_computed as number).toFixed(2)} s` : "—"}
            accent
          />
          <Stat
            label="Reflections (full)"
            value={String(simResult.reflection_count ?? "—")}
            accent
          />
        </div>
      )}

      {/* Progress bar */}
      {simStatus === "running" && (
        <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-accent transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {errMsg && <p className="text-red-400 text-xs">{errMsg}</p>}

      <button
        onClick={runDeepSimulation}
        disabled={simStatus === "running" || !sessionId}
        className="py-2 rounded-lg font-semibold text-sm transition-all bg-accent text-white hover:bg-accent/80 disabled:opacity-40"
      >
        {simStatus === "running" ? "Simulating…" : "Deep Simulate Now"}
      </button>

      {simStatus === "done" && (
        <p className="text-green-400 text-xs text-center">
          RIR ready — switch to Audio tab to process
        </p>
      )}

      <p className="text-muted text-xs text-center">
        Auto-simulates {DEEP_SIM_IDLE_MS / 1000}s after last change
      </p>
    </div>
  );
}

function Stat({
  label,
  value,
  accent = false,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div
      className={`rounded-lg p-2 ${
        accent ? "bg-accent/10 border border-accent/30" : "bg-white/5"
      }`}
    >
      <div className="text-muted text-xs">{label}</div>
      <div className={`font-semibold ${accent ? "text-accent" : "text-white"}`}>{value}</div>
    </div>
  );
}
