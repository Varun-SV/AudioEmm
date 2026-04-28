import { useState } from "react";
import { useRoomStore } from "../../store/roomStore";
import { useSessionStore } from "../../store/sessionStore";
import { startSimulation, getSimulationStatus } from "../../api/simulation";

export function RoomStats() {
  const { length: L, width: W, height: H, rt60_preview, speakers } = useRoomStore();
  const { sessionId, setRirId } = useSessionStore();
  const [simStatus, setSimStatus] = useState<"idle" | "running" | "done" | "error">("idle");
  const [simResult, setSimResult] = useState<Record<string, unknown> | null>(null);
  const [errMsg, setErrMsg] = useState("");

  const volume = L * W * H;

  async function runSimulation() {
    if (!sessionId) return;
    setSimStatus("running");
    setErrMsg("");
    try {
      const { job_id } = await startSimulation(sessionId);
      // Poll until done
      const poll = setInterval(async () => {
        const status = await getSimulationStatus(sessionId, job_id);
        if (status.status === "done") {
          clearInterval(poll);
          setSimResult(status.result ?? null);
          if (status.result?.rir_id) {
            setRirId(status.result.rir_id as string);
          }
          setSimStatus("done");
        } else if (status.status === "error") {
          clearInterval(poll);
          setErrMsg(status.error ?? "Unknown error");
          setSimStatus("error");
        }
      }, 2000);
    } catch (e) {
      setSimStatus("error");
      setErrMsg("Failed to start simulation");
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <h3 className="font-semibold text-white text-base">Room Stats</h3>

      <div className="grid grid-cols-2 gap-2 text-sm">
        <Stat label="Dimensions" value={`${L}×${W}×${H} m`} />
        <Stat label="Volume" value={`${volume.toFixed(1)} m³`} />
        <Stat label="RT60 (preview)" value={rt60_preview ? `${rt60_preview.toFixed(2)} s` : "—"} />
        <Stat label="Speakers" value={String(speakers.length)} />
      </div>

      {simResult && (
        <div className="grid grid-cols-2 gap-2 text-sm mt-1">
          <Stat label="RT60 (measured)" value={simResult.rt60_computed ? `${(simResult.rt60_computed as number).toFixed(2)} s` : "—"} accent />
          <Stat label="Direct delay" value={`${(simResult.direct_delay_ms as number ?? 0).toFixed(1)} ms`} accent />
          <Stat label="Reflections" value={String(simResult.reflection_count ?? "—")} accent />
        </div>
      )}

      {errMsg && <p className="text-red-400 text-xs">{errMsg}</p>}

      <button
        onClick={runSimulation}
        disabled={simStatus === "running" || !sessionId}
        className="mt-1 py-2 rounded-lg font-semibold text-sm transition-all bg-accent text-white hover:bg-accent/80 disabled:opacity-40"
      >
        {simStatus === "running" ? "Simulating…" : "Run Acoustic Simulation"}
      </button>

      {simStatus === "done" && (
        <p className="text-green-400 text-xs text-center">
          RIR generated — go to Audio tab to process
        </p>
      )}
    </div>
  );
}

function Stat({ label, value, accent = false }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className={`rounded-lg p-2 ${accent ? "bg-accent/10 border border-accent/30" : "bg-white/5"}`}>
      <div className="text-muted text-xs">{label}</div>
      <div className={`font-semibold ${accent ? "text-accent" : "text-white"}`}>{value}</div>
    </div>
  );
}
