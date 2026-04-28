import { create } from "zustand";
import type { RoomConfig, SurfaceName, MaterialName, Speaker, Listener, RoomObject } from "../types/room";

interface RoomState extends RoomConfig {
  selectedSurface: SurfaceName | null;
  roomObjects: RoomObject[];
  setSelectedSurface: (s: SurfaceName | null) => void;
  setDimensions: (length: number, width: number, height: number) => void;
  setSurfaceMaterial: (surface: SurfaceName, material: MaterialName) => void;
  setSpeakers: (speakers: Speaker[]) => void;
  setListener: (listener: Listener) => void;
  loadConfig: (config: RoomConfig) => void;
  rt60_preview: number | null;
  setRt60Preview: (v: number | null) => void;
  addRoomObject: (obj: RoomObject) => void;
  removeRoomObject: (id: string) => void;
  updateRoomObject: (id: string, patch: Partial<RoomObject>) => void;
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
  roomObjects: [],

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

  loadConfig: (config) => {
    const rawObjects = (config as any).room_objects ?? config.room_objects ?? [];
    const roomObjects = rawObjects.map((o: any) => ({
      id: o.id,
      type: o.type,
      wallSurface: o.wallSurface ?? o.wall_surface,
      posU: o.posU ?? o.pos_u ?? 0.5,
      posV: o.posV ?? o.pos_v ?? 0.5,
      width: o.width ?? 1.0,
      height: o.height ?? 1.5,
    }));
    set({
      length: config.length,
      width: config.width,
      height: config.height,
      surfaces: config.surfaces.length ? config.surfaces : DEFAULT_SURFACES,
      speakers: config.speakers,
      listener: config.listener,
      rt60_preview: config.rt60_preview ?? null,
      roomObjects,
    });
  },

  setRt60Preview: (v) => set({ rt60_preview: v }),

  addRoomObject: (obj) =>
    set((state) => ({ roomObjects: [...state.roomObjects, obj] })),

  removeRoomObject: (id) =>
    set((state) => ({ roomObjects: state.roomObjects.filter((o) => o.id !== id) })),

  updateRoomObject: (id, patch) =>
    set((state) => ({
      roomObjects: state.roomObjects.map((o) => o.id === id ? { ...o, ...patch } : o),
    })),
}));
