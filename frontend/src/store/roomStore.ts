import { create } from "zustand";
import type { RoomConfig, SurfaceName, MaterialName, Speaker, Listener, RoomObject, ModelObject } from "../types/room";

interface RoomState extends RoomConfig {
  selectedSurface: SurfaceName | null;
  roomObjects: RoomObject[];
  modelObjects: ModelObject[];
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
  addModelObject: (obj: ModelObject) => void;
  removeModelObject: (id: string) => void;
  updateModelObject: (id: string, patch: Partial<ModelObject>) => void;
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
  modelObjects: [],

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
    const rawModelObjects = (config as any).model_objects ?? config.model_objects ?? [];
    const modelObjects: ModelObject[] = rawModelObjects.map((o: any) => ({
      id: o.id,
      modelId: o.modelId ?? o.model_id,
      filename: o.filename,
      url: o.url ?? "",
      material: o.material ?? "drywall",
      wallSurface: o.wallSurface ?? o.wall_surface ?? "floor",
      position: o.position ?? [0, 0, 0],
      rotation: o.rotation ?? [0, 0, 0],
      scale: o.scale ?? [1, 1, 1],
      bboxW: o.bboxW ?? o.bbox_w ?? 1.0,
      bboxH: o.bboxH ?? o.bbox_h ?? 1.0,
      bboxD: o.bboxD ?? o.bbox_d ?? 1.0,
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
      modelObjects,
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

  addModelObject: (obj) =>
    set((state) => ({ modelObjects: [...state.modelObjects, obj] })),

  removeModelObject: (id) =>
    set((state) => ({ modelObjects: state.modelObjects.filter((o) => o.id !== id) })),

  updateModelObject: (id, patch) =>
    set((state) => ({
      modelObjects: state.modelObjects.map((o) => o.id === id ? { ...o, ...patch } : o),
    })),
}));
