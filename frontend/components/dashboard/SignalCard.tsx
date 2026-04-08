"use client";

import { usePrice } from "@/lib/hooks/useMarketData";

interface SignalCardProps {
  symbol: string;
  isSelected: boolean;
  onSelect: () => void;
  signal?: string;
  confidence?: number;
}

const SIGNAL_STYLES: Record<string, { bg: string; text: string }> = {
  STRONG_BUY: { bg: "bg-buy/15", text: "text-buy" },
  BUY: { bg: "bg-buy/10", text: "text-buy" },
  HOLD: { bg: "bg-hold/10", text: "text-hold" },
  SELL: { bg: "bg-sell/10", text: "text-sell" },
  STRONG_SELL: { bg: "bg-sell/15", text: "text-sell" },
};

function formatPrice(price: number): string {
  if (price >= 1000) return price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  if (price >= 1) return price.toFixed(4);
  return price.toFixed(6);
}

export function SignalCard({ symbol, isSelected, onSelect, signal, confidence }: SignalCardProps) {
  const { data: priceData, isLoading: priceLoading } = usePrice(symbol);

  const sig = signal || "HOLD";
  const style = SIGNAL_STYLES[sig] || SIGNAL_STYLES.HOLD;
  const changeColor = priceData && priceData.price_change_pct_24h >= 0 ? "text-buy" : "text-sell";

  return (
    <button
      onClick={onSelect}
      className={`w-full text-left bg-card border rounded-xl p-5 transition-colors ${
        isSelected ? "border-accent" : "border-border hover:border-muted"
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-base font-semibold">{symbol}/USDT</h3>
        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${style.bg} ${style.text}`}>
          {sig.replace("_", " ")}
        </span>
      </div>

      {priceLoading && <div className="text-xl font-bold text-muted">...</div>}

      {priceData && (
        <>
          <div className="text-2xl font-bold">${formatPrice(priceData.price)}</div>
          <div className={`text-sm font-medium ${changeColor}`}>
            {priceData.price_change_pct_24h >= 0 ? "+" : ""}
            {priceData.price_change_pct_24h.toFixed(2)}%
          </div>
        </>
      )}

      {confidence != null && (
        <div className="mt-3 text-xs text-muted">
          Confidence: {(confidence * 100).toFixed(0)}%
        </div>
      )}
    </button>
  );
}
