import { useSessionStore } from "../../store/sessionStore";
import { useRoomStore } from "../../store/roomStore";
import { getPreset } from "../../api/room";

const PRESETS = [
  { key: "living_room", label: "Living Room", icon: "🛋️", desc: "5×4×3 m" },
  { key: "bedroom",     label: "Bedroom",     icon: "🛏️", desc: "4×3.5×2.8 m" },
  { key: "office",      label: "Office",      icon: "🖥️", desc: "4×3×2.8 m" },
  { key: "studio",      label: "Studio",      icon: "🎙️", desc: "6×5×3.5 m" },
];

export function PresetSelector() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const { loadConfig } = useRoomStore();

  async function load(key: string) {
    if (!sessionId) return;
    try {
      const config = await getPreset(sessionId, key);
      loadConfig(config);
    } catch {
      // ignore
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <h3 className="font-semibold text-white text-sm">Room Presets</h3>
      <div className="grid grid-cols-2 gap-2">
        {PRESETS.map((p) => (
          <button
            key={p.key}
            onClick={() => load(p.key)}
            className="flex flex-col items-center gap-0.5 rounded-lg p-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-accent/50 transition-all text-xs"
          >
            <span className="text-lg">{p.icon}</span>
            <span className="text-white font-medium">{p.label}</span>
            <span className="text-muted">{p.desc}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
