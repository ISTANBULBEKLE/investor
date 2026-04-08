# INVESTOR — System Architecture

## Project Status

| Phase | Status | Description |
|-------|--------|-------------|
| **1: Foundation** | COMPLETE | FastAPI + Next.js 16.2 + better-auth + SQLite + 22 crypto symbols |
| **2: Analysis Engine** | COMPLETE | pandas-ta (150+ indicators) + XGBoost + LSTM + backtesting |
| **3: AI & Sentiment** | COMPLETE | FinBERT + Reddit + Fear & Greed + Ollama LLM |
| **4: Signal Engine** | COMPLETE | Ensemble weighting + APScheduler (30-min) + Resend email alerts |
| **5: Dashboard** | COMPLETE | TradingView charts + portfolio + predictions + settings |
| **6: Deployment** | PARTIAL | Dockerfile exists; Vercel/Railway config + production DB still needed |

**Overall: ~85% complete** — fully functional locally, deployment config remaining.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER (Browser)                          │
│                    http://localhost:3000                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    NEXT.JS 16.2 (Frontend)                      │
│                                                                 │
│  ┌─────────┐ ┌───────────┐ ┌────────────┐ ┌──────────────────┐ │
│  │ Login   │ │ Dashboard │ │ Portfolio  │ │ Predictions      │ │
│  │ (auth)  │ │ (charts)  │ │ (holdings) │ │ (signal history) │ │
│  └─────────┘ └───────────┘ └────────────┘ └──────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Proxy Layer: /api/proxy/[...path] → Backend :8000    │       │
│  └──────────────────────────────────────────────────────┘       │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Auth: better-auth (email/password, session cookies)   │       │
│  └──────────────────────────────────────────────────────┘       │
│  State: Zustand (client) + React Query (server cache)           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP (server-side fetch)
┌──────────────────────────▼──────────────────────────────────────┐
│                   FASTAPI (Backend :8000)                        │
│                                                                 │
│  ┌─────────────────────── API ROUTERS ─────────────────────┐    │
│  │ /health  /api/market  /api/settings  /api/data          │    │
│  │ /api/analysis  /api/signals  /api/portfolio             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────── ANALYSIS SERVICES ───────────────────┐    │
│  │                                                         │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │    │
│  │  │  Technical   │  │     ML       │  │  Sentiment   │  │    │
│  │  │  Analysis    │  │  Predictor   │  │  Aggregator  │  │    │
│  │  │  (pandas-ta) │  │  (XGB+LSTM)  │  │  (FinBERT)   │  │    │
│  │  │  Weight: 35% │  │  Weight: 30% │  │  Weight: 20% │  │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │    │
│  │         │                 │                  │          │    │
│  │         └────────────┬────┴──────────────────┘          │    │
│  │                      ▼                                  │    │
│  │            ┌──────────────────┐    ┌──────────────┐     │    │
│  │            │ Signal Generator │◄───│ LLM Analyzer │     │    │
│  │            │   (Ensemble)     │    │  (Ollama)    │     │    │
│  │            │                  │    │  Weight: 15% │     │    │
│  │            └────────┬─────────┘    └──────────────┘     │    │
│  │                     │                                   │    │
│  │         ┌───────────▼────────────┐                      │    │
│  │         │   Signal Monitor      │                      │    │
│  │         │   (Alert Detection)   │                      │    │
│  │         └───────────┬────────────┘                      │    │
│  │                     │                                   │    │
│  │         ┌───────────▼────────────┐                      │    │
│  │         │   Email Notifier      │                      │    │
│  │         │   (Resend API)        │                      │    │
│  │         └────────────────────────┘                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌──────────────────── SCHEDULER ──────────────────────────┐    │
│  │ APScheduler (AsyncIO)                                   │    │
│  │ • run_analysis_cycle() — every 30 min (all symbols)     │    │
│  │ • update_prices()      — every 5 min                    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────┬──────────────┬──────────────┬─────────────────────────────┘
      │              │              │
