import { Suspense, useRef, useState, useCallback, useEffect } from "react";
import { useLoader, useThree } from "@react-three/fiber";
import { useGLTF, TransformControls, Html } from "@react-three/drei";
import * as THREE from "three";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader.js";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
import { FBXLoader } from "three/examples/jsm/loaders/FBXLoader.js";
import { useRoomStore } from "../../store/roomStore";
import type { ModelObject } from "../../types/room";
import { MATERIAL_LABELS } from "../../types/room";
import type { MaterialName } from "../../types/room";

// ── per-format loader components (hooks must be unconditional per component) ──

function GltfContent({ url }: { url: string }) {
  const { scene } = useGLTF(url);
  return <primitive object={scene.clone()} />;
}

function ObjContent({ url }: { url: string }) {
  const obj = useLoader(OBJLoader, url);
  return <primitive object={obj.clone()} />;
}

function StlContent({ url }: { url: string }) {
  const geo = useLoader(STLLoader, url);
  return (
    <mesh geometry={geo}>
      <meshStandardMaterial color="#aaaaaa" />
    </mesh>
  );
}

function FbxContent({ url }: { url: string }) {
  const fbx = useLoader(FBXLoader, url);
  return <primitive object={fbx.clone()} />;
}

function FallbackBox() {
  return (
    <mesh>
      <boxGeometry args={[0.5, 0.5, 0.5]} />
      <meshStandardMaterial color="#666" wireframe />
    </mesh>
  );
}

function ModelContent({ url }: { url: string }) {
  const ext = url.split("?")[0].split(".").pop()?.toLowerCase() ?? "";
  if (ext === "glb" || ext === "gltf") return <GltfContent url={url} />;
  if (ext === "obj") return <ObjContent url={url} />;
  if (ext === "stl") return <StlContent url={url} />;
  if (ext === "fbx") return <FbxContent url={url} />;
  return <FallbackBox />;
}

// ── single model object item ──

interface ItemProps {
  obj: ModelObject;
  onDragStart: () => void;
  onDragEnd: () => void;
}

function ModelObjectItem({ obj, onDragStart, onDragEnd }: ItemProps) {
  const [selected, setSelected] = useState(false);
  const [mode, setMode] = useState<"translate" | "rotate" | "scale">("translate");
  const [hovered, setHovered] = useState(false);
  const groupRef = useRef<THREE.Group>(null);
  const bboxComputedRef = useRef(false);
  const { updateModelObject, removeModelObject } = useRoomStore();

  // Compute bounding box once after first render
  useEffect(() => {
    if (bboxComputedRef.current || !groupRef.current) return;
    const box = new THREE.Box3().setFromObject(groupRef.current);
    const size = new THREE.Vector3();
    box.getSize(size);
    if (size.lengthSq() > 0) {
      bboxComputedRef.current = true;
      updateModelObject(obj.id, { bboxW: size.x, bboxH: size.y, bboxD: size.z });
    }
  });

  const handleTransformEnd = useCallback(() => {
    onDragEnd();
    if (!groupRef.current) return;
    const p = groupRef.current.position;
    const r = groupRef.current.rotation;
    const s = groupRef.current.scale;
    const box = new THREE.Box3().setFromObject(groupRef.current);
    const size = new THREE.Vector3();
    box.getSize(size);
    updateModelObject(obj.id, {
      position: [p.x, p.y, p.z],
      rotation: [r.x, r.y, r.z],
      scale: [s.x, s.y, s.z],
      bboxW: size.x,
      bboxH: size.y,
      bboxD: size.z,
    });
  }, [obj.id, updateModelObject, onDragEnd]);

  const handleClick = useCallback((e: any) => {
    e.stopPropagation();
    setSelected((v) => !v);
  }, []);

  const deselect = useCallback(() => setSelected(false), []);

  return (
    <>
      <TransformControls
        enabled={selected}
        mode={mode}
        onMouseDown={onDragStart}
        onMouseUp={handleTransformEnd}
      >
        <group
          ref={groupRef}
          position={obj.position}
          rotation={obj.rotation as any}
          scale={obj.scale}
          onClick={handleClick}
          onPointerOver={(e) => { e.stopPropagation(); setHovered(true); }}
          onPointerOut={() => setHovered(false)}
        >
          <Suspense fallback={<FallbackBox />}>
            <ModelContent url={obj.url} />
          </Suspense>

          {/* Selection outline */}
          {(selected || hovered) && (
            <mesh>
              <boxGeometry args={[obj.bboxW + 0.05, obj.bboxH + 0.05, obj.bboxD + 0.05]} />
              <meshBasicMaterial color={selected ? "#4488ff" : "#ffffff"} wireframe transparent opacity={0.4} />
            </mesh>
          )}
        </group>
      </TransformControls>

      {/* UI overlay when selected */}
      {selected && groupRef.current && (
        <Html
          position={[
            groupRef.current.position.x,
            groupRef.current.position.y + obj.bboxH / 2 + 0.3,
            groupRef.current.position.z,
          ]}
          center
          distanceFactor={6}
          style={{ pointerEvents: "all" }}
        >
          <div
            className="bg-black/85 border border-white/20 rounded-lg px-3 py-2 text-white text-xs flex flex-col gap-2 min-w-[160px]"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="font-semibold truncate max-w-[140px]">{obj.filename}</div>

            {/* Transform mode */}
            <div className="flex gap-1">
              {(["translate", "rotate", "scale"] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setMode(m)}
                  className={`flex-1 py-0.5 rounded text-[10px] capitalize ${
                    mode === m ? "bg-blue-600 text-white" : "bg-white/10 hover:bg-white/20"
                  }`}
                >
                  {m[0].toUpperCase()}
                </button>
              ))}
            </div>

            {/* Material picker */}
            <div>
              <div className="text-gray-400 text-[10px] mb-0.5">Acoustic material</div>
              <select
                value={obj.material}
                onChange={(e) => updateModelObject(obj.id, { material: e.target.value as MaterialName })}
                className="w-full bg-white/10 border border-white/20 rounded px-1 py-0.5 text-[11px]"
              >
                {Object.entries(MATERIAL_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
            </div>

            {/* Delete + close */}
            <div className="flex gap-1 mt-0.5">
              <button
                onClick={deselect}
                className="flex-1 py-0.5 rounded bg-white/10 hover:bg-white/20 text-[11px]"
              >
                Done
              </button>
              <button
                onClick={() => removeModelObject(obj.id)}
                className="flex-1 py-0.5 rounded bg-red-600/70 hover:bg-red-600 text-[11px]"
              >
                Delete
              </button>
            </div>
          </div>
        </Html>
      )}
    </>
  );
}

// ── layer renders all model objects ──

interface LayerProps {
  onDragStart: () => void;
  onDragEnd: () => void;
}

export function ImportedModelLayer({ onDragStart, onDragEnd }: LayerProps) {
  const { modelObjects } = useRoomStore();
  return (
    <>
      {modelObjects.map((obj) => (
        <ModelObjectItem
          key={obj.id}
          obj={obj}
          onDragStart={onDragStart}
          onDragEnd={onDragEnd}
        />
      ))}
    </>
  );
}
