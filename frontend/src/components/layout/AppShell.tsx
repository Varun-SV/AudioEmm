import { useState } from "react";
import { RoomScene } from "../room/RoomScene";
import { MaterialPanel } from "../materials/MaterialPanel";
import { RoomStats } from "../room/RoomStats";
import { PresetSelector } from "../presets/PresetSelector";
import { AudioUploader } from "../audio/AudioUploader";
import { ProcessingStatus } from "../audio/ProcessingStatus";
import { EQPanel } from "../eq/EQPanel";
import { useRoomSync } from "../../hooks/useRoomSync";
import { useSessionStore } from "../../store/sessionStore";

type Tab = "room" | "audio" | "eq";

export function AppShell() {
  const [activeTab, setActiveTab] = useState<Tab>("room");
  const sessionId = useSessionStore((s) => s.sessionId);
  useRoomSync();

  return (
    <div className="flex h-screen bg-surface text-white overflow-hidden">
      {/* Left sidebar */}
      <div className="w-72 flex-shrink-0 bg-panel border-r border-white/10 flex flex-col">
        {/* Logo */}
        <div className="px-4 pt-5 pb-3 border-b border-white/10">
          <h1 className="text-xl font-bold tracking-tight">
            Audio<span className="text-accent">Emm</span>
          </h1>
          <p className="text-muted text-xs mt-0.5">3D Room Acoustics Simulator</p>
        </div>

        {/* Tab nav */}
        <div className="flex border-b border-white/10">
          {(["room", "audio", "eq"] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 py-2.5 text-xs font-semibold capitalize transition-colors ${
                activeTab === tab
                  ? "text-accent border-b-2 border-accent"
                  : "text-muted hover:text-white"
              }`}
            >
              {tab === "eq" ? "EQ / FR" : tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Panel content */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-5">
          {activeTab === "room" && (
            <>
              <PresetSelector />
              <hr className="border-white/10" />
              <MaterialPanel />
              <hr className="border-white/10" />
              <RoomStats />
            </>
          )}
          {activeTab === "audio" && (
            <>
              <AudioUploader />
              <ProcessingStatus />
            </>
          )}
          {activeTab === "eq" && <EQPanel />}
        </div>

        {/* Status bar */}
        <div className="px-4 py-2 border-t border-white/10 text-muted text-xs flex items-center gap-1">
          <span className={`w-1.5 h-1.5 rounded-full ${sessionId ? "bg-green-400" : "bg-yellow-400"}`} />
          {sessionId ? `Session: ${sessionId.slice(0, 8)}…` : "Connecting…"}
        </div>
      </div>

      {/* Main 3D canvas */}
      <div className="flex-1 relative">
        <RoomScene />

        {/* Keyboard hint overlay */}
        <div className="absolute bottom-3 right-3 text-muted text-xs bg-black/50 rounded px-2 py-1">
          Drag speakers/listener · Orbit: left-click · Zoom: scroll
        </div>
      </div>
    </div>
  );
}
