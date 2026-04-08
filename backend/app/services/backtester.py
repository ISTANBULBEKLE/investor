import logging

import numpy as np
import pandas as pd

from app.models.feature_engineering import engineer_features
from app.schemas.backtest import BacktestResult
from app.services.technical_analysis import ta_service

logger = logging.getLogger(__name__)


class BacktestEngine:
    def run(
        self,
        symbol: str,
        df: pd.DataFrame,
        strategy: str = "ta",
        position_size_pct: float = 1.0,
    ) -> BacktestResult:
        """Run backtest on historical OHLCV data."""
        df = df.copy().sort_values("timestamp").reset_index(drop=True)

        if strategy == "ta":
            signals = self._generate_ta_signals(df)
        else:
            signals = self._generate_ta_signals(df)  # Default to TA for now

        trades = self._simulate_trades(df, signals, position_size_pct)
        return self._compute_metrics(symbol, strategy, trades)

    def _generate_ta_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate a signal series from TA indicators."""
        featured = ta_service.compute_indicators(df.copy())
        signals = pd.Series(0, index=df.index)  # 0=HOLD, 1=BUY, -1=SELL

        rsi = featured.get("rsi_14")
        macd_hist = featured.get("macd_histogram")

        if rsi is not None:
            signals[rsi < 35] = 1
            signals[rsi > 65] = -1

        if macd_hist is not None:
            # MACD crossover confirmation
            prev_hist = macd_hist.shift(1)
            bullish_cross = (prev_hist < 0) & (macd_hist > 0)
            bearish_cross = (prev_hist > 0) & (macd_hist < 0)
            signals[bullish_cross & (signals >= 0)] = 1
            signals[bearish_cross & (signals <= 0)] = -1

        return signals

    def _simulate_trades(
        self, df: pd.DataFrame, signals: pd.Series, position_size_pct: float
    ) -> list[dict]:
        """Simple long-only simulation."""
        trades: list[dict] = []
        in_position = False
        entry_price = 0.0
        entry_time = ""

        for i in range(len(df)):
            if signals.iloc[i] == 1 and not in_position:
                in_position = True
                entry_price = df.iloc[i]["close"]
                entry_time = str(df.iloc[i]["timestamp"])
            elif signals.iloc[i] == -1 and in_position:
                exit_price = df.iloc[i]["close"]
                pnl_pct = ((exit_price - entry_price) / entry_price) * 100
                trades.append(
                    {
                        "entry_time": entry_time,
                        "exit_time": str(df.iloc[i]["timestamp"]),
                        "direction": "LONG",
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "pnl_pct": round(pnl_pct * position_size_pct / 100, 4),
                    }
                )
                in_position = False

        return trades

    def _compute_metrics(
        self, symbol: str, strategy: str, trades: list[dict]
    ) -> BacktestResult:
        if not trades:
            return BacktestResult(
                symbol=symbol,
                strategy=strategy,
                total_return_pct=0.0,
                sharpe_ratio=0.0,
                max_drawdown_pct=0.0,
                win_rate=0.0,
                total_trades=0,
                profit_factor=0.0,
            )

        pnls = [t["pnl_pct"] for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]

        total_return = sum(pnls)
        win_rate = len(wins) / len(pnls) if pnls else 0.0
        gross_profit = sum(wins) if wins else 0.0
        gross_loss = abs(sum(losses)) if losses else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        # Sharpe ratio (annualized, assuming ~8760 hourly trades/year)
        if len(pnls) > 1:
            pnl_arr = np.array(pnls)
            sharpe = (pnl_arr.mean() / pnl_arr.std()) * np.sqrt(365) if pnl_arr.std() > 0 else 0.0
        else:
            sharpe = 0.0

        # Max drawdown
        cumulative = np.cumsum(pnls)
        peak = np.maximum.accumulate(cumulative)
        drawdown = cumulative - peak
        max_dd = abs(drawdown.min()) if len(drawdown) > 0 else 0.0

        return BacktestResult(
            symbol=symbol,
            strategy=strategy,
            total_return_pct=round(total_return, 4),
            sharpe_ratio=round(sharpe, 4),
            max_drawdown_pct=round(max_dd, 4),
            win_rate=round(win_rate, 4),
            total_trades=len(trades),
            profit_factor=round(min(profit_factor, 999.0), 4),
        )


backtest_engine = BacktestEngine()
