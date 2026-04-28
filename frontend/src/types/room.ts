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