┌─────▼────┐  ┌──────▼──┐  ┌───────▼──────┐
│  SQLite  │  │  Cache  │  │ ML Artifacts │
│  (DB)    │  │  (mem)  │  │ (.joblib/.pt)│
└──────────┘  └─────────┘  └──────────────┘
```

---

## Signal Generation Pipeline

The core intelligence — how buy/sell/hold decisions are made:

```
                        ┌───────────────────┐
                        │   Binance API     │
                        │  (OHLCV prices)   │
                        └────────┬──────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   300 hourly candles    │
                    │   (OHLCV DataFrame)    │
                    └──┬──────┬──────┬───────┘
                       │      │      │
          ┌────────────▼┐  ┌──▼──────▼────────┐
          │             │  │                   │
    ┌─────▼──────┐  ┌───▼──▼─────┐  ┌─────────▼──────────┐
    │  TECHNICAL │  │    ML      │  │    SENTIMENT        │
    │  ANALYSIS  │  │ PREDICTION │  │    ANALYSIS         │
    │            │  │            │  │                     │
    │ RSI(14)    │  │ Features:  │  │ ┌─────────────────┐ │
    │ MACD       │  │ 19 cols    │  │ │ FinBERT         │ │
    │ Bollinger  │  │            │  │ │ (news headlines)│ │
    │ SMA 50/200 │  │ XGBoost    │  │ └─────────────────┘ │
    │ EMA 12/26  │  │ (wt: 0.6) │  │ ┌─────────────────┐ │
    │ ATR(14)    │  │    +       │  │ │ Reddit (PRAW)   │ │
    │ OBV        │  │ LSTM       │  │ │ (post titles)   │ │
    │ StochRSI   │  │ (wt: 0.4) │  │ └─────────────────┘ │
    │            │  │            │  │ ┌─────────────────┐ │
    │ Rules:     │  │ 48h seq    │  │ │ Fear & Greed    │ │
    │ RSI<30=Buy │  │ CPU only   │  │ │ (alternative.me)│ │
    │ RSI>70=Sel │  │            │  │ └─────────────────┘ │
    │ MACD cross │  │            │  │                     │
    └─────┬──────┘  └─────┬──────┘  └──────────┬──────────┘
          │               │                    │
     score: -1→+1    score: -1→+1         score: -1→+1
     weight: 0.35    weight: 0.30         weight: 0.20
          │               │                    │
          └───────────────┼────────────────────┘
                          │
                ┌─────────▼──────────┐
                │  ENSEMBLE COMBINER │
                │                    │
                │  weighted_score =  │
                │   TA×0.35 +        │
                │   ML×0.30 +        │    ┌──────────────┐
                │   Sent×0.20 +      │◄───│ LLM (Ollama) │
                │   LLM×0.15        │    │ weight: 0.15 │
                │                    │    │ (optional)   │
                │  SAFETY OVERRIDES: │    └──────────────┘
                │  • TA↔ML disagree  │
                │    → force HOLD    │
                │  • All agree       │
                │    → +15% boost    │
                └─────────┬──────────┘
                          │
                    score mapping:
                   > 0.50 → STRONG_BUY
                   > 0.15 → BUY
                  -0.15–0.15 → HOLD
                  < -0.15 → SELL
                  < -0.50 → STRONG_SELL
                          │
                ┌─────────▼──────────┐
                │  EnsembleSignal    │
                │  {                 │
                │    signal: "BUY",  │
                │    confidence: 72%,│
                │    components: [], │
                │    reasoning: []   │
                │  }                 │
                └─────────┬──────────┘
                          │
              ┌───────────▼───────────┐
              │   Signal Monitor      │
              │                       │
              │ Checks for:           │
              │ • Signal changed      │
              │ • RSI extreme (<30/>70│)
              │ • MACD crossover      │
              │ • F&G extreme         │
              │ • Confidence > 80%    │
              └───────────┬───────────┘
                          │ triggers?
                   ┌──────▼──────┐
                   │ Email Alert │
                   │ (Resend)    │
                   │ 1/sym/hour  │
                   └─────────────┘
