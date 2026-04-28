export type MaterialName =
  | "drywall" | "hardwood" | "carpet" | "curtain" | "concrete" | "glass";

export type SurfaceName =
  | "floor" | "ceiling" | "wall_front" | "wall_back" | "wall_left" | "wall_right";

export interface SurfaceMaterial {
  surface: SurfaceName;
  material: MaterialName;
}

export interface Speaker {
  id: string;
  x: number;
  y: number;
  z: number;
  label: string;
}

export interface Listener {
  x: number;
  y: number;
  z: number;
}

export interface RoomConfig {
  length: number;
  width: number;
  height: number;
  surfaces: SurfaceMaterial[];
  speakers: Speaker[];
  listener: Listener;
  rt60_preview?: number | null;
  room_objects?: RoomObject[];
}

export const MATERIAL_COLORS: Record<MaterialName, string> = {
  drywall:  "#c0c0c0",
  hardwood: "#8b5e3c",
  carpet:   "#b04040",
  curtain:  "#7b3f9e",
  concrete: "#707070",
  glass:    "#a0d8ef",
};

export const MATERIAL_LABELS: Record<MaterialName, string> = {
  drywall:  "Drywall",
  hardwood: "Hardwood",
  carpet:   "Carpet",
  curtain:  "Curtain",
  concrete: "Concrete",
  glass:    "Glass",
};

export const ALL_SURFACES: SurfaceName[] = [
  "floor", "ceiling", "wall_front", "wall_back", "wall_left", "wall_right",
];

export const SURFACE_LABELS: Record<SurfaceName, string> = {
  floor:      "Floor",
  ceiling:    "Ceiling",
  wall_front: "Wall (Front)",
  wall_back:  "Wall (Back)",
  wall_left:  "Wall (Left)",
  wall_right: "Wall (Right)",
};

export type RoomObjectType =
  | "curtain" | "window" | "door" | "sofa" | "bookshelf" | "desk";

export interface RoomObject {
  id: string;
  type: RoomObjectType;
  wallSurface: SurfaceName;
  posU: number;
  posV: number;
  width: number;
  height: number;
}

export const ROOM_OBJECT_LABELS: Record<RoomObjectType, string> = {
  curtain:   "Curtain",
  window:    "Window",
  door:      "Door",
  sofa:      "Sofa",
  bookshelf: "Bookshelf",
  desk:      "Desk",
};

export const ROOM_OBJECT_WALL_TYPES: RoomObjectType[] = ["curtain", "window", "door"];
export const ROOM_OBJECT_FLOOR_TYPES: RoomObjectType[] = ["sofa", "bookshelf", "desk"];

export const ROOM_OBJECT_DEFAULTS: Record<RoomObjectType, { width: number; height: number }> = {
  curtain:   { width: 1.5, height: 2.0 },
  window:    { width: 1.2, height: 1.0 },
  door:      { width: 0.9, height: 2.1 },
  sofa:      { width: 2.0, height: 0.9 },
  bookshelf: { width: 1.0, height: 1.8 },
  desk:      { width: 1.4, height: 0.75 },
};
