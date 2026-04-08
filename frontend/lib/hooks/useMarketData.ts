"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface TickerData {
  symbol: string;
  price: number;
  price_change_24h: number;
  price_change_pct_24h: number;
  high_24h: number;
  low_24h: number;
  volume_24h: number;
  timestamp: string;
}

interface OHLCVItem {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface OHLCVData {
  symbol: string;
  timeframe: string;
  data: OHLCVItem[];
}

export function usePrice(symbol: string) {
  return useQuery<TickerData>({
    queryKey: ["price", symbol],
    queryFn: () => api.get(`/api/market/${symbol}/price`),
    refetchInterval: 30_000,
    enabled: !!symbol,
  });
}

export function useOHLCV(
  symbol: string,
  timeframe: string = "1h",
  limit: number = 100
) {
  return useQuery<OHLCVData>({
    queryKey: ["ohlcv", symbol, timeframe, limit],
    queryFn: () =>
      api.get(`/api/market/${symbol}/ohlcv?timeframe=${timeframe}&limit=${limit}`),
    refetchInterval: 60_000,
    enabled: !!symbol,
  });
}
