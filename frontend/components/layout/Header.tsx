"use client";

import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";

export function Header() {
  const router = useRouter();
  const { data: session } = authClient.useSession();

  const handleSignOut = async () => {
    await authClient.signOut({
      fetchOptions: {
        onSuccess: () => {
          router.push("/login");
          router.refresh();
        },
      },
    });
  };

  return (
    <header className="h-14 border-b border-border bg-card flex items-center justify-between px-6">
      <div className="text-sm text-muted">
        {session?.user?.email && (
          <span>{session.user.email}</span>
        )}
      </div>
      <button
        onClick={handleSignOut}
        className="text-sm text-muted hover:text-foreground transition-colors"
      >
        Sign Out
      </button>
    </header>
  );
}
