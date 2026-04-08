"use client";

import { useState } from "react";
import { useSignalHistory } from "@/lib/hooks/useSignal";

const SIGNAL_COLORS: Record<string, string> = {
  STRONG_BUY: "text-buy",
  BUY: "text-buy",
  HOLD: "text-hold",
  SELL: "text-sell",
  STRONG_SELL: "text-sell",
};

const SYMBOLS = ["BTC", "ETH", "HBAR", "IOTA"];

export default function PredictionsPage() {
  const [symbol, setSymbol] = useState("BTC");
  const { data: history = [], isLoading } = useSignalHistory(symbol, 30);

  // Compute stats
  const total = history.length;
  const signalCounts: Record<string, number> = {};
  for (const h of history) {
    signalCounts[h.signal] = (signalCounts[h.signal] || 0) + 1;
  }
  const avgConfidence = total > 0
    ? history.reduce((s, h) => s + h.confidence, 0) / total
    : 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Predictions</h2>
        <div className="flex gap-2">
          {SYMBOLS.map((s) => (
            <button
              key={s}
              onClick={() => setSymbol(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                symbol === s
                  ? "bg-accent text-background"
                  : "bg-card text-muted border border-border hover:text-foreground"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-card border border-border rounded-xl p-4">
          <div className="text-xs text-muted">Total Signals</div>
          <div className="text-2xl font-bold">{total}</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-4">
          <div className="text-xs text-muted">Avg Confidence</div>
          <div className="text-2xl font-bold">{(avgConfidence * 100).toFixed(0)}%</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-4">
          <div className="text-xs text-muted">Buy Signals</div>
          <div className="text-2xl font-bold text-buy">
            {(signalCounts["BUY"] || 0) + (signalCounts["STRONG_BUY"] || 0)}
          </div>
        </div>
        <div className="bg-card border border-border rounded-xl p-4">
          <div className="text-xs text-muted">Sell Signals</div>
          <div className="text-2xl font-bold text-sell">
            {(signalCounts["SELL"] || 0) + (signalCounts["STRONG_SELL"] || 0)}
          </div>
        </div>
      </div>

      {/* Signal History Table */}
      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-muted">
              <th className="py-3 px-4 text-left font-medium">Time</th>
              <th className="py-3 px-4 text-left font-medium">Signal</th>
              <th className="py-3 px-4 text-right font-medium">Confidence</th>
              <th className="py-3 px-4 text-right font-medium">TA</th>
              <th className="py-3 px-4 text-right font-medium">ML</th>
              <th className="py-3 px-4 text-right font-medium">Sentiment</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr><td colSpan={6} className="py-8 text-center text-muted">Loading...</td></tr>
            )}
            {!isLoading && history.length === 0 && (
              <tr><td colSpan={6} className="py-8 text-center text-muted">
                No signal history yet. Signals are generated every 30 minutes.
              </td></tr>
            )}
            {history.map((h, i) => (
              <tr key={i} className="border-b border-border hover:bg-background/50">
                <td className="py-3 px-4 text-muted">
                  {h.timestamp ? new Date(h.timestamp).toLocaleString() : "--"}
                </td>
                <td className={`py-3 px-4 font-medium ${SIGNAL_COLORS[h.signal] || "text-foreground"}`}>
                  {h.signal?.replace("_", " ")}
                </td>
                <td className="py-3 px-4 text-right">
                  {(h.confidence * 100).toFixed(0)}%
                </td>
                <td className="py-3 px-4 text-right text-muted">
                  {(h as Record<string, unknown>).technical_score != null
                    ? Number((h as Record<string, unknown>).technical_score).toFixed(2)
                    : "--"}
                </td>
                <td className="py-3 px-4 text-right text-muted">
                  {(h as Record<string, unknown>).ml_score != null
                    ? Number((h as Record<string, unknown>).ml_score).toFixed(2)
                    : "--"}
                </td>
                <td className="py-3 px-4 text-right text-muted">
                  {(h as Record<string, unknown>).sentiment_score != null
                    ? Number((h as Record<string, unknown>).sentiment_score).toFixed(2)
                    : "--"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
