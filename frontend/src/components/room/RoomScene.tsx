import { useState, useRef, useCallback } from "react";
import { Canvas, useThree } from "@react-three/fiber";
import { OrbitControls, GizmoHelper, GizmoViewport, Grid } from "@react-three/drei";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import * as THREE from "three";
import { RoomBox } from "./RoomBox";
import { SpeakerObject } from "./SpeakerObject";
import { ListenerObject } from "./ListenerObject";
import { RoomObjectsLayer } from "./RoomObjectMesh";
import { ImportedModelLayer } from "./ImportedModelLayer";
import { useRoomStore } from "../../store/roomStore";
import type { RoomObjectType, SurfaceName } from "../../types/room";
import { ROOM_OBJECT_DEFAULTS, SUPPORTED_MODEL_EXTENSIONS } from "../../types/room";
import { uploadModel } from "../../api/models";
import { useSessionStore } from "../../store/sessionStore";
import type { ModelObject } from "../../types/room";

// Wall planes for drop hit-testing (defined in room space)
function buildWallPlanes(L: number, W: number, H: number) {
  return [
    { name: "wall_front" as SurfaceName, plane: new THREE.Plane(new THREE.Vector3(0, 0, 1),  0) },
    { name: "wall_back"  as SurfaceName, plane: new THREE.Plane(new THREE.Vector3(0, 0, -1), -W) },
    { name: "wall_left"  as SurfaceName, plane: new THREE.Plane(new THREE.Vector3(1, 0, 0),  0) },
    { name: "wall_right" as SurfaceName, plane: new THREE.Plane(new THREE.Vector3(-1, 0, 0), -L) },
    { name: "floor"      as SurfaceName, plane: new THREE.Plane(new THREE.Vector3(0, 1, 0),  0) },
    { name: "ceiling"    as SurfaceName, plane: new THREE.Plane(new THREE.Vector3(0, -1, 0), -H) },
  ];
}

interface DropHandlerProps {
  onDrop: (type: RoomObjectType, wallSurface: SurfaceName, posU: number, posV: number) => void;
}

function DropHandler({ onDrop }: DropHandlerProps) {
  const { camera, raycaster } = useThree();
  const { length: L, width: W, height: H } = useRoomStore();

  // Exposed via ref so the outer Canvas element can call it
  (DropHandler as any)._handler = useCallback(
    (e: DragEvent, canvasRect: DOMRect) => {
      const type = e.dataTransfer?.getData("roomObjectType") as RoomObjectType | undefined;
      if (!type) return;

      const ndcX = ((e.clientX - canvasRect.left) / canvasRect.width) * 2 - 1;
      const ndcY = -((e.clientY - canvasRect.top) / canvasRect.height) * 2 + 1;
      raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera);

      const walls = buildWallPlanes(L, W, H);
      const hit = new THREE.Vector3();
      let bestDist = Infinity;
      let bestWall: SurfaceName = "wall_front";
      let bestHit = new THREE.Vector3();

      for (const { name, plane } of walls) {
        if (raycaster.ray.intersectPlane(plane, hit)) {
          const dist = raycaster.ray.origin.distanceTo(hit);
          if (dist < bestDist) {
            bestDist = dist;
            bestWall = name;
            bestHit.copy(hit);
          }
        }
      }

      // Convert hit point to posU/posV (0-1) for the identified surface
      let posU = 0.5;
      let posV = 0.5;
      switch (bestWall) {
        case "wall_front": case "wall_back":
          posU = Math.max(0, Math.min(1, bestHit.x / L));
          posV = Math.max(0, Math.min(1, bestHit.y / H));
          break;
        case "wall_left": case "wall_right":
          posU = Math.max(0, Math.min(1, bestHit.z / W));
          posV = Math.max(0, Math.min(1, bestHit.y / H));
          break;
        case "floor": case "ceiling":
          posU = Math.max(0, Math.min(1, bestHit.x / L));
          posV = Math.max(0, Math.min(1, bestHit.z / W));
          break;
      }

      onDrop(type, bestWall, posU, posV);
    },
    [camera, raycaster, L, W, H, onDrop],
  );

  return null;
}

export function RoomScene() {
  const { speakers, length: L, width: W, height: H, addRoomObject, addModelObject } = useRoomStore();
  const sessionId = useSessionStore((s) => s.sessionId);
  const orbitRef = useRef<OrbitControlsImpl>(null);
  const [orbitEnabled, setOrbitEnabled] = useState(true);
  const canvasRef = useRef<HTMLDivElement>(null);

  const handleDrop = useCallback(
    (type: RoomObjectType, wallSurface: SurfaceName, posU: number, posV: number) => {
      const defaults = ROOM_OBJECT_DEFAULTS[type];
      addRoomObject({
        id: crypto.randomUUID(),
        type,
        wallSurface,
        posU,
        posV,
        width: defaults.width,
        height: defaults.height,
      });
    },
    [addRoomObject],
  );

  const handleModelFileDrop = useCallback(
    async (files: FileList) => {
      if (!sessionId) return;
      for (const file of Array.from(files)) {
        const ext = "." + (file.name.split(".").pop()?.toLowerCase() ?? "");
        if (!SUPPORTED_MODEL_EXTENSIONS.includes(ext)) continue;
        try {
          const resp = await uploadModel(sessionId, file);
          const obj: ModelObject = {
            id: crypto.randomUUID(),
            modelId: resp.model_id,
            filename: resp.filename,
            url: resp.url,
            material: "drywall",
            wallSurface: "floor",
            position: [L / 2, 0, W / 2],
            rotation: [0, 0, 0],
            scale: [1, 1, 1],
            bboxW: 1, bboxH: 1, bboxD: 1,
          };
          addModelObject(obj);
        } catch {
          // silent — user can retry via sidebar panel
        }
      }
    },
    [sessionId, addModelObject, L, W],
  );

  const handleCanvasDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      // 3D file drop takes priority over room-object tile drop
      if (e.dataTransfer.files.length > 0) {
        handleModelFileDrop(e.dataTransfer.files);
        return;
      }
      const rect = (e.currentTarget as HTMLDivElement).getBoundingClientRect();
      const handler = (DropHandler as any)._handler;
      if (handler) handler(e.nativeEvent, rect);
    },
    [handleModelFileDrop],
  );

  return (
    <div
      ref={canvasRef}
      style={{ width: "100%", height: "100%" }}
      onDrop={handleCanvasDrop}
      onDragOver={(e) => e.preventDefault()}
    >
      <Canvas
        camera={{ position: [L / 2 + 5, H + 3, W / 2 + 5], fov: 50 }}
        style={{ background: "#0f0f1a" }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 10]} intensity={1} castShadow />
        <pointLight position={[L / 2, H - 0.2, W / 2]} intensity={0.3} />

        <RoomBox />
        <RoomObjectsLayer />
        <ImportedModelLayer
          onDragStart={() => setOrbitEnabled(false)}
          onDragEnd={() => setOrbitEnabled(true)}
        />

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

        <DropHandler onDrop={handleDrop} />
      </Canvas>
    </div>
  );
}
