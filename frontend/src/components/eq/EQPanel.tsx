import { useEffect, useRef, useState } from "react";
import { uploadEQProfile, listEQProfiles, deleteEQProfile } from "../../api/eq";
import { useSessionStore } from "../../store/sessionStore";
import { useAudioStore } from "../../store/audioStore";
import type { EQProfile } from "../../types/eq";

export function EQPanel() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const { activeEqProfileId, setActiveEqProfile } = useAudioStore();
  const [profiles, setProfiles] = useState<{ profile_id: string; name: string }[]>([]);
  const [uploading, setUploading] = useState(false);
  const [profileName, setProfileName] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!sessionId) return;
    listEQProfiles(sessionId).then(setProfiles).catch(() => {});
  }, [sessionId]);

  async function handleUpload(file: File) {
    if (!sessionId || !profileName.trim()) return;
    setUploading(true);
    try {
      const p = await uploadEQProfile(sessionId, file, profileName.trim());
      setProfiles((prev) => [...prev, { profile_id: p.profile_id, name: p.name }]);
      setProfileName("");
    } catch {
      // ignore
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(profileId: string) {
    if (!sessionId) return;
    await deleteEQProfile(sessionId, profileId).catch(() => {});
    setProfiles((prev) => prev.filter((p) => p.profile_id !== profileId));
    if (activeEqProfileId === profileId) setActiveEqProfile(null);
  }

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h3 className="font-semibold text-white text-base mb-1">Headphone / Speaker FR</h3>
        <p className="text-muted text-xs">
          Upload a frequency-response CSV (frequency_hz, db columns) to model how a
          specific headphone or speaker will colour the binaural mix.
        </p>
      </div>

      {/* Upload */}
      <div className="flex flex-col gap-2">
        <input
          value={profileName}
          onChange={(e) => setProfileName(e.target.value)}
          placeholder="Profile name (e.g. Sony WH-1000XM5)"
          className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-muted focus:outline-none focus:border-accent"
        />
        <button
          onClick={() => profileName.trim() && inputRef.current?.click()}
          disabled={uploading || !profileName.trim()}
          className="py-2 rounded-lg text-sm font-semibold bg-white/10 hover:bg-white/20 text-white disabled:opacity-40 transition-all"
        >
          {uploading ? "Uploading…" : "Upload FR File"}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.txt"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
        />
      </div>

      {/* Profile list */}
      {profiles.length > 0 && (
        <div className="flex flex-col gap-2">
          <h4 className="text-muted text-xs font-semibold uppercase tracking-wide">
            Active EQ Profile
          </h4>

          <button
            onClick={() => setActiveEqProfile(null)}
            className={`text-sm rounded-lg px-3 py-2 text-left transition-colors ${
              !activeEqProfileId
                ? "bg-accent text-white font-semibold"
                : "bg-white/5 text-muted hover:bg-white/10"
            }`}
          >
            No EQ (room + HRTF only)
          </button>

          {profiles.map((p) => (
            <div key={p.profile_id} className="flex items-center gap-2">
              <button
                onClick={() =>
                  setActiveEqProfile(
                    activeEqProfileId === p.profile_id ? null : p.profile_id,
                  )
                }
                className={`flex-1 text-sm rounded-lg px-3 py-2 text-left transition-colors ${
                  activeEqProfileId === p.profile_id
                    ? "bg-accent text-white font-semibold"
                    : "bg-white/5 text-muted hover:bg-white/10"
                }`}
              >
                {p.name}
              </button>
              <button
                onClick={() => handleDelete(p.profile_id)}
                className="text-red-400 hover:text-red-300 text-xs px-2"
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
