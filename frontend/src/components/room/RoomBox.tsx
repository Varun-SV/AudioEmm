import { WallSurface } from "./WallSurface";
import { useRoomStore } from "../../store/roomStore";

const THICKNESS = 0.05;

export function RoomBox() {
  const { length: L, width: W, height: H } = useRoomStore();

  return (
    <group>
      {/* Floor */}
      <WallSurface
        name="floor"
        position={[L / 2, 0, W / 2]}
        rotation={[0, 0, 0]}
        size={[L, THICKNESS, W]}
      />
      {/* Ceiling */}
      <WallSurface
        name="ceiling"
        position={[L / 2, H, W / 2]}
        rotation={[0, 0, 0]}
        size={[L, THICKNESS, W]}
      />
      {/* Wall Front (z = 0) */}
      <WallSurface
        name="wall_front"
        position={[L / 2, H / 2, 0]}
        rotation={[0, 0, 0]}
        size={[L, H, THICKNESS]}
      />
      {/* Wall Back (z = W) */}
      <WallSurface
        name="wall_back"
        position={[L / 2, H / 2, W]}
        rotation={[0, 0, 0]}
        size={[L, H, THICKNESS]}
      />
      {/* Wall Left (x = 0) */}
      <WallSurface
        name="wall_left"
        position={[0, H / 2, W / 2]}
        rotation={[0, 0, 0]}
        size={[THICKNESS, H, W]}
      />
      {/* Wall Right (x = L) */}
      <WallSurface
        name="wall_right"
        position={[L, H / 2, W / 2]}
        rotation={[0, 0, 0]}
        size={[THICKNESS, H, W]}
      />
    </group>
  );
}