```

---

## ML Model Architecture

```
Training Pipeline (scripts/train_models.py):
─────────────────────────────────────────────

  Binance API ──► 365 days hourly OHLCV (8,760 candles per symbol)
                          │
                          ▼
              ┌───────────────────────┐
              │  Feature Engineering  │
              │  (19 features)        │
              │                       │
              │  Price returns:       │
              │  • 1h, 4h, 24h, 7d   │
              │  Volatility:          │
              │  • 24h std, 7d std    │
              │  Volume:              │
              │  • ratio vs 24h SMA   │
              │  Indicators:          │
              │  • RSI, MACD, BB%,    │
              │    SMA ratios, ATR%,  │
              │    Stochastic RSI     │
              │  Time:                │
              │  • hour sin/cos,      │
              │    day-of-week sin/cos│
              │                       │
              │  Target:              │
              │  • price UP/DOWN 24h  │
              └───────────┬───────────┘
                          │
              ┌───────────▼───────────┐
              │   Temporal Split      │
              │   80% train / 20% test│
              │   (NO random shuffle) │
              └─────┬───────────┬─────┘
                    │           │
         ┌──────────▼──┐  ┌────▼──────────┐
         │  XGBoost    │  │  LSTM         │
         │             │  │               │
         │  max_depth=6│  │  2 layers     │
         │  200 trees  │  │  hidden=64    │
         │  lr=0.05    │  │  seq_len=48   │
         │             │  │  Adam, BCE    │
         │  ~58% acc   │  │  early stop   │
         │             │  │               │
         │  .joblib    │  │  ~54% acc     │
         └──────┬──────┘  │               │
                │         │  .pt          │
                │         └───────┬───────┘
                │                 │
         ┌──────▼─────────────────▼──────┐
         │  Ensemble Prediction          │
         │  XGBoost × 0.6 + LSTM × 0.4  │
         │  → direction + confidence     │
         └───────────────────────────────┘

  Trained symbols: BTC, ETH, HBAR, IOTA
  Accuracy range: 54–58% (realistic for crypto)
```

---

## Frontend Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                     Next.js 16.2 App Router                   │
│                                                               │
│  proxy.ts (route protection via better-auth cookies)          │
│                                                               │
│  ┌──────────────────── Pages ────────────────────────┐        │
│  │                                                   │        │
│  │  /login ─────── Login form (email/password)       │        │
│  │                                                   │        │
│  │  /dashboard ─── Signal cards (4 symbols)          │        │
│  │                  TradingView candlestick chart     │        │
│  │                  Metrics grid (RSI, MACD, F&G)     │        │
│  │                  Signal breakdown (component scores)│       │
│  │                                                   │        │
│  │  /portfolio ─── Holdings table (add/edit/delete)  │        │
│  │                  Live P&L calculation              │        │
│  │                  Cost basis tracking               │        │
│  │                                                   │        │
│  │  /predictions ─ Signal history table              │        │
│  │                  Stats (total, avg confidence)     │        │
│  │                  Per-symbol filtering              │        │
│  │                                                   │        │
│  │  /settings ──── Symbol selector (2-10 of 22)     │        │
│  │                  Email alert config               │        │
│  │                  Service status monitor            │        │
│  └───────────────────────────────────────────────────┘        │
│                                                               │
│  ┌──────────── State Management ─────────────────────┐        │
│  │                                                   │        │
│  │  Zustand Store          React Query Cache         │        │
│  │  ├─ selectedSymbol      ├─ ["price", sym]  30s    │        │
│  │  ├─ selectedTimeframe   ├─ ["ohlcv", sym]  60s    │        │
│  │  └─ sidebarCollapsed    ├─ ["signal", sym] 120s   │        │
│  │                         ├─ ["ta", sym]     120s   │        │
│  │                         ├─ ["sentiment"]   300s   │        │
│  │                         ├─ ["services"]    60s    │        │
│  │                         ├─ ["portfolio"]          │        │
│  │                         └─ ["settings"]           │        │
│  └───────────────────────────────────────────────────┘        │
│                                                               │
│  ┌──────────── Components ───────────────────────────┐        │
│  │                                                   │        │
│  │  charts/                 dashboard/               │        │
│  │  ├─ CandlestickChart    ├─ SignalCard             │        │
│  │  └─ IndicatorPanel      ├─ MetricsGrid            │        │
│  │                         └─ SignalBreakdown         │        │
│  │  layout/                                          │        │
│  │  ├─ Sidebar                                       │        │
│  │  └─ Header                                        │        │
│  └───────────────────────────────────────────────────┘        │
└───────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Dashboard Load

What happens when a user opens the dashboard:

```
  Browser                  Next.js                  FastAPI                Binance
    │                        │                        │                      │
    │─── GET /dashboard ────►│                        │                      │
    │◄── HTML + JS ──────────│                        │                      │
    │                        │                        │                      │
    │  React hydrates, hooks fire:                    │                      │
    │                        │                        │                      │
    │─ GET /api/proxy/api/market/BTC/price ──────────►│── GET /ticker/24hr──►│
    │─ GET /api/proxy/api/market/ETH/price ──────────►│── GET /ticker/24hr──►│
    │─ GET /api/proxy/api/market/HBAR/price ─────────►│── GET /ticker/24hr──►│
    │─ GET /api/proxy/api/market/IOTA/price ─────────►│── GET /ticker/24hr──►│
    │◄── { price, 24h change, volume } ──────────────│◄── JSON ──────────────│
    │                        │                        │                      │
    │─ GET /api/proxy/api/signals/BTC ───────────────►│                      │
    │  (only selected symbol)│                        │─► TA service         │
    │                        │                        │─► ML predictor       │
    │                        │                        │─► Sentiment agg      │
    │                        │                        │   └─► Fear & Greed   │
    │                        │                        │─► Ensemble combiner  │
    │◄── { signal, confidence, components } ─────────│                      │
    │                        │                        │                      │
    │─ GET /api/proxy/api/market/BTC/ohlcv ──────────►│── GET /klines ──────►│
    │◄── { 200 candles } ────────────────────────────│◄── OHLCV array ──────│
    │                        │                        │                      │
    │  Renders:              │                        │                      │
    │  • 4 price cards       │                        │                      │
    │  • Candlestick chart   │                        │                      │
    │  • Metrics grid        │                        │                      │
    │  • Signal breakdown    │                        │                      │
