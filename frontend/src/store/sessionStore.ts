import { create } from "zustand";

interface SessionState {
  sessionId: string | null;
  rirId: string | null;
  setSessionId: (id: string) => void;
  setRirId: (id: string | null) => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  rirId: null,
  setSessionId: (id) => set({ sessionId: id }),
  setRirId: (id) => set({ rirId: id }),
}));
