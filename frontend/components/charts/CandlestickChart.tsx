"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  CandlestickSeries,
  HistogramSeries,
  type IChartApi,
  type CandlestickData,
  type HistogramData,
  type Time,
  ColorType,
  LineStyle,
} from "lightweight-charts";

interface OHLCVItem {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface CandlestickChartProps {
  data: OHLCVItem[];
  height?: number;
}

export function CandlestickChart({ data, height = 400 }: CandlestickChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;

    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const chart = createChart(containerRef.current, {
      height,
      layout: {
        background: { type: ColorType.Solid, color: "#1e2329" },
        textColor: "#848e9c",
      },
      grid: {
        vertLines: { color: "#2b3139" },
        horzLines: { color: "#2b3139" },
      },
      crosshair: {
        vertLine: { color: "#f0b90b", width: 1, style: LineStyle.Dashed },
        horzLine: { color: "#f0b90b", width: 1, style: LineStyle.Dashed },
      },
      rightPriceScale: { borderColor: "#2b3139" },
      timeScale: { borderColor: "#2b3139", timeVisible: true, secondsVisible: false },
    });
    chartRef.current = chart;

    // Candlestick series
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#0ecb81",
      downColor: "#f6465d",
      borderUpColor: "#0ecb81",
      borderDownColor: "#f6465d",
      wickUpColor: "#0ecb81",
      wickDownColor: "#f6465d",
    });

    const candleData: CandlestickData<Time>[] = data.map((d) => ({
      time: (new Date(d.timestamp).getTime() / 1000) as Time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));
    candleSeries.setData(candleData);

    // Volume histogram
    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });
    chart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    const volumeData: HistogramData<Time>[] = data.map((d, i) => ({
      time: (new Date(d.timestamp).getTime() / 1000) as Time,
      value: d.volume,
      color:
        i > 0 && d.close >= data[i - 1].close
          ? "rgba(14,203,129,0.3)"
          : "rgba(246,70,93,0.3)",
    }));
    volumeSeries.setData(volumeData);

    chart.timeScale().fitContent();

    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) chart.applyOptions({ width: entry.contentRect.width });
    });
    ro.observe(containerRef.current);

    return () => {
      ro.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, [data, height]);

  return <div ref={containerRef} className="w-full rounded-lg overflow-hidden" />;
}