```

---

## Scheduled Analysis Cycle

Runs every 30 minutes automatically:

```
  APScheduler                    Signal Generator              External
      │                              │                           │
      │── run_analysis_cycle() ─────►│                           │
      │   for each symbol:           │                           │
      │                              │── get OHLCV ─────────────►│ Binance
      │                              │◄── 300 candles ───────────│
      │                              │                           │
      │                              │── TA service              │
      │                              │   (pandas-ta indicators)  │
      │                              │                           │
      │                              │── ML predictor            │
      │                              │   (XGBoost + LSTM)        │
      │                              │                           │
      │                              │── Sentiment aggregator    │
      │                              │   ├── Fear & Greed ──────►│ alternative.me
      │                              │   ├── News headlines ────►│ CoinGecko
      │                              │   └── Reddit posts ──────►│ Reddit API
      │                              │                           │
      │                              │── LLM analyzer ──────────►│ Ollama
      │                              │   (if available)          │ (localhost)
      │                              │                           │
      │                              │── Ensemble combine        │
      │                              │── Store in DB             │
      │                              │                           │
      │◄── EnsembleSignal ──────────│                           │
      │                              │                           │
      │── Signal Monitor             │                           │
      │   check for alert triggers   │                           │
      │                              │                           │
      │── Email Notifier (if triggered)                          │
      │   └── Resend API ──────────────────────────────────────►│ Resend
      │       (rate: 1/symbol/hour)                              │
      │                              │                           │
      │── sleep 2s, next symbol      │                           │
```

---

## Database Schema

```
  ┌──────────────────┐     ┌───────────────────────┐
  │  user_settings   │     │     ohlcv_data         │
  ├──────────────────┤     ├───────────────────────┤
  │  id              │     │  id                   │
  │  symbols (JSON)  │     │  symbol    (indexed)  │
  │  email           │     │  timestamp (indexed)  │
  │  alert_prefs     │     │  open, high, low      │
  │  created_at      │     │  close, volume        │
  │  updated_at      │     │  timeframe, source    │
  └──────────────────┘     └───────────────────────┘

  ┌───────────────────────┐     ┌──────────────────────┐
  │  analysis_results     │     │  alert_logs          │
  ├───────────────────────┤     ├──────────────────────┤
  │  id                   │     │  id                  │
  │  symbol    (indexed)  │     │  symbol   (indexed)  │
  │  timestamp (indexed)  │     │  alert_type          │
  │  signal (enum)        │     │  message             │
  │  confidence           │     │  sent_at             │
  │  technical_score      │     │  email_sent          │
  │  ml_score             │     └──────────────────────┘
  │  sentiment_score      │
  │  llm_summary          │     ┌──────────────────────┐
  │  raw_data (JSON)      │     │  holdings            │
  └───────────────────────┘     ├──────────────────────┤
                                │  id                  │
  ┌───────────────────────┐     │  symbol   (indexed)  │
  │  prediction_history   │     │  amount              │
  ├───────────────────────┤     │  avg_buy_price       │
  │  id                   │     │  updated_at          │
  │  symbol    (indexed)  │     └──────────────────────┘
  │  predicted_signal     │
  │  predicted_at         │     ┌──────────────────────┐
  │  actual_outcome       │     │  auth.db (separate)  │
  │  accuracy_score       │     ├──────────────────────┤
  │  evaluated_at         │     │  user               │
  └───────────────────────┘     │  session            │
                                │  account            │
                                │  verification       │
                                └──────────────────────┘
