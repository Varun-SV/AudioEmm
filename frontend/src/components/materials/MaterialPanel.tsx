import { useRoomStore } from "../../store/roomStore";
import { ALL_SURFACES, SURFACE_LABELS, MATERIAL_COLORS, MATERIAL_LABELS } from "../../types/room";
import type { MaterialName, SurfaceName } from "../../types/room";

const MATERIALS: MaterialName[] = ["drywall", "hardwood", "carpet", "curtain", "concrete", "glass"];

export function MaterialPanel() {
  const { surfaces, selectedSurface, setSelectedSurface, setSurfaceMaterial } = useRoomStore();

  const matFor = (s: SurfaceName) =>
    surfaces.find((x) => x.surface === s)?.material ?? "drywall";

  return (
    <div className="flex flex-col gap-3 text-sm">
      <h3 className="font-semibold text-white text-base">Surfaces</h3>
      <p className="text-muted text-xs">Click a surface in the 3D view or select below</p>

      {ALL_SURFACES.map((surface) => (
        <div
          key={surface}
          onClick={() => setSelectedSurface(selectedSurface === surface ? null : surface)}
          className={`rounded-lg p-2 cursor-pointer border transition-colors ${
            selectedSurface === surface
              ? "border-accent bg-accent/10"
              : "border-white/10 bg-white/5 hover:bg-white/10"
          }`}
        >
          <div className="flex items-center justify-between mb-1">
            <span className="text-white font-medium">{SURFACE_LABELS[surface]}</span>
            <span
              className="text-xs px-2 py-0.5 rounded-full font-semibold"
              style={{
                background: MATERIAL_COLORS[matFor(surface)] + "40",
                color: MATERIAL_COLORS[matFor(surface)],
                border: `1px solid ${MATERIAL_COLORS[matFor(surface)]}80`,
              }}
            >
              {MATERIAL_LABELS[matFor(surface)]}
            </span>
          </div>

          {selectedSurface === surface && (
            <div className="grid grid-cols-3 gap-1 mt-2">
              {MATERIALS.map((mat) => (
                <button
                  key={mat}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSurfaceMaterial(surface, mat);
                  }}
                  className={`text-xs rounded px-1 py-1 transition-all ${
                    matFor(surface) === mat
                      ? "ring-2 ring-white font-bold"
                      : "opacity-60 hover:opacity-100"
                  }`}
                  style={{ background: MATERIAL_COLORS[mat] + "60", color: "#fff" }}
                >
                  {MATERIAL_LABELS[mat]}
                </button>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
