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
      let id = stored;

      if (stored) {
        try {
          await getSession(stored);
        } catch {
          id = null;
        }
      }

      if (!id) {
        const s = await createSession();
        id = s.session_id;
        localStorage.setItem(SESSION_KEY, id);
      }

      setSessionId(id);

      // Load persisted room config
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
