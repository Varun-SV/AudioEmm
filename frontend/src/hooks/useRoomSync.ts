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
  ]);
}
