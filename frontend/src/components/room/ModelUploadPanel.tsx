import { useRef, useState, useCallback } from "react";
import { uploadModel } from "../../api/models";
import { useSessionStore } from "../../store/sessionStore";
import { useRoomStore } from "../../store/roomStore";
import { SUPPORTED_MODEL_EXTENSIONS } from "../../types/room";
import type { ModelObject } from "../../types/room";

function makeModelObject(resp: { model_id: string; filename: string; url: string }, L: number, W: number): ModelObject {
  return {
    id: crypto.randomUUID(),
    modelId: resp.model_id,
    filename: resp.filename,
    url: resp.url,
    material: "drywall",
    wallSurface: "floor",
    position: [L / 2, 0, W / 2],
    rotation: [0, 0, 0],
    scale: [1, 1, 1],
    bboxW: 1,
    bboxH: 1,
    bboxD: 1,
  };
}

export function ModelUploadPanel() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionId = useSessionStore((s) => s.sessionId);
  const { addModelObject, modelObjects, removeModelObject, length: L, width: W } = useRoomStore();

  const handleFiles = useCallback(
    async (files: FileList | null) => {
      if (!files || !sessionId) return;
      setError(null);
      setUploading(true);
      try {
        for (const file of Array.from(files)) {
          const ext = "." + file.name.split(".").pop()?.toLowerCase();
          if (!SUPPORTED_MODEL_EXTENSIONS.includes(ext)) {
            setError(`Unsupported format: ${ext}`);
            continue;
          }
          const resp = await uploadModel(sessionId, file);
          addModelObject(makeModelObject(resp, L, W));
        }
      } catch (e: any) {
        setError(e?.response?.data?.detail ?? "Upload failed");
      } finally {
        setUploading(false);
      }
    },
    [sessionId, addModelObject, L, W],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles],
  );

  return (
    <div className="flex flex-col gap-2">
      {/* Drop zone / upload button */}
      <div
        className="border-2 border-dashed border-white/20 hover:border-white/40 rounded-lg
                   p-3 text-center cursor-pointer transition-colors"
        onClick={() => fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onDragEnter={(e) => e.preventDefault()}
      >
        <div className="text-lg mb-1">📦</div>
        <div className="text-xs text-gray-300 leading-tight">
          {uploading ? "Uploading…" : "Drop 3D file here or click to browse"}
        </div>
        <div className="text-[10px] text-gray-500 mt-1">
          {SUPPORTED_MODEL_EXTENSIONS.join(" · ")}
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept={SUPPORTED_MODEL_EXTENSIONS.join(",")}
        multiple
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />

      {error && (
        <p className="text-xs text-red-400 px-1">{error}</p>
      )}

      {/* List of uploaded models in this session */}
      {modelObjects.length > 0 && (
        <div className="flex flex-col gap-1 mt-1">
          {modelObjects.map((obj) => (
            <div
              key={obj.id}
              className="flex items-center justify-between bg-white/5 rounded px-2 py-1.5 text-xs"
            >
              <span className="text-gray-300 truncate max-w-[130px]">{obj.filename}</span>
              <button
                onClick={() => removeModelObject(obj.id)}
                className="text-gray-500 hover:text-red-400 ml-2 flex-shrink-0"
                title="Remove"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
