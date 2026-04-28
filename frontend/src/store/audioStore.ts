import { create } from "zustand";
import type { ProcessingState } from "../types/audio";

interface AudioState {
  uploadId: string | null;
  uploadFilename: string | null;
  uploadDuration: number | null;
  processingState: ProcessingState;
  resultUrl: string | null;
  resultDuration: number | null;
  errorMessage: string | null;
  activeEqProfileId: string | null;

  setUpload: (id: string, filename: string, duration: number) => void;
  setProcessingState: (s: ProcessingState) => void;
  setResult: (url: string, duration: number) => void;
  setError: (msg: string) => void;
  setActiveEqProfile: (id: string | null) => void;
  reset: () => void;
}

export const useAudioStore = create<AudioState>((set) => ({
  uploadId: null,
  uploadFilename: null,
  uploadDuration: null,
  processingState: "idle",
  resultUrl: null,
  resultDuration: null,
  errorMessage: null,
  activeEqProfileId: null,

  setUpload: (id, filename, duration) =>
    set({ uploadId: id, uploadFilename: filename, uploadDuration: duration, processingState: "idle" }),

  setProcessingState: (s) => set({ processingState: s }),

  setResult: (url, duration) =>
    set({ resultUrl: url, resultDuration: duration, processingState: "done" }),

  setError: (msg) => set({ errorMessage: msg, processingState: "error" }),

  setActiveEqProfile: (id) => set({ activeEqProfileId: id }),

  reset: () =>
    set({
      uploadId: null,
      uploadFilename: null,
      uploadDuration: null,
      processingState: "idle",
      resultUrl: null,
      resultDuration: null,
      errorMessage: null,
    }),
}));
