import { useState } from "react";
import { Html } from "@react-three/drei";
import type { RoomObject, RoomObjectType } from "../../types/room";
import { ROOM_OBJECT_LABELS } from "../../types/room";
import { useRoomStore } from "../../store/roomStore";

const OBJECT_COLOR: Record<RoomObjectType, string> = {
  curtain:   "#7b3f9e",
  window:    "#a0d8ef",
  door:      "#8b5e3c",
  sofa:      "#6b4e3d",
  bookshelf: "#5c4a2a",
  desk:      "#4a5568",
};

const OBJECT_OPACITY: Record<RoomObjectType, number> = {
  curtain:   0.85,
  window:    0.45,
  door:      1.0,
  sofa:      1.0,
  bookshelf: 1.0,
  desk:      1.0,
};

interface Props {
  obj: RoomObject;
}

function RoomObjectMesh({ obj }: Props) {
  const [hovered, setHovered] = useState(false);
  const { removeRoomObject, length: L, width: W, height: H } = useRoomStore();

  const isFloor = obj.wallSurface === "floor";
  const isFloorType = ["sofa", "bookshelf", "desk"].includes(obj.type);

  // Compute 3D position and euler rotation from wall surface + posU/posV
  let position: [number, number, number];
  let rotation: [number, number, number];
  const OFFSET = 0.05; // distance from wall face

  switch (obj.wallSurface) {
    case "wall_front":
      position = [obj.posU * L, obj.posV * H, OFFSET];
      rotation = [0, 0, 0];
      break;
    case "wall_back":
      position = [obj.posU * L, obj.posV * H, W - OFFSET];
      rotation = [0, Math.PI, 0];
      break;
    case "wall_left":
      position = [OFFSET, obj.posV * H, obj.posU * W];
      rotation = [0, -Math.PI / 2, 0];
      break;
    case "wall_right":
      position = [L - OFFSET, obj.posV * H, obj.posU * W];
      rotation = [0, Math.PI / 2, 0];
      break;
    case "ceiling":
      position = [obj.posU * L, H - OFFSET, obj.posV * W];
      rotation = [Math.PI / 2, 0, 0];
      break;
    case "floor":
    default:
      // Floor objects sit on the ground; posV is used as Z depth axis
      position = [obj.posU * L, isFloorType ? obj.height / 2 : OFFSET, obj.posV * W];
      rotation = [0, 0, 0];
      break;
  }

  const color = OBJECT_COLOR[obj.type];
  const opacity = OBJECT_OPACITY[obj.type];
  const transparent = opacity < 1;

  // Geometry dimensions depend on type and surface
  let geoW = obj.width;
  let geoH = isFloor && isFloorType ? obj.height : obj.height; // depth for floor furniture
  let geoD = isFloor && isFloorType ? obj.width : 0.06;

  // Floor furniture: box lying flat — swap axes
  if (isFloor && isFloorType) {
    geoW = obj.width;
    geoH = obj.height; // actual height of furniture
    geoD = obj.width * 0.6; // depth (front-to-back)
  }

  return (
    <mesh
      position={position}
      rotation={rotation}
      onClick={(e) => {
        e.stopPropagation();
        if (window.confirm(`Remove ${ROOM_OBJECT_LABELS[obj.type]}?`)) {
          removeRoomObject(obj.id);
        }
      }}
      onPointerOver={(e) => { e.stopPropagation(); setHovered(true); }}
      onPointerOut={() => setHovered(false)}
    >
      <boxGeometry args={[geoW, geoH, isFloor && isFloorType ? geoD : 0.06]} />
      <meshStandardMaterial
        color={hovered ? "#ffffff" : color}
        opacity={opacity}
        transparent={transparent}
      />
      {hovered && (
        <Html distanceFactor={5} center style={{ pointerEvents: "none" }}>
          <div className="bg-black/80 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
            {ROOM_OBJECT_LABELS[obj.type]} — click to remove
          </div>
        </Html>
      )}
    </mesh>
  );
}

export function RoomObjectsLayer() {
  const { roomObjects } = useRoomStore();
  return (
    <>
      {roomObjects.map((obj) => (
        <RoomObjectMesh key={obj.id} obj={obj} />
      ))}
    </>
  );
}
