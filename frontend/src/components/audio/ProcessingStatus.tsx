import { useState } from "react";
import { processAudio, getAudioResult, downloadUrl } from "../../api/audio";
import { useSessionStore } from "../../store/sessionStore";
import { useAudioStore } from "../../store/audioStore";

export function ProcessingStatus() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const rirId = useSessionStore((s) => s.rirId);
  const {
    uploadId, uploadFilename, uploadDuration,
    processingState, resultUrl, resultDuration,
    errorMessage, activeEqProfileId,
    setProcessingState, setResult, setError,
  } = useAudioStore();

  const [polling, setPolling] = useState(false);

  async function startProcessing() {
    if (!sessionId || !uploadId || !rirId) return;
    setProcessingState("processing");
    try {
      const { job_id } = await processAudio(
        sessionId, uploadId, rirId, activeEqProfileId ?? undefined,
      );
      setPolling(true);
      const interval = setInterval(async () => {
        const res = await getAudioResult(sessionId, job_id);
        if (res.status === "done" && res.result_url) {
          clearInterval(interval);
          setPolling(false);
          setResult(res.result_url, res.duration_s ?? 0);
        } else if (res.status === "error") {
          clearInterval(interval);
          setPolling(false);
          setError("Processing failed");
        }
      }, 2000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Processing failed");
    }
  }

  if (!uploadId) return null;

  return (
    <div className="flex flex-col gap-3">
      <div className="rounded-lg bg-white/5 p-3 text-sm">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-white font-medium">{uploadFilename}</div>
            <div className="text-muted text-xs">{uploadDuration?.toFixed(1)} s</div>
          </div>
          {!rirId && (
            <span className="text-yellow-400 text-xs">Run simulation first</span>
          )}
        </div>
      </div>

      {errorMessage && <p className="text-red-400 text-xs">{errorMessage}</p>}

      {resultUrl && (
        <div className="flex flex-col gap-2">
          <audio controls src={resultUrl} className="w-full" />
          <a
            href={resultUrl}
            download
            className="text-center py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-medium transition-colors"
          >
            Download WAV
          </a>
        </div>
      )}

      <button
        onClick={startProcessing}
        disabled={!rirId || processingState === "processing" || !uploadId}
        className="py-2 rounded-lg font-semibold text-sm bg-accent text-white hover:bg-accent/80 disabled:opacity-40 transition-all"
      >
        {processingState === "processing" ? "Processing…" : "Process Audio"}
      </button>
    </div>
  );
}
