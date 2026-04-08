"use client";

import { useEffect, useState } from "react";
import { useSettings, useUpdateSettings } from "@/lib/hooks/useSettings";
import { useServiceStatus } from "@/lib/hooks/useSignal";

const SUPPORTED_SYMBOLS = [
  "BTC", "ETH", "HBAR", "IOTA", "SOL", "BNB", "XRP", "ADA", "DOGE", "DOT",
  "AVAX", "LINK", "MATIC", "UNI", "ATOM", "LTC", "ARB",
  "OP", "SUI", "APT", "NEAR", "FIL",
];

export default function SettingsPage() {
  const { data: settings, isLoading } = useSettings();
  const { data: services } = useServiceStatus();
  const updateSettings = useUpdateSettings();

  const [selected, setSelected] = useState<string[]>([]);
  const [email, setEmail] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (settings) {
      setSelected(settings.symbols);
      setEmail(settings.email);
    }
  }, [settings]);

  const toggleSymbol = (symbol: string) => {
    setSelected((prev) =>
      prev.includes(symbol)
        ? prev.filter((s) => s !== symbol)
        : [...prev, symbol]
    );
  };

  const handleSave = async () => {
    if (selected.length < 2 || selected.length > 10) return;
    updateSettings.mutate(
      { symbols: selected, email },
      {
        onSuccess: () => {
          setSaved(true);
          setTimeout(() => setSaved(false), 2000);
        },
      }
    );
  };

  if (isLoading) {
    return <div className="text-muted p-6">Loading settings...</div>;
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <h2 className="text-2xl font-bold">Settings</h2>

      {/* Tracked Symbols */}
      <div className="bg-card border border-border rounded-xl p-6 space-y-4">
        <h3 className="text-lg font-semibold">Tracked Cryptocurrencies</h3>
        <p className="text-sm text-muted">
          Select 2–10 symbols to monitor. Currently tracking {selected.length}.
        </p>

        <div className="flex flex-wrap gap-2">
          {SUPPORTED_SYMBOLS.map((s) => {
            const isSelected = selected.includes(s);
            return (
              <button
                key={s}
                onClick={() => toggleSymbol(s)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                  isSelected
                    ? "bg-accent/15 border-accent text-accent"
                    : "bg-background border-border text-muted hover:text-foreground"
                }`}
              >
                {s}
              </button>
            );
          })}
        </div>
      </div>

      {/* Email Alerts */}
      <div className="bg-card border border-border rounded-xl p-6 space-y-4">
        <h3 className="text-lg font-semibold">Email Alerts</h3>
        <p className="text-sm text-muted">
          Receive email notifications when signals change or extreme conditions are detected.
        </p>
        <div>
          <label className="block text-sm text-muted mb-1">Alert Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            className="w-full bg-background border border-border rounded-lg px-3 py-2 text-foreground focus:outline-none focus:border-accent"
          />
        </div>
        <div className="text-xs text-muted">
          Alerts are rate-limited to 1 per symbol per hour. Configure RESEND_API_KEY in backend .env to enable.
        </div>
      </div>

      {/* Service Status */}
      <div className="bg-card border border-border rounded-xl p-6 space-y-4">
        <h3 className="text-lg font-semibold">Service Status</h3>
        {services ? (
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(services).map(([name, online]) => (
              <div
                key={name}
                className="flex items-center justify-between bg-background border border-border rounded-lg px-4 py-2.5"
              >
                <span className="text-sm capitalize">{name.replace("_", " ")}</span>
                <span
                  className={`text-xs font-medium px-2 py-0.5 rounded ${
                    online ? "bg-buy/10 text-buy" : "bg-sell/10 text-sell"
                  }`}
                >
                  {online ? "Online" : "Offline"}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted">Checking services...</p>
        )}
      </div>

      {/* Save */}
      <button
        onClick={handleSave}
        disabled={updateSettings.isPending || selected.length < 2 || selected.length > 10}
        className="bg-accent text-background px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-accent/90 disabled:opacity-50 transition-colors"
      >
        {updateSettings.isPending
          ? "Saving..."
          : saved
          ? "Saved!"
          : "Save Settings"}
      </button>
    </div>
  );
}
