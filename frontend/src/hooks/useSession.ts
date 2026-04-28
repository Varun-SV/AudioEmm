import { useEffect } from "react";
import { createSession, getSession } from "../api/sessions";
import { getRoom } from "../api/room";
import { useSessionStore } from "../store/sessionStore";
import { useRoomStore } from "../store/roomStore";

const SESSION_KEY = "audioemm_session_id";

export function useSession() {
  const { sessionId, setSessionId } = useSessionStore();
  const { loadConfig } = useRoomStore();

  useEffect(() => {
    if (sessionId) return;

    async function init() {
      const stored = localStorage.getItem(SESSION_KEY);
      let id: string | null = stored;

      if (stored) {
        try {
          await getSession(stored);
        } catch {
          id = null;
          localStorage.removeItem(SESSION_KEY);
        }
      }

      if (!id) {
        try {
          const s = await createSession();
          id = s.session_id;
          localStorage.setItem(SESSION_KEY, id);
        } catch (err) {
          console.error("[useSession] Failed to create session, retrying in 3s:", err);
          setTimeout(init, 3000);
          return;
        }
      }

      setSessionId(id);

      try {
        const config = await getRoom(id);
        loadConfig(config);
      } catch {
        // Fresh session, use defaults
      }
    }

    init();
  }, [sessionId, setSessionId, loadConfig]);

  return sessionId;
}
