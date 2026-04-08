"use client";

import dynamic from "next/dynamic";
import { useAppStore } from "@/lib/store/app-store";
import { useOHLCV } from "@/lib/hooks/useMarketData";
import { useEnsembleSignal, useServiceStatus } from "@/lib/hooks/useSignal";
import { SignalCard } from "@/components/dashboard/SignalCard";
import { MetricsGrid } from "@/components/dashboard/MetricsGrid";
import { SignalBreakdown } from "@/components/dashboard/SignalBreakdown";

const CandlestickChart = dynamic(
  () => import("@/components/charts/CandlestickChart").then((m) => m.CandlestickChart),
  { ssr: false, loading: () => <div className="h-[400px] bg-card rounded-xl flex items-center justify-center text-muted">Loading chart...</div> }
);

const SYMBOLS = ["BTC", "ETH", "HBAR", "IOTA"];
const TIMEFRAMES = ["1h", "4h", "1d"] as const;

export default function DashboardPage() {
  const { selectedSymbol, setSelectedSymbol, selectedTimeframe, setSelectedTimeframe } = useAppStore();
  const { data: ohlcv } = useOHLCV(selectedSymbol, selectedTimeframe, 200);
  const { data: services } = useServiceStatus();

  // Only fetch the ensemble signal for the SELECTED symbol (avoids 4x heavy requests)
  const { data: activeSignal } = useEnsembleSignal(selectedSymbol);

  const chartData = ohlcv?.data || [];

  return (
    <div className="space-y-6">
      {/* Header with service status */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Dashboard</h2>
        {services && (
          <div className="flex gap-2 text-xs">
            {Object.entries(services).map(([name, online]) => (
              <span
                key={name}
                className={`px-2 py-1 rounded ${online ? "bg-buy/10 text-buy" : "bg-border text-muted"}`}
              >
                {name}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Signal Cards — prices only, signal shown for selected */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        {SYMBOLS.map((symbol) => (
          <SignalCard
            key={symbol}
            symbol={symbol}
            isSelected={selectedSymbol === symbol}
            onSelect={() => setSelectedSymbol(symbol)}
            signal={selectedSymbol === symbol ? activeSignal?.signal : undefined}
            confidence={selectedSymbol === symbol ? activeSignal?.confidence : undefined}
          />
        ))}
      </div>

      {/* Chart */}
      <div className="bg-card border border-border rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold">{selectedSymbol}/USDT</h3>
          <div className="flex gap-1">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf}
                onClick={() => setSelectedTimeframe(tf)}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  selectedTimeframe === tf
                    ? "bg-accent text-background"
                    : "text-muted hover:text-foreground"
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {chartData.length > 0 ? (
          <CandlestickChart data={chartData} height={400} />
        ) : (
          <div className="h-[400px] flex items-center justify-center text-muted">
            Loading chart data...
          </div>
        )}
      </div>

      {/* Metrics + Signal Breakdown for selected symbol */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MetricsGrid symbol={selectedSymbol} />
        <SignalBreakdown symbol={selectedSymbol} />
      </div>
    </div>
  );
}
