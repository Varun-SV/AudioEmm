import { create } from "zustand";
import type { RoomConfig, SurfaceName, MaterialName, Speaker, Listener } from "../types/room";

interface RoomState extends RoomConfig {
  selectedSurface: SurfaceName | null;
  setSelectedSurface: (s: SurfaceName | null) => void;
  setDimensions: (length: number, width: number, height: number) => void;
  setSurfaceMaterial: (surface: SurfaceName, material: MaterialName) => void;
  setSpeakers: (speakers: Speaker[]) => void;
  setListener: (listener: Listener) => void;
  loadConfig: (config: RoomConfig) => void;
  rt60_preview: number | null;
  setRt60Preview: (v: number | null) => void;
}

const DEFAULT_SURFACES = [
  { surface: "floor"      as SurfaceName, material: "hardwood" as MaterialName },
  { surface: "ceiling"    as SurfaceName, material: "drywall"  as MaterialName },
  { surface: "wall_front" as SurfaceName, material: "drywall"  as MaterialName },
  { surface: "wall_back"  as SurfaceName, material: "drywall"  as MaterialName },
  { surface: "wall_left"  as SurfaceName, material: "drywall"  as MaterialName },
  { surface: "wall_right" as SurfaceName, material: "drywall"  as MaterialName },
];

export const useRoomStore = create<RoomState>((set, get) => ({
  length: 5,
  width: 4,
  height: 3,
  surfaces: DEFAULT_SURFACES,
  speakers: [
    { id: "sp1", x: 1.0, y: 2.0, z: 1.0, label: "Speaker L" },
    { id: "sp2", x: 4.0, y: 2.0, z: 1.0, label: "Speaker R" },
  ],
  listener: { x: 2.5, y: 1.0, z: 1.2 },
  rt60_preview: null,
  selectedSurface: null,

  setSelectedSurface: (s) => set({ selectedSurface: s }),

  setDimensions: (length, width, height) => set({ length, width, height }),

  setSurfaceMaterial: (surface, material) =>
    set((state) => ({
      surfaces: state.surfaces.map((s) =>
        s.surface === surface ? { ...s, material } : s,
      ),
    })),

  setSpeakers: (speakers) => set({ speakers }),

  setListener: (listener) => set({ listener }),

  loadConfig: (config) =>
    set({
      length: config.length,
      width: config.width,
      height: config.height,
      surfaces: config.surfaces.length ? config.surfaces : DEFAULT_SURFACES,
      speakers: config.speakers,
      listener: config.listener,
      rt60_preview: config.rt60_preview ?? null,
    }),

  setRt60Preview: (v) => set({ rt60_preview: v }),
}));
