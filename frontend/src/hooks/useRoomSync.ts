import { useEffect, useRef } from "react";
import { putRoom } from "../api/room";
import { useSessionStore } from "../store/sessionStore";
import { useRoomStore } from "../store/roomStore";
import type { RoomConfig } from "../types/room";

const DEBOUNCE_MS = 600;

export function useRoomSync() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const room = useRoomStore();
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (!sessionId) return;
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    if (timerRef.current) clearTimeout(timerRef.current);

    timerRef.current = setTimeout(async () => {
      const config: RoomConfig = {
        length: room.length,
        width: room.width,
        height: room.height,
        surfaces: room.surfaces,
        speakers: room.speakers,
        listener: room.listener,
        room_objects: room.roomObjects.map((o) => ({
          id: o.id,
          type: o.type,
          wall_surface: o.wallSurface,
          pos_u: o.posU,
          pos_v: o.posV,
          width: o.width,
          height: o.height,
        })) as any,
        model_objects: room.modelObjects.map((o) => ({
          id: o.id,
          model_id: o.modelId,
          filename: o.filename,
          url: o.url,
          material: o.material,
          wall_surface: o.wallSurface,
          position: o.position,
          rotation: o.rotation,
          scale: o.scale,
          bbox_w: o.bboxW,
          bbox_h: o.bboxH,
          bbox_d: o.bboxD,
        })) as any,
      };
      try {
        const updated = await putRoom(sessionId, config);
        room.setRt60Preview(updated.rt60_preview ?? null);
      } catch {
        // silent — sync will retry on next change
      }
    }, DEBOUNCE_MS);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [
    sessionId,
    room.length, room.width, room.height,
    room.surfaces, room.speakers, room.listener,
    room.roomObjects, room.modelObjects,
  ]);
}
