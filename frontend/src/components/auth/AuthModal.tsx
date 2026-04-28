import { useState } from "react";
import { login, register, googleLoginUrl, githubLoginUrl } from "../../api/auth";
import { useAuthStore } from "../../store/authStore";

interface Props {
  onClose: () => void;
}

export function AuthModal({ onClose }: Props) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { setTokens } = useAuthStore();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res =
        mode === "login"
          ? await login(email, password)
          : await register(email, password, displayName || undefined);
      setTokens(res.access_token, res.refresh_token);
      onClose();
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Something went wrong";
      setError(typeof msg === "string" ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-panel border border-white/10 rounded-2xl p-6 w-full max-w-sm mx-4 flex flex-col gap-5"
        onClick={(e) => e.stopPropagation()}
      >
        <div>
          <h2 className="text-white text-xl font-bold">
            {mode === "login" ? "Sign in" : "Create account"}
          </h2>
          <p className="text-muted text-sm mt-0.5">
            Save your rooms and audio library across devices
          </p>
        </div>

        {/* OAuth buttons */}
        <div className="flex gap-2">
          <a
            href={googleLoginUrl()}
            className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-white text-sm font-medium transition-colors"
          >
            <span>G</span> Google
          </a>
          <a
            href={githubLoginUrl()}
            className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-white text-sm font-medium transition-colors"
          >
            <span>⌥</span> GitHub
          </a>
        </div>

        <div className="flex items-center gap-3">
          <hr className="flex-1 border-white/10" />
          <span className="text-muted text-xs">or</span>
          <hr className="flex-1 border-white/10" />
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          {mode === "register" && (
            <input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Display name (optional)"
              className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-muted focus:outline-none focus:border-accent"
            />
          )}
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-muted focus:outline-none focus:border-accent"
          />
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-muted focus:outline-none focus:border-accent"
          />
          {error && <p className="text-red-400 text-xs">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="py-2.5 rounded-lg font-semibold text-sm bg-accent text-white hover:bg-accent/80 disabled:opacity-40 transition-all"
          >
            {loading ? "…" : mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>

        <button
          onClick={() => setMode(mode === "login" ? "register" : "login")}
          className="text-muted text-xs text-center hover:text-white transition-colors"
        >
          {mode === "login" ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
        </button>
      </div>
    </div>
  );
}
