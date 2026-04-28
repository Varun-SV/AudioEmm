import { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";

interface Props {
  url: string;
  label?: string;
  accentColor?: string;
}

export function WaveformPlayer({ url, label, accentColor = "#e94560" }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WaveSurfer | null>(null);
  const [playing, setPlaying] = useState(false);
  const [duration, setDuration] = useState<number | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!containerRef.current || !url) return;

    wsRef.current?.destroy();
    setLoading(true);
    setError(false);
    setPlaying(false);

    const ws = WaveSurfer.create({
      container: containerRef.current,
      waveColor: "rgba(255,255,255,0.2)",
      progressColor: accentColor,
      cursorColor: accentColor,
      barWidth: 2,
      barGap: 1,
      height: 56,
      normalize: true,
      backend: "WebAudio",
    });

    ws.load(url);
    ws.on("ready", () => {
      setDuration(ws.getDuration());
      setLoading(false);
    });
    ws.on("audioprocess", () => setCurrentTime(ws.getCurrentTime()));
    ws.on("interaction", () => setCurrentTime(ws.getCurrentTime()));
    ws.on("play", () => setPlaying(true));
    ws.on("pause", () => setPlaying(false));
    ws.on("finish", () => setPlaying(false));
    ws.on("error", () => { setError(true); setLoading(false); });

    wsRef.current = ws;
    return () => { ws.destroy(); wsRef.current = null; };
  }, [url, accentColor]);

  function fmt(s: number) {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60).toString().padStart(2, "0");
    return `${m}:${sec}`;
  }

  return (
    <div className="rounded-xl bg-white/5 border border-white/10 p-3 flex flex-col gap-2">
      {label && <div className="text-xs text-muted font-semibold uppercase tracking-wide">{label}</div>}

      {loading && !error && (
        <div className="h-14 flex items-center justify-center text-muted text-xs">Loading waveform…</div>
      )}
      {error && (
        <div className="h-14 flex items-center justify-center text-red-400 text-xs">Could not load audio</div>
      )}

      <div ref={containerRef} className={loading || error ? "hidden" : ""} />

      {!loading && !error && (
        <div className="flex items-center gap-3">
          <button
            onClick={() => wsRef.current?.playPause()}
            className="w-8 h-8 rounded-full flex items-center justify-center text-white transition-colors"
            style={{ background: accentColor }}
          >
            {playing ? "⏸" : "▶"}
          </button>
          <div className="flex-1 text-xs text-muted">
            {fmt(currentTime)} / {duration != null ? fmt(duration) : "—"}
          </div>
        </div>
      )}
    </div>
  );
}
