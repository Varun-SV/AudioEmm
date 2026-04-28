import { useRef, useState } from "react";
import { ThreeEvent } from "@react-three/fiber";
import type { Mesh } from "three";
import type { SurfaceName } from "../../types/room";
import { MATERIAL_COLORS } from "../../types/room";
import { useRoomStore } from "../../store/roomStore";

interface Props {
  name: SurfaceName;
  position: [number, number, number];
  rotation: [number, number, number];
  size: [number, number, number];
}

export function WallSurface({ name, position, rotation, size }: Props) {
  const ref = useRef<Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const { surfaces, selectedSurface, setSelectedSurface } = useRoomStore();

  const surfaceCfg = surfaces.find((s) => s.surface === name);
  const mat = surfaceCfg?.material ?? "drywall";
  const color = MATERIAL_COLORS[mat];
  const isSelected = selectedSurface === name;

  function onClick(e: ThreeEvent<MouseEvent>) {
    e.stopPropagation();
    setSelectedSurface(isSelected ? null : name);
  }

  return (
    <mesh
      ref={ref}
      position={position}
      rotation={rotation}
      onClick={onClick}
      onPointerOver={(e) => { e.stopPropagation(); setHovered(true); }}
      onPointerOut={() => setHovered(false)}
    >
      <boxGeometry args={size} />
      <meshStandardMaterial
        color={hovered ? "#ffffff" : color}
        opacity={isSelected ? 1.0 : 0.75}
        transparent={!isSelected}
        wireframe={false}
      />
    </mesh>
  );
}
