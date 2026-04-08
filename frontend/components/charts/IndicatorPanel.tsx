"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  LineSeries,
  HistogramSeries,
  type IChartApi,
  type Time,
  ColorType,
  LineStyle,
} from "lightweight-charts";

interface IndicatorPanelProps {
  timestamps: string[];
  rsi?: number[];
  macdLine?: number[];
  macdSignal?: number[];
  macdHist?: number[];
  height?: number;
}

export function IndicatorPanel({
  timestamps,
  rsi,
  macdLine,
  macdSignal,
  macdHist,
  height = 150,
}: IndicatorPanelProps) {
  const rsiRef = useRef<HTMLDivElement>(null);
  const macdRef = useRef<HTMLDivElement>(null);
  const rsiChartRef = useRef<IChartApi | null>(null);
  const macdChartRef = useRef<IChartApi | null>(null);

  const chartOpts = {
    height,
    layout: {
      background: { type: ColorType.Solid as const, color: "#1e2329" },
      textColor: "#848e9c",
    },
    grid: { vertLines: { color: "#2b3139" }, horzLines: { color: "#2b3139" } },
    rightPriceScale: { borderColor: "#2b3139" },
    timeScale: { borderColor: "#2b3139", timeVisible: true, secondsVisible: false },
  };

  useEffect(() => {
    if (!rsiRef.current || !rsi || rsi.length === 0) return;
    if (rsiChartRef.current) rsiChartRef.current.remove();

    const chart = createChart(rsiRef.current, chartOpts);
    rsiChartRef.current = chart;

    const series = chart.addSeries(LineSeries, {
      color: "#f0b90b",
      lineWidth: 1,
      priceLineVisible: false,
    });
    series.setData(
      timestamps
        .map((t, i) =>
          rsi[i] != null ? { time: (new Date(t).getTime() / 1000) as Time, value: rsi[i] } : null
        )
        .filter(Boolean) as { time: Time; value: number }[]
    );

    // RSI levels
    const overbought = chart.addSeries(LineSeries, {
      color: "rgba(246,70,93,0.4)", lineWidth: 1, lineStyle: LineStyle.Dashed,
      priceLineVisible: false, lastValueVisible: false,
    });
    const oversold = chart.addSeries(LineSeries, {
      color: "rgba(14,203,129,0.4)", lineWidth: 1, lineStyle: LineStyle.Dashed,
      priceLineVisible: false, lastValueVisible: false,
    });
    const lvl = (val: number) => timestamps.map((t) => ({ time: (new Date(t).getTime() / 1000) as Time, value: val }));
    overbought.setData(lvl(70));
    oversold.setData(lvl(30));
    chart.timeScale().fitContent();

    const ro = new ResizeObserver((e) => { for (const x of e) chart.applyOptions({ width: x.contentRect.width }); });
    ro.observe(rsiRef.current);
    return () => { ro.disconnect(); chart.remove(); rsiChartRef.current = null; };
  }, [timestamps, rsi, height]);

  useEffect(() => {
    if (!macdRef.current || !macdLine || macdLine.length === 0) return;
    if (macdChartRef.current) macdChartRef.current.remove();

    const chart = createChart(macdRef.current, chartOpts);
    macdChartRef.current = chart;

    const line = chart.addSeries(LineSeries, { color: "#2196f3", lineWidth: 1, priceLineVisible: false });
    line.setData(
      timestamps.map((t, i) => macdLine[i] != null ? { time: (new Date(t).getTime() / 1000) as Time, value: macdLine[i] } : null)
        .filter(Boolean) as { time: Time; value: number }[]
    );

    if (macdSignal) {
      const sig = chart.addSeries(LineSeries, { color: "#ff9800", lineWidth: 1, priceLineVisible: false });
      sig.setData(
        timestamps.map((t, i) => macdSignal[i] != null ? { time: (new Date(t).getTime() / 1000) as Time, value: macdSignal[i] } : null)
          .filter(Boolean) as { time: Time; value: number }[]
      );
    }

    if (macdHist) {
      const hist = chart.addSeries(HistogramSeries, { priceLineVisible: false });
      hist.setData(
        timestamps.map((t, i) => macdHist[i] != null ? {
          time: (new Date(t).getTime() / 1000) as Time, value: macdHist[i],
          color: macdHist[i] >= 0 ? "rgba(14,203,129,0.5)" : "rgba(246,70,93,0.5)",
        } : null).filter(Boolean) as { time: Time; value: number; color: string }[]
      );
    }

    chart.timeScale().fitContent();
    const ro = new ResizeObserver((e) => { for (const x of e) chart.applyOptions({ width: x.contentRect.width }); });
    ro.observe(macdRef.current);
    return () => { ro.disconnect(); chart.remove(); macdChartRef.current = null; };
  }, [timestamps, macdLine, macdSignal, macdHist, height]);

  return (
    <div className="space-y-2">
      {rsi && (
        <div>
          <div className="text-xs text-muted px-2 py-1">RSI (14)</div>
          <div ref={rsiRef} className="w-full rounded-lg overflow-hidden" />
        </div>
      )}
      {macdLine && (
        <div>
          <div className="text-xs text-muted px-2 py-1">MACD (12,26,9)</div>
          <div ref={macdRef} className="w-full rounded-lg overflow-hidden" />
        </div>
      )}
    </div>
  );
}
