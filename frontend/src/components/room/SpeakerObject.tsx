import { useRef, useState, useCallback } from "react";
import { useThree, ThreeEvent } from "@react-three/fiber";
import { Plane, Html } from "@react-three/drei";
import * as THREE from "three";
import type { Mesh } from "three";
import { useRoomStore } from "../../store/roomStore";
import type { Speaker } from "../../types/room";

interface Props {
  speaker: Speaker;
  onDragStart: () => void;
  onDragEnd: () => void;
}

export function SpeakerObject({ speaker, onDragStart, onDragEnd }: Props) {
  const ref = useRef<Mesh>(null);
  const [dragging, setDragging] = useState(false);
  const [hovered, setHovered] = useState(false);
  const { camera, gl, raycaster } = useThree();
  const { setSpeakers, speakers, length, width, height } = useRoomStore();

  const dragPlane = useRef(new THREE.Plane(new THREE.Vector3(0, 1, 0), -speaker.y));
  const intersection = useRef(new THREE.Vector3());

  const handlePointerDown = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      e.stopPropagation();
      (e.target as HTMLElement).setPointerCapture(e.pointerId);
      setDragging(true);
      onDragStart();
      dragPlane.current.set(new THREE.Vector3(0, 1, 0), -speaker.y);
    },
    [speaker.y, onDragStart],
  );

  const handlePointerMove = useCallback(
    (e: ThreeEvent<PointerEvent>) => {
      if (!dragging) return;
      raycaster.ray.intersectPlane(dragPlane.current, intersection.current);
      const newX = Math.max(0, Math.min(intersection.current.x, length));
      const newZ = Math.max(0, Math.min(intersection.current.z, width));
      setSpeakers(
        speakers.map((s) =>
          s.id === speaker.id ? { ...s, x: newX, y: speaker.y, z: newZ } : s,
        ),
      );
    },
    [dragging, raycaster, speaker, speakers, setSpeakers, length, width],
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
      position={[speaker.x, speaker.z, speaker.y]}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <coneGeometry args={[0.15, 0.3, 8]} />
      <meshStandardMaterial color={hovered || dragging ? "#ff6666" : "#e94560"} />
      {(hovered || dragging) && (
        <Html distanceFactor={5} center style={{ pointerEvents: "none" }}>
          <div className="bg-black/70 text-white text-xs px-1 rounded whitespace-nowrap">
            {speaker.label} ({speaker.x.toFixed(1)}, {speaker.z.toFixed(1)})
          </div>
        </Html>
      )}
    </mesh>
  );
}
