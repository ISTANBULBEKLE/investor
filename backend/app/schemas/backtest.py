from pydantic import BaseModel


class BacktestConfig(BaseModel):
    symbol: str
    days: int = 90
    strategy: str = "ensemble"  # "ta", "ml", "ensemble"
    position_size_pct: float = 1.0


class TradeRecord(BaseModel):
    entry_time: str
    exit_time: str
    direction: str
    entry_price: float
    exit_price: float
    pnl_pct: float


class BacktestResult(BaseModel):
    symbol: str
    strategy: str
    total_return_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    win_rate: float
    total_trades: int
    profit_factor: float
