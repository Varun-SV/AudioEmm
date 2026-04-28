import { useEffect, useState } from "react";
import { listRooms, saveRoom, deleteRoom, listResults, deleteResult } from "../../api/library";
import { useRoomStore } from "../../store/roomStore";
import type { RoomSaveRead, ProcessedResultRead } from "../../api/library";

interface Props {
  onClose: () => void;
}

export function LibraryDrawer({ onClose }: Props) {
  const [tab, setTab] = useState<"rooms" | "results">("rooms");
  const [rooms, setRooms] = useState<RoomSaveRead[]>([]);
  const [results, setResults] = useState<ProcessedResultRead[]>([]);
  const [saveName, setSaveName] = useState("");
  const [saving, setSaving] = useState(false);
  const { loadConfig, length, width, height, surfaces, speakers, listener } = useRoomStore();

  useEffect(() => {
    loadLibrary();
  }, []);

  async function loadLibrary() {
    const [r, res] = await Promise.all([
      listRooms().catch(() => [] as RoomSaveRead[]),
      listResults().catch(() => [] as ProcessedResultRead[]),
    ]);
    setRooms(r);
    setResults(res);
  }

  async function handleSaveRoom() {
    if (!saveName.trim()) return;
    setSaving(true);
    try {
      const saved = await saveRoom(saveName.trim(), { length, width, height, surfaces, speakers, listener });
      setRooms((prev) => [saved, ...prev]);
      setSaveName("");
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteRoom(id: string) {
    await deleteRoom(id).catch(() => {});
    setRooms((prev) => prev.filter((r) => r.id !== id));
  }

  async function handleDeleteResult(id: string) {
    await deleteResult(id).catch(() => {});
    setResults((prev) => prev.filter((r) => r.id !== id));
  }

  return (
    <div
      className="fixed inset-0 z-40 flex"
      onClick={onClose}
    >
      <div className="flex-1" />
      <div
        className="w-80 h-full bg-panel border-l border-white/10 flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-4 py-4 border-b border-white/10 flex items-center justify-between">
          <h2 className="text-white font-bold text-base">Library</h2>
          <button onClick={onClose} className="text-muted hover:text-white text-xl transition-colors">
            ×
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-white/10">
          {(["rooms", "results"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`flex-1 py-2.5 text-xs font-semibold capitalize transition-colors ${
                tab === t ? "text-accent border-b-2 border-accent" : "text-muted hover:text-white"
              }`}
            >
              {t === "rooms" ? "Saved Rooms" : "Audio History"}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-4">
          {tab === "rooms" && (
            <div className="flex flex-col gap-3">
              {/* Save current room */}
              <div className="flex gap-2">
                <input
                  value={saveName}
                  onChange={(e) => setSaveName(e.target.value)}
                  placeholder="Room name…"
                  className="flex-1 bg-white/5 border border-white/10 rounded-lg px-2 py-1.5 text-sm text-white placeholder:text-muted focus:outline-none focus:border-accent"
                  onKeyDown={(e) => e.key === "Enter" && handleSaveRoom()}
                />
                <button
                  onClick={handleSaveRoom}
                  disabled={saving || !saveName.trim()}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-accent text-white disabled:opacity-40 transition-all"
                >
                  {saving ? "…" : "Save"}
                </button>
              </div>

              {rooms.length === 0 ? (
                <p className="text-muted text-xs text-center py-6">No saved rooms yet</p>
              ) : (
                rooms.map((r) => (
                  <div
                    key={r.id}
                    className="flex items-center gap-2 rounded-lg bg-white/5 border border-white/10 p-2.5"
                  >
                    <button
                      onClick={() => { loadConfig(r.config); onClose(); }}
                      className="flex-1 text-left"
                    >
                      <div className="text-white text-sm font-medium">{r.name}</div>
                      <div className="text-muted text-xs">
                        {r.config.length}×{r.config.width}×{r.config.height} m ·{" "}
                        {new Date(r.updated_at).toLocaleDateString()}
                      </div>
                    </button>
                    <button
                      onClick={() => handleDeleteRoom(r.id)}
                      className="text-red-400 hover:text-red-300 text-xs px-1.5"
                    >
                      ✕
                    </button>
                  </div>
                ))
              )}
            </div>
          )}

          {tab === "results" && (
            <div className="flex flex-col gap-3">
              {results.length === 0 ? (
                <p className="text-muted text-xs text-center py-6">No processed audio yet</p>
              ) : (
                results.map((r) => (
                  <div
                    key={r.id}
                    className="flex items-center gap-2 rounded-lg bg-white/5 border border-white/10 p-2.5"
                  >
                    <div className="flex-1">
                      <div className="text-white text-sm font-medium">
                        Binaural {r.id.slice(0, 8)}
                      </div>
                      <div className="text-muted text-xs">
                        {r.duration_s.toFixed(1)} s · {new Date(r.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <a
                      href={r.download_url}
                      download
                      className="text-accent hover:text-accent/80 text-xs px-1.5"
                    >
                      ↓
                    </a>
                    <button
                      onClick={() => handleDeleteResult(r.id)}
                      className="text-red-400 hover:text-red-300 text-xs px-1.5"
                    >
                      ✕
                    </button>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
