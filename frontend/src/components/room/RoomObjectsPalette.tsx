import type { RoomObjectType } from "../../types/room";
import { ROOM_OBJECT_LABELS, ROOM_OBJECT_WALL_TYPES, ROOM_OBJECT_FLOOR_TYPES } from "../../types/room";

const ICONS: Record<RoomObjectType, string> = {
  curtain:   "🪟",
  window:    "🔲",
  door:      "🚪",
  sofa:      "🛋",
  bookshelf: "📚",
  desk:      "🖥",
};

const WALL_ITEMS = ROOM_OBJECT_WALL_TYPES;
const FLOOR_ITEMS = ROOM_OBJECT_FLOOR_TYPES;

interface TileProps {
  type: RoomObjectType;
}

function ObjectTile({ type }: TileProps) {
  return (
    <div
      draggable
      onDragStart={(e) => {
        e.dataTransfer.setData("roomObjectType", type);
        e.dataTransfer.effectAllowed = "copy";
      }}
      className="flex items-center gap-2 px-3 py-2 rounded cursor-grab
                 bg-white/5 hover:bg-white/10 border border-white/10
                 hover:border-white/30 select-none transition-colors"
      title={`Drag to place ${ROOM_OBJECT_LABELS[type]}`}
    >
      <span className="text-lg leading-none">{ICONS[type]}</span>
      <span className="text-xs text-gray-300">{ROOM_OBJECT_LABELS[type]}</span>
    </div>
  );
}

export function RoomObjectsPalette() {
  return (
    <div className="flex flex-col gap-1">
      <p className="text-xs text-gray-500 font-medium uppercase tracking-wider mb-1">
        Wall objects
      </p>
      {WALL_ITEMS.map((t) => (
        <ObjectTile key={t} type={t} />
      ))}
      <p className="text-xs text-gray-500 font-medium uppercase tracking-wider mt-3 mb-1">
        Floor objects
      </p>
      {FLOOR_ITEMS.map((t) => (
        <ObjectTile key={t} type={t} />
      ))}
    </div>
  );
}
