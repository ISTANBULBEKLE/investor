"use client";

import { useEnsembleSignal } from "@/lib/hooks/useSignal";

interface SignalBreakdownProps {
  symbol: string;
}

const SOURCE_LABELS: Record<string, string> = {
  technical: "Technical Analysis",
  ml: "ML Prediction",
  sentiment: "Sentiment",
  llm: "LLM Analysis",
};

const SIGNAL_COLORS: Record<string, string> = {
  STRONG_BUY: "bg-buy",
  BUY: "bg-buy/60",
  HOLD: "bg-hold",
  SELL: "bg-sell/60",
  STRONG_SELL: "bg-sell",
};

export function SignalBreakdown({ symbol }: SignalBreakdownProps) {
  const { data } = useEnsembleSignal(symbol);

  if (!data) return null;

  return (
    <div className="bg-card border border-border rounded-xl p-5 space-y-4">
      <h3 className="text-sm font-semibold">Signal Breakdown</h3>

      <div className="space-y-3">
        {data.components.map((comp) => (
          <div key={comp.source} className="flex items-center gap-3">
            <div className="w-28 text-xs text-muted">
              {SOURCE_LABELS[comp.source] || comp.source}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-border rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      comp.score > 0 ? "bg-buy" : comp.score < 0 ? "bg-sell" : "bg-hold"
                    }`}
                    style={{ width: `${Math.min(100, Math.abs(comp.score) * 100)}%`, marginLeft: comp.score < 0 ? "auto" : 0 }}
                  />
                </div>
                <span className="text-xs font-mono w-12 text-right">
                  {comp.score >= 0 ? "+" : ""}{comp.score.toFixed(2)}
                </span>
              </div>
            </div>
            <div className="w-16 text-right">
              {comp.available ? (
                <span className={`text-xs px-2 py-0.5 rounded ${SIGNAL_COLORS[comp.signal] || "bg-hold"} text-background`}>
                  {comp.signal.replace("_", " ")}
                </span>
              ) : (
                <span className="text-xs text-muted">offline</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {data.reasoning.length > 0 && (
        <div className="border-t border-border pt-3">
          <div className="text-xs text-muted mb-1">Reasoning</div>
          <ul className="text-xs space-y-1">
            {data.reasoning.map((r, i) => (
              <li key={i} className="text-muted">
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
