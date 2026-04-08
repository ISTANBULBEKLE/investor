"use client";

import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    await authClient.signIn.email(
      { email, password },
      {
        onSuccess: () => {
          router.push("/dashboard");
          router.refresh();
        },
        onError: (ctx) => {
          setError(ctx.error.message || "Invalid credentials");
          setLoading(false);
        },
      }
    );
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-accent">INVESTOR</h1>
          <p className="text-muted text-sm mt-1">
            AI-Powered Crypto Prediction
          </p>
        </div>

        <form
          onSubmit={handleSignIn}
          className="bg-card border border-border rounded-xl p-6 space-y-4"
        >
          <div>
            <label className="block text-sm text-muted mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-background border border-border rounded-lg px-3 py-2 text-foreground focus:outline-none focus:border-accent"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-muted mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-background border border-border rounded-lg px-3 py-2 text-foreground focus:outline-none focus:border-accent"
              required
            />
          </div>

          {error && <p className="text-sell text-sm">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-accent text-background py-2.5 rounded-lg font-medium hover:bg-accent/90 disabled:opacity-50 transition-colors"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="text-center text-xs text-muted mt-4">
          First time? Use the sign-up script to create your account.
        </p>
      </div>
    </div>
  );
}