```

---

## API Endpoint Map

```
  GET  /health                           → System health + DB status

  GET  /api/market/{sym}/price           → Live ticker from Binance
  GET  /api/market/{sym}/ohlcv           → Live OHLCV candles

  POST /api/data/{sym}/backfill          → Trigger historical data fetch
  GET  /api/data/{sym}/ohlcv             → Query stored candles
  GET  /api/data/{sym}/count             → Count stored data points

  GET  /api/settings                     → User settings (symbols, email)
  PUT  /api/settings                     → Update settings

  GET  /api/analysis/{sym}/technical     → Technical analysis signal
  GET  /api/analysis/{sym}/ml            → ML prediction signal
  GET  /api/analysis/{sym}/sentiment     → Sentiment analysis
  GET  /api/analysis/{sym}/llm-summary   → LLM narrative (Ollama)
  POST /api/analysis/backtest            → Run backtest strategy
  GET  /api/analysis/services/status     → External service health

  GET  /api/signals/{sym}                → Full ensemble signal
  GET  /api/signals/{sym}/history        → Signal history (30d)

  GET  /api/portfolio                    → All holdings
  POST /api/portfolio                    → Add/update holding
  DELETE /api/portfolio/{sym}            → Delete holding
```

---

## Technology Stack

```
  FRONTEND                          BACKEND                        EXTERNAL
  ────────                          ───────                        ────────
  Next.js 16.2                      FastAPI                        Binance API
  React 19                          Python 3.12+                   CoinGecko API
  TypeScript                        SQLAlchemy (async)             Alternative.me
  Tailwind CSS v4                   pandas + pandas-ta             Reddit API
  TradingView Charts v5             XGBoost + PyTorch LSTM         Ollama (local)
  better-auth v1.6                  scikit-learn                   Resend (email)
  React Query v5                    HuggingFace Transformers
  Zustand v5                        APScheduler
  Recharts v3                       PRAW (Reddit)
                                    LangChain
```

---

## File Tree (key files)

```
investor/
├── ARCHITECTURE.md              ← this file
├── INVESTOR_BUSINESS_PLAN.md    ← full plan with research
├── START.md                     ← setup and run commands
├── Makefile                     ← 13 commands (start/stop/test/train)
├── .env.example                 ← environment variable template
│
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI app + scheduler lifecycle
│   │   ├── database.py          ← async SQLAlchemy engine
│   │   ├── config/
│   │   │   ├── settings.py      ← env-based config (22 settings)
│   │   │   └── symbols.py       ← 22 crypto symbol mappings
│   │   ├── models/
│   │   │   ├── db_models.py     ← 6 ORM tables
│   │   │   ├── feature_engineering.py  ← 19 ML features
│   │   │   ├── xgboost_model.py       ← XGBoost train/predict/save
│   │   │   ├── lstm_model.py          ← LSTM train/predict/save
│   │   │   ├── training_pipeline.py   ← training orchestration
│   │   │   └── artifacts/             ← saved .joblib + .pt files
│   │   ├── routers/             ← 7 API routers (23 endpoints)
│   │   ├── services/            ← 13 business logic services
│   │   └── schemas/             ← 9 Pydantic schema files
│   ├── tests/                   ← 10 test files (49 tests)
│   ├── scripts/train_models.py  ← CLI model trainer
│   ├── requirements.txt         ← 18 Python dependencies
│   └── Dockerfile               ← production container
│
├── frontend/
│   ├── app/                     ← 5 pages + 2 API routes
│   ├── components/              ← 7 React components
│   ├── lib/                     ← 7 utilities + hooks + store
│   ├── proxy.ts                 ← route protection
│   ├── scripts/create-user.ts   ← admin user seed
│   └── package.json             ← 10 dependencies
```
