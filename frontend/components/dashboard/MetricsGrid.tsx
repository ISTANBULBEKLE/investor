"use client";

import { useTechnicalAnalysis, useSentiment } from "@/lib/hooks/useSignal";

interface MetricsGridProps {
  symbol: string;
}

function MetricCard({ label, value, subtext }: { label: string; value: string; subtext?: string }) {
  return (
    <div className="bg-card border border-border rounded-xl p-4">
      <div className="text-xs text-muted mb-1">{label}</div>
      <div className="text-xl font-semibold">{value}</div>
      {subtext && <div className="text-xs text-muted mt-0.5">{subtext}</div>}
    </div>
  );
}

export function MetricsGrid({ symbol }: MetricsGridProps) {
  const { data: ta } = useTechnicalAnalysis(symbol);
  const { data: sent } = useSentiment(symbol);

  const rsi = ta?.indicators.rsi_14;
  const macdHist = ta?.indicators.macd_histogram;
  const fg = sent?.fear_greed;
  const sentScore = sent?.score;

  const rsiLabel = rsi != null
    ? rsi < 30 ? "Oversold" : rsi > 70 ? "Overbought" : "Neutral"
    : "";

  const macdLabel = macdHist != null
    ? macdHist > 0 ? "Bullish" : "Bearish"
    : "";

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <MetricCard
        label="RSI (14)"
        value={rsi != null ? rsi.toFixed(1) : "--"}
        subtext={rsiLabel}
      />
      <MetricCard
        label="MACD Histogram"
        value={macdHist != null ? macdHist.toFixed(2) : "--"}
        subtext={macdLabel}
      />
      <MetricCard
        label="Fear & Greed"
        value={fg ? `${fg.value}` : "--"}
        subtext={fg?.classification}
      />
      <MetricCard
        label="Sentiment"
        value={sentScore != null ? sentScore.toFixed(2) : "--"}
        subtext={sent ? `${sent.sources_available.length} source(s)` : ""}
      />
    </div>
  );
}
