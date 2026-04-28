import { useState, useRef } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, GizmoHelper, GizmoViewport, Grid } from "@react-three/drei";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import { RoomBox } from "./RoomBox";
import { SpeakerObject } from "./SpeakerObject";
import { ListenerObject } from "./ListenerObject";
import { useRoomStore } from "../../store/roomStore";

export function RoomScene() {
  const { speakers, length: L, width: W, height: H } = useRoomStore();
  const orbitRef = useRef<OrbitControlsImpl>(null);
  const [orbitEnabled, setOrbitEnabled] = useState(true);

  return (
    <Canvas
      camera={{ position: [L / 2 + 5, H + 3, W / 2 + 5], fov: 50 }}
      style={{ background: "#0f0f1a" }}
    >
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 10]} intensity={1} castShadow />
      <pointLight position={[L / 2, H - 0.2, W / 2]} intensity={0.3} />

      <RoomBox />

      {speakers.map((sp) => (
        <SpeakerObject
          key={sp.id}
          speaker={sp}
          onDragStart={() => setOrbitEnabled(false)}
          onDragEnd={() => setOrbitEnabled(true)}
        />
      ))}

      <ListenerObject
        onDragStart={() => setOrbitEnabled(false)}
        onDragEnd={() => setOrbitEnabled(true)}
      />

      <Grid
        position={[L / 2, 0.01, W / 2]}
        args={[Math.max(L, W) * 2, Math.max(L, W) * 2]}
        cellSize={1}
        cellColor="#334"
        sectionColor="#446"
        fadeDistance={30}
        infiniteGrid
      />

      <OrbitControls
        ref={orbitRef}
        enabled={orbitEnabled}
        target={[L / 2, H / 2, W / 2]}
        maxPolarAngle={Math.PI * 0.85}
      />

      <GizmoHelper alignment="bottom-right" margin={[60, 60]}>
        <GizmoViewport
          axisColors={["#e94560", "#4caf50", "#2196f3"]}
          labelColor="white"
        />
      </GizmoHelper>
    </Canvas>
  );
}
