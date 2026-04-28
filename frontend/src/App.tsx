import { useSession } from "./hooks/useSession";
import { AppShell } from "./components/layout/AppShell";

export default function App() {
  const sessionId = useSession();

  if (!sessionId) {
    return (
      <div className="h-screen flex items-center justify-center bg-surface">
        <div className="text-center">
          <div className="text-2xl font-bold mb-2">
            Audio<span className="text-accent">Emm</span>
          </div>
          <p className="text-muted text-sm">Initialising session…</p>
        </div>
      </div>
    );
  }

  return <AppShell />;
}
