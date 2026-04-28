import { useRef, useState } from "react";
import { uploadAudio } from "../../api/audio";
import { useSessionStore } from "../../store/sessionStore";
import { useAudioStore } from "../../store/audioStore";

export function AudioUploader() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const { setUpload, setProcessingState, setError } = useAudioStore();
  const [progress, setProgress] = useState(0);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    if (!sessionId) return;
    setProcessingState("uploading");
    setProgress(0);
    try {
      const res = await uploadAudio(sessionId, file, setProgress);
      setUpload(res.upload_id, res.filename, res.duration_s);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed");
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => inputRef.current?.click()}
      className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
        dragging
          ? "border-accent bg-accent/10"
          : "border-white/20 hover:border-white/40 bg-white/5"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept="audio/*"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
      />
      <div className="text-3xl mb-2">🎵</div>
      <p className="text-white font-medium">Drop audio file here</p>
      <p className="text-muted text-xs mt-1">WAV, MP3, FLAC, AIFF — up to 200 MB</p>
      {progress > 0 && progress < 100 && (
        <div className="mt-3 h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-accent transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  );
}
