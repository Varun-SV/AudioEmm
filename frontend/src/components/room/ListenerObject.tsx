import { useRef, useState, useCallback } from "react";
import { useThree, ThreeEvent } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import type { Mesh } from "three";
import { useRoomStore } from "../../store/roomStore";

interface Props {
  onDragStart: () => void;
  onDragEnd: () => void;
}

export function ListenerObject({ onDragStart, onDragEnd }: Props) {
  const ref = useRef<Mesh>(null);
  const [dragging, setDragging] = useState(false);
  const [hovered, setHovered] = useState(false);
  const { raycaster } = useThree();
  const { listener, setListener, length, width } = useRoomStore();

  // Three.js Y = room Z (height); Three.js Z = room Y (depth)
  const dragPlane = useRef(new THREE.Plane(new THREE.Vector3(0, 1, 0), -listener.z));
  const intersection = useRef(new THREE.Vector3());

  const handlePointerDown = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      e.stopPropagation();
      (e.target as HTMLElement).setPointerCapture(e.pointerId);
      setDragging(true);
      onDragStart();
      dragPlane.current.set(new THREE.Vector3(0, 1, 0), -listener.z);
    },
    [listener.z, onDragStart],
  );

  const handlePointerMove = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      if (!dragging) return;
      raycaster.ray.intersectPlane(dragPlane.current, intersection.current);
      const newX = Math.max(0, Math.min(intersection.current.x, length));
      const newY = Math.max(0, Math.min(intersection.current.z, width));
      setListener({ x: newX, y: newY, z: listener.z });
    },
    [dragging, raycaster, listener, setListener, length, width],
  );

  const handlePointerUp = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      (e.target as HTMLElement).releasePointerCapture(e.pointerId);
      setDragging(false);
      onDragEnd();
    },
    [onDragEnd],
  );

  return (
    <mesh
      ref={ref}
      position={[listener.x, listener.z, listener.y]}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <sphereGeometry args={[0.15, 16, 16]} />
      <meshStandardMaterial color={hovered || dragging ? "#66aaff" : "#4488ff"} />
      {(hovered || dragging) && (
        <Html distanceFactor={5} center style={{ pointerEvents: "none" }}>
          <div className="bg-black/70 text-white text-xs px-1 rounded whitespace-nowrap">
            Listener ({listener.x.toFixed(1)}, {listener.y.toFixed(1)})
          </div>
        </Html>
      )}
    </mesh>
  );
}
