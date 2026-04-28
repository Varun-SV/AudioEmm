import { useState } from "react";
import { processAudio, getAudioResult, previewUrl } from "../../api/audio";
import { useSessionStore } from "../../store/sessionStore";
import { useAudioStore } from "../../store/audioStore";
import { WaveformPlayer } from "./WaveformPlayer";

export function ProcessingStatus() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const rirId = useSessionStore((s) => s.rirId);
  const {
    uploadId, uploadFilename, uploadDuration,
    processingState, resultUrl, resultDuration,
    errorMessage, activeEqProfileId,
    setProcessingState, setResult, setError,
  } = useAudioStore();

  async function startProcessing() {
    if (!sessionId || !uploadId || !rirId) return;
    setProcessingState("processing");
    try {
      const { job_id } = await processAudio(
        sessionId, uploadId, rirId, activeEqProfileId ?? undefined,
      );
      const interval = setInterval(async () => {
        const res = await getAudioResult(sessionId, job_id);
        if (res.status === "done" && res.result_url) {
          clearInterval(interval);
          setResult(res.result_url, res.duration_s ?? 0);
        } else if (res.status === "error") {
          clearInterval(interval);
          setError("Processing failed");
        }
      }, 2000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Processing failed");
    }
  }

  if (!uploadId) return null;

  const dryPreviewUrl = sessionId ? previewUrl(sessionId, uploadId) : undefined;

  return (
    <div className="flex flex-col gap-4">
      {/* Dry audio waveform */}
      {dryPreviewUrl && (
        <WaveformPlayer
          url={dryPreviewUrl}
          label={`Dry — ${uploadFilename ?? ""} (${uploadDuration?.toFixed(1)} s)`}
          accentColor="#a8a8b3"
        />
      )}

      {errorMessage && <p className="text-red-400 text-xs">{errorMessage}</p>}

      {!rirId && (
        <p className="text-yellow-400 text-xs text-center">
          Waiting for room simulation… move a speaker or click "Deep Simulate Now"
        </p>
      )}

      <button
        onClick={startProcessing}
        disabled={!rirId || processingState === "processing" || !uploadId}
        className="py-2 rounded-lg font-semibold text-sm bg-accent text-white hover:bg-accent/80 disabled:opacity-40 transition-all"
      >
        {processingState === "processing" ? "Processing…" : "Process Audio"}
      </button>

      {/* Processed binaural waveform */}
      {resultUrl && (
        <div className="flex flex-col gap-2">
          <WaveformPlayer url={resultUrl} label={`Binaural result (${resultDuration?.toFixed(1)} s)`} />
          <a
            href={resultUrl}
            download
            className="text-center py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-medium transition-colors"
          >
            Download WAV
          </a>
        </div>
      )}
    </div>
  );
}
