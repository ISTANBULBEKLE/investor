"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface ComponentSignal {
  source: string;
  signal: string;
  score: number;
  weight: number;
  available: boolean;
}

interface EnsembleSignal {
  symbol: string;
  signal: string;
  confidence: number;
  composite_score: number;
  components: ComponentSignal[];
  reasoning: string[];
  timestamp: string;
}

interface TAIndicators {
  rsi_14: number | null;
  macd_line: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  bb_upper: number | null;
  bb_middle: number | null;
  bb_lower: number | null;
  sma_50: number | null;
  sma_200: number | null;
  ema_12: number | null;
  ema_26: number | null;
  atr_14: number | null;
  obv: number | null;
  stoch_rsi_k: number | null;
  stoch_rsi_d: number | null;
}

interface TASignal {
  symbol: string;
  signal: string;
  score: number;
  indicators: TAIndicators;
  reasoning: string[];
}

interface SentimentData {
  symbol: string;
  signal: string;
  score: number;
  news_score: number | null;
  reddit_score: number | null;
  fear_greed: { value: number; classification: string; signal_contribution: number } | null;
  sources_available: string[];
}

interface ServiceStatus {
  binance: boolean;
  coingecko: boolean;
  ollama: boolean;
  reddit: boolean;
  fear_greed: boolean;
}

export function useEnsembleSignal(symbol: string) {
  return useQuery<EnsembleSignal>({
    queryKey: ["signal", symbol],
    queryFn: () => api.get(`/api/signals/${symbol}`),
    refetchInterval: 120_000, // 2 min
    enabled: !!symbol,
    retry: 1,
  });
}

export function useTechnicalAnalysis(symbol: string) {
  return useQuery<TASignal>({
    queryKey: ["ta", symbol],
    queryFn: () => api.get(`/api/analysis/${symbol}/technical`),
    refetchInterval: 120_000,
    enabled: !!symbol,
    retry: 1,
  });
}

export function useSentiment(symbol: string) {
  return useQuery<SentimentData>({
    queryKey: ["sentiment", symbol],
    queryFn: () => api.get(`/api/analysis/${symbol}/sentiment`),
    refetchInterval: 300_000, // 5 min
    enabled: !!symbol,
    retry: 1,
  });
}

export function useServiceStatus() {
  return useQuery<ServiceStatus>({
    queryKey: ["services"],
    queryFn: () => api.get("/api/analysis/services/status"),
    refetchInterval: 60_000,
  });
}

export function useSignalHistory(symbol: string, days: number = 30) {
  return useQuery<Array<{ signal: string; confidence: number; timestamp: string }>>({
    queryKey: ["signalHistory", symbol, days],
    queryFn: () => api.get(`/api/signals/${symbol}/history?days=${days}`),
    enabled: !!symbol,
  });
}
