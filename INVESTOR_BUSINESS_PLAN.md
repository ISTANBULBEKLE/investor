# INVESTOR — AI-Powered Crypto Investment Prediction Tool

## Business Plan & Technical Implementation Guide

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Tech Stack — Research Findings & Recommendations](#2-tech-stack)
3. [Architecture Overview](#3-architecture-overview)
4. [Project Structure](#4-project-structure)
5. [Phase 1: Foundation (Weeks 1–2)](#5-phase-1-foundation)
6. [Phase 2: Analysis Engine (Weeks 3–4)](#6-phase-2-analysis-engine)
7. [Phase 3: AI & Sentiment (Weeks 5–6)](#7-phase-3-ai--sentiment)
8. [Phase 4: Signal Engine & Notifications (Weeks 7–8)](#8-phase-4-signal-engine--notifications)
9. [Phase 5: Dashboard & Visualization (Weeks 9–10)](#9-phase-5-dashboard--visualization)
10. [Phase 6: Deployment & Polish (Weeks 11–12)](#10-phase-6-deployment--polish)
11. [Signal Generation Strategy](#11-signal-generation-strategy)
12. [Risk Management & Realistic Expectations](#12-risk-management--realistic-expectations)
13. [Cost Analysis](#13-cost-analysis)
14. [Risk Factors & Mitigations](#14-risk-factors--mitigations)

---

## 1. Executive Summary

**INVESTOR** is a personal crypto investment prediction tool designed to monitor multiple configurable cryptocurrencies (default: BTC, ETH, HBAR, IOTA), generate AI-powered buy/sell/hold signals, and send email alerts for immediate trading decisions.

**Core Capabilities:**
- Real-time price monitoring via Binance API
- Technical analysis using 150+ indicators (pandas-ta)
- ML-based price direction prediction (XGBoost + LSTM ensemble)
- Sentiment analysis (FinBERT, Reddit, Fear & Greed Index)
- LLM-powered analysis summaries (Ollama with Llama 3.3/Mistral)
- Email notifications for actionable signals (Resend)
- Vercel-deployed dashboard with TradingView charts

**Target User:** Single user managing multiple crypto positions (default 4: BTC, ETH, HBAR, IOTA), seeking data-driven buy/sell decisions with continuous monitoring.

---

## 2. Tech Stack

### 2.1 Frontend

| Technology | Version | Purpose | Free Tier |
|------------|---------|---------|-----------|
| **Next.js** | 16.2 (March 2026) | App Router, Server Components, Turbopack | Open source |
| **TradingView Lightweight Charts** | Latest | Candlestick/OHLCV charts (~20KB) | Open source |
| **Recharts** | Latest | Dashboard charts (pie, line, bar) | Open source |
| **Zustand** | Latest | Client-side state (~1.2KB) | Open source |
| **TanStack React Query** | v5 | Server state management, caching | Open source |
| **better-auth** | v1.6 | Email/password authentication (session-based) | Open source |
| **Tailwind CSS** | v4 | Utility-first styling | Open source |
| **Vercel** | Hobby plan | Hosting: 100GB bandwidth, 150K function invocations/mo | Free |

**Why Next.js 16.2:** Released March 18, 2026. ~400% faster dev startup with Turbopack. React Compiler support is stable. App Router fully mature. Server Components reduce bundle size for data-heavy pages.

**Why TradingView Lightweight Charts:** Most specialized for financial/crypto charting at only ~20KB. Professional candlestick rendering with volume overlays. Recharts is used only for simpler dashboard components (pie charts, accuracy graphs).

**Why Zustand over Redux:** ~1.2KB vs ~11KB footprint. Minimal boilerplate, SSR-friendly. Combined with TanStack React Query — Zustand for client state (UI preferences), React Query for server state (prices, signals).

### 2.2 Backend (Python)

| Technology | Version | Purpose | Free Tier |
|------------|---------|---------|-----------|
| **FastAPI** | 0.115+ | Async API framework (20K+ req/s) | Open source |
| **pandas-ta** | Latest | 150+ technical indicators | Open source |
| **scikit-learn** | Latest | XGBoost/LightGBM classification | Open source |
| **PyTorch** | Latest (CPU) | LSTM time series prediction | Open source |
| **Prophet** | Latest | Trend forecasting | Open source |
| **Hugging Face Transformers** | Latest | FinBERT sentiment analysis | Open source |
| **Ollama** | 0.5+ | Local LLM hosting (Llama 3.3 / Mistral) | Free ($0/token) |
| **LangChain** | Latest | LLM orchestration | Open source |
| **APScheduler** | Latest | Periodic analysis scheduling | Open source |
| **CCXT** | Latest | Unified crypto exchange API (100+ exchanges) | Open source |

**Why FastAPI over Flask:** 5-10x faster performance (15K-20K req/s vs 2K-3K). Native async/await for real-time data feeds. Built-in WebSocket support. Auto-generated API documentation (Swagger/ReDoc). 38% of Python developers use FastAPI as of 2025.

**Why PyTorch over TensorFlow:** Lighter install for CPU-only LSTM models. More Pythonic API. Better for small research-style models. Dynamic computation graphs simplify debugging.

### 2.3 Data Sources (All Free)

| Source | Data Type | Free Limits | Auth Required |
|--------|-----------|-------------|---------------|
| **Binance API** | Real-time OHLCV, order book, tickers | Unlimited public endpoints | No |
| **CoinGecko API** | Historical data, market info | 30 calls/min with API key | Optional |
| **CoinMarketCap API** | Aggregated market data | 10K credits/month, 30 req/min | Yes (free key) |
| **Alternative.me** | Fear & Greed Index | Unlimited | No |
| **Reddit (PRAW)** | Sentiment from crypto subreddits | Free developer app | Yes (free) |
| **CoinCap** | Real-time WebSocket feeds | Unlimited | No |
| **CryptoCompare** | Historical data | ~1000s calls/day | Yes (free key) |

**Primary Strategy:** Binance for real-time data (no auth, unlimited), CoinGecko for historical backfill, Alternative.me for Fear & Greed, Reddit for retail sentiment.

### 2.4 Infrastructure & Services

| Service | Purpose | Free Tier Limits |
|---------|---------|-----------------|
| **Vercel** | Frontend hosting | 100GB bandwidth, 150K invocations, 6K build min/mo |
| **Railway** | Backend hosting | $5 credit/mo, 512MB RAM, 500 hrs/mo |
| **Neon PostgreSQL** | Database (production) | 0.5GB storage, 10 branches |
| **Upstash Redis** | Caching, rate limiting | 10K commands/day |
| **Resend** | Email notifications | 3,000 emails/month (100/day) |

**Alternative Backend Hosts:**
- **Render:** Persistent free tier, 15-min sleep after inactivity (30-60s cold starts)
- **Fly.io:** 3 VMs at 256MB always-on (no cold starts) — best for scheduled analysis

### 2.5 Email Notification Comparison

| Service | Free Limit | Status (2026) | Recommendation |
|---------|-----------|---------------|----------------|
| **Resend** | 3,000/month | Active | **Primary choice** — developer-friendly, React Email support |
| **Brevo** | 9,000/month (300/day) | Active | Best volume on free tier |
| **SendGrid** | 60-day trial only | Free tier retired May 2025 | Not recommended |
| **Nodemailer + Gmail** | 500/day | Works | Development/testing only |

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    VERCEL (Frontend)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Next.js 16.2 App                                    │   │
│  │  ├── Dashboard (TradingView Charts + Signal Cards)   │   │
│  │  ├── Portfolio (Holdings + P&L)                      │   │
│  │  ├── Predictions (History + Accuracy)                │   │
│  │  ├── Settings (Crypto Selection + Alerts)            │   │
│  │  └── API Proxy Routes → Python Backend               │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS (server-side fetch)
┌──────────────────────────▼──────────────────────────────────┐
│                 RAILWAY (Python Backend)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastAPI Application                                 │   │
│  │  ├── Data Fetcher (Binance + CoinGecko + CCXT)       │   │
│  │  ├── Technical Analysis (pandas-ta: RSI, MACD, BB)   │   │
│  │  ├── ML Predictor (XGBoost + LSTM ensemble)          │   │
│  │  ├── Sentiment Analyzer (FinBERT + Reddit + F&G)     │   │
│  │  ├── LLM Analyzer (Ollama via LangChain)             │   │
│  │  ├── Signal Generator (ensemble combiner)            │   │
│  │  ├── Email Notifier (Resend)                         │   │
│  │  ├── APScheduler (30-min analysis cycles)            │   │
│  │  └── WebSocket (real-time price relay)               │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────┬────────────┬────────────┬────────────────────────┘
           │            │            │
    ┌──────▼──┐  ┌──────▼──┐  ┌─────▼─────┐
    │ SQLite/ │  │ Upstash │  │  Resend   │
    │  Neon   │  │  Redis  │  │  (Email)  │
    │  (DB)   │  │ (Cache) │  │           │
    └─────────┘  └─────────┘  └───────────┘
```

**API Communication Pattern:** The Next.js frontend proxies all API requests through its own API routes (`/api/proxy/[...path]`). This avoids CORS issues and keeps the backend URL private. In production, Vercel server-side fetch calls the Railway backend URL stored in an environment variable.

**Configurable Crypto Selection:** The system defaults to BTC, ETH, HBAR, and IOTA but the user can configure 2–10 cryptocurrencies in `UserSettings`. Every service accepts symbol parameters rather than hardcoding tickers. A mapping config translates symbols to API-specific identifiers:

```python
SYMBOL_CONFIG = {
    "BTC": {"binance": "BTCUSDT", "coingecko": "bitcoin", "subreddits": ["bitcoin"]},
    "ETH": {"binance": "ETHUSDT", "coingecko": "ethereum", "subreddits": ["ethereum"]},
    "SOL": {"binance": "SOLUSDT", "coingecko": "solana", "subreddits": ["solana"]},
    # ... top 20 supported cryptos
}
```

---

## 4. Project Structure

```
investor/
├── frontend/                          # Next.js 16.2 Application
│   ├── app/
│   │   ├── layout.tsx                 # Root layout (dark theme, providers)
│   │   ├── page.tsx                   # Landing → redirect to dashboard
│   │   ├── login/page.tsx             # Login form
│   │   ├── dashboard/
│   │   │   ├── layout.tsx             # Dashboard layout with sidebar
│   │   │   └── page.tsx               # Main dashboard (charts + signals)
│   │   ├── portfolio/page.tsx         # Portfolio tracker (holdings + P&L)
│   │   ├── predictions/page.tsx       # Prediction history & accuracy
│   │   ├── settings/page.tsx          # Crypto selection + alert config
│   │   └── api/
│   │       ├── auth/[...all]/route.ts       # better-auth handler
│   │       └── proxy/[...path]/route.ts     # Backend API proxy
│   ├── components/
│   │   ├── ui/                        # Base components (Button, Card, Badge...)
│   │   ├── layout/                    # Sidebar, Header
│   │   ├── charts/                    # CandlestickChart, IndicatorPanel
│   │   ├── dashboard/                 # SignalCard, MetricsGrid, SignalBreakdown
│   │   ├── portfolio/                 # HoldingsTable, PortfolioSummary
│   │   └── predictions/              # AccuracyChart, PredictionTable
│   ├── lib/
│   │   ├── api.ts                     # Typed API client
│   │   ├── auth.ts                    # better-auth server config
│   │   ├── auth-client.ts             # better-auth React client
│   │   ├── providers.tsx              # Combined providers
│   │   ├── chart-utils.ts            # Data transformation for charts
│   │   ├── hooks/                     # React Query hooks (useSignal, useOHLCV...)
│   │   └── store/                     # Zustand store (app-store.ts)
│   ├── proxy.ts                       # Route protection (Next.js 16.2)
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── package.json
│   └── __tests__/                     # Component tests
│
├── backend/                           # Python FastAPI Application
│   ├── app/
│   │   ├── main.py                    # FastAPI entry, CORS, lifespan
│   │   ├── database.py                # SQLAlchemy async engine
│   │   ├── config/
│   │   │   ├── settings.py            # Pydantic BaseSettings (.env)
│   │   │   └── symbols.py            # Crypto symbol mappings
│   │   ├── models/
│   │   │   ├── db_models.py           # ORM models (UserSettings, OHLCVData, etc.)
│   │   │   ├── feature_engineering.py # Feature extraction for ML
│   │   │   ├── xgboost_model.py       # XGBoost classifier
│   │   │   ├── lstm_model.py          # PyTorch LSTM predictor
│   │   │   ├── training_pipeline.py   # Model training orchestrator
│   │   │   └── artifacts/             # Saved model files
│   │   ├── routers/
│   │   │   ├── health.py              # Health check endpoint
│   │   │   ├── market.py              # Price and OHLCV endpoints
│   │   │   ├── analysis.py            # TA, ML, sentiment endpoints
│   │   │   ├── signals.py             # Ensemble signal endpoints
│   │   │   ├── portfolio.py           # Portfolio management
│   │   │   ├── predictions.py         # Prediction history & accuracy
│   │   │   ├── backtest.py            # Backtesting endpoints
│   │   │   ├── settings.py            # User settings & alerts
│   │   │   ├── data.py                # Data backfill endpoints
│   │   │   └── websocket.py           # Real-time price WebSocket
│   │   ├── services/
│   │   │   ├── data_fetcher.py        # Binance + CoinGecko clients
│   │   │   ├── technical_analysis.py  # pandas-ta indicator computation
│   │   │   ├── ml_predictor.py        # ML model inference service
│   │   │   ├── sentiment_analyzer.py  # FinBERT sentiment scoring
│   │   │   ├── news_fetcher.py        # Crypto news headlines
│   │   │   ├── reddit_scraper.py      # Reddit sentiment via PRAW
│   │   │   ├── fear_greed.py          # Fear & Greed Index client
│   │   │   ├── sentiment_aggregator.py # Combined sentiment score
│   │   │   ├── llm_analyzer.py        # Ollama LLM integration
│   │   │   ├── llm_prompts.py         # Prompt templates
│   │   │   ├── llm_chain.py           # LangChain orchestration
│   │   │   ├── signal_generator.py    # Ensemble signal combiner
│   │   │   ├── signal_monitor.py      # Alert trigger detection
│   │   │   ├── email_notifier.py      # Resend email service
│   │   │   ├── email_templates.py     # HTML email templates
│   │   │   ├── scheduler.py           # APScheduler integration
│   │   │   ├── backtester.py          # Strategy backtesting engine
│   │   │   ├── cache.py               # Upstash Redis cache
│   │   │   └── health_checker.py      # Service availability checker
│   │   └── schemas/                   # Pydantic v2 models
│   │       ├── common.py              # SignalEnum, TimeframeEnum
│   │       ├── market.py              # OHLCVResponse, PriceResponse
│   │       ├── analysis.py            # AnalysisResultResponse
│   │       ├── technical.py           # TAIndicators, TASignal
│   │       ├── prediction.py          # MLSignal, MLPrediction
│   │       ├── sentiment.py           # SentimentScore, CryptoSentiment
│   │       ├── signal.py              # EnsembleSignal
│   │       ├── backtest.py            # BacktestConfig, BacktestResult
│   │       └── settings.py            # UserSettings, AlertConfig
│   ├── scripts/
│   │   └── train_models.py            # Model training CLI
│   ├── tests/                         # pytest + pytest-asyncio
│   ├── alembic/                       # Database migrations
│   ├── alembic.ini
│   ├── requirements.txt
│   └── Dockerfile
│
├── .env.example                       # All environment variables
├── .gitignore
├── Makefile                           # Dev commands
├── INVESTOR_BUSINESS_PLAN.md          # This file
└── README.md
```

---

## 5. Phase 1: Foundation (Weeks 1–2)

### Week 1: Backend Skeleton

**Task 1.1 — Monorepo Initialization**
- Create root directory structure
- `.gitignore`: Python venvs, node_modules, .env, __pycache__, .next, SQLite files, model artifacts
- `Makefile`: commands for `backend-dev`, `frontend-dev`, `test`, `lint`
- `.env.example`: all required environment variables with descriptions

**Task 1.2 — FastAPI Backend Skeleton**
- `backend/app/main.py`: FastAPI app, CORS middleware, lifespan handler
- `backend/app/config/settings.py`: Pydantic `BaseSettings` loading from `.env`
  - Fields: `DATABASE_URL`, `BINANCE_BASE_URL`, `COINGECKO_API_KEY`, `RESEND_API_KEY`, `REDIS_URL`, `DEFAULT_SYMBOLS` (default: `["BTC", "ETH", "HBAR", "IOTA"]`), `ANALYSIS_INTERVAL_MINUTES` (default: 30)
- `backend/app/database.py`: SQLAlchemy async engine for SQLite (`aiosqlite`)
- `backend/app/models/db_models.py`: ORM models:
  - `UserSettings`: symbols (JSON), email, alert_preferences (JSON)
  - `OHLCVData`: symbol, timestamp, OHLCV, timeframe, source
  - `AnalysisResult`: symbol, timestamp, signal, confidence, component scores, llm_summary
  - `AlertLog`: symbol, alert_type, message, sent_at, email_sent
  - `PredictionHistory`: symbol, predicted_signal, actual_outcome, accuracy_score
- Placeholder routers: `/health`, `/api/market/{symbol}/price`, `/api/settings`
- `requirements.txt`: fastapi, uvicorn, sqlalchemy[asyncio], aiosqlite, pydantic-settings, httpx

**Task 1.3 — Database Migrations**
- Alembic setup with initial migration creating all tables
- Decision: Alembic over raw SQL for reproducible schema changes

**Task 1.4 — Backend Tests**
- `conftest.py` with async test client fixture (in-memory SQLite)
- Tests for health and settings endpoints

### Week 2: Frontend & Data Fetching

**Task 1.5 — Next.js 16.2 Frontend**
- `package.json` dependencies: next@16.2, react, zustand, @tanstack/react-query, tailwindcss, better-auth, better-sqlite3, recharts, lightweight-charts
- Dark theme by default (crypto standard)
- Custom color palette: buy (green), sell (red), hold (amber)
- Root layout with providers, dashboard shell with sidebar navigation
- Pages: Dashboard, Portfolio, Predictions, Settings (all placeholder)

**Task 1.6 — better-auth (Single User)**
- better-auth with `emailAndPassword` enabled, SQLite database (`auth.db`)
- Session-based auth (cookie), `nextCookies()` plugin for Server Actions
- `proxy.ts` (Next.js 16.2 convention, replaces middleware.ts) protecting all routes
- `scripts/create-user.ts` seed script for initial admin account

**Task 1.7 — Data Fetcher Service**
- `BinanceClient`: async methods for `get_current_price()`, `get_ohlcv()`, `get_24h_ticker()` via httpx
- `CoinGeckoClient`: `get_historical_data()`, `get_market_data()`
- Symbol mapping: "BTC" → "BTCUSDT" (Binance) / "bitcoin" (CoinGecko)
- In-memory cache with TTL for Phase 1 (Redis comes in Phase 4)

**Task 1.8 — Frontend API Proxy**
- Catch-all route `api/proxy/[...path]/route.ts` proxying to Python backend
- Keeps backend URL secret from browser, avoids CORS entirely

**Task 1.9 — Integration Smoke Test**
- Settings page: select 2 cryptos from top 20 dropdown
- Dashboard: display current prices, 24h change, volume for both cryptos

### Phase 1 Definition of Done
- [ ] Backend starts, `/health` returns 200
- [ ] Database tables created via Alembic migration
- [ ] User can log in to frontend
- [ ] Settings page allows selecting 2 cryptocurrencies
- [ ] Dashboard shows live prices for both configured cryptos from Binance
- [ ] All routes return Pydantic-validated JSON
- [ ] 5+ passing backend tests

---

## 6. Phase 2: Analysis Engine (Weeks 3–4)

### Week 3: Technical Analysis & ML Models

**Task 2.1 — Historical Data Pipeline**
- `backfill_historical(symbol, days=365)`: fetches 1-year hourly candles from CoinGecko
- ~8,760 rows per symbol (well within SQLite/Neon limits)
- Runs once on setup, then incremental updates

**Task 2.2 — Technical Analysis Service**
- `TechnicalAnalysisService` using pandas-ta:
  - **Indicators computed**: RSI(14), MACD(12,26,9), Bollinger Bands(20,2), SMA(50), SMA(200), EMA(12), EMA(26), Stochastic RSI, ATR(14), OBV
  - **Signal rules**:
    - STRONG_BUY: RSI < 30 AND price below lower BB AND MACD bullish crossover
    - BUY: RSI < 40 AND MACD bullish
    - SELL: RSI > 60 AND MACD bearish
    - STRONG_SELL: RSI > 70 AND price above upper BB AND MACD bearish crossover
    - HOLD: otherwise
  - Returns composite technical score (-1.0 to +1.0)
- Endpoint: `GET /api/analysis/{symbol}/technical`

**Task 2.3 — ML Model Training Pipeline**
- **Feature Engineering**: lagged returns (1h, 4h, 24h, 7d), volatility measures, TA indicator values, volume profiles, day-of-week, hour-of-day
- **Target**: binary classification (price up/down after 24 hours)
- **XGBoost Model**:
  - Walk-forward cross-validation (no random shuffle — prevents data leakage)
  - Hyperparameters: max_depth=6, n_estimators=200, learning_rate=0.05
  - Saves via joblib
- **LSTM Model (PyTorch)**:
  - 2 layers, hidden_size=64, sequence_length=48 (48 hours)
  - Input: normalized OHLCV + key TA indicators (10-15 features)
  - Adam optimizer, BCELoss, early stopping
  - CPU-only (training: 5-15 min)

**Task 2.4 — ML Prediction Service**
- Loads trained models at startup
- Ensemble: XGBoost weight 0.6, LSTM weight 0.4 (XGBoost more reliable on tabular data)
- Endpoint: `GET /api/analysis/{symbol}/ml`

### Week 4: Backtesting Framework

**Task 2.5 — Backtesting Engine**
- Simulates trading based on signals over historical data
- Metrics: total return, Sharpe ratio, max drawdown, win rate, profit factor
- Position sizing: 1% of portfolio per trade (configurable)
- Supports TA-only, ML-only, and ensemble strategies
- Endpoint: `POST /api/backtest`

**Task 2.6 — Model Training Script**
- `scripts/train_models.py`: backfill → features → train → backtest → save artifacts
- Runs manually or weekly via scheduled job

### Phase 2 Definition of Done
- [ ] 1-year hourly OHLCV data stored for both cryptos
- [ ] TA endpoint returns all indicator values and signal
- [ ] XGBoost and LSTM models trained and saved
- [ ] ML prediction endpoint returns forecast with confidence
- [ ] Backtester reports metrics for TA-only and ML-only strategies
- [ ] 10+ passing analysis tests

---

## 7. Phase 3: AI & Sentiment (Weeks 5–6)

### Week 5: Sentiment Analysis Pipeline

**Task 3.1 — FinBERT Sentiment Analyzer**
- Loads `ProsusAI/finbert` from Hugging Face (~400MB, cached after first download)
- Runs on CPU: batch of 20 headlines in 2-5 seconds
- Methods: `analyze_text()`, `analyze_batch()`, `get_crypto_sentiment()`

**Task 3.2 — News Data Sources**
- Fetch latest 20 headlines per symbol from CoinGecko news / CryptoPanic
- HTML/text cleaning, 15-minute cache

**Task 3.3 — Reddit Sentiment (PRAW)**
- Fetch top 25 posts from configured subreddits (r/cryptocurrency, r/bitcoin, r/ethereum)
- Filter by symbol mention, extract title + first 200 chars
- Feed to FinBERT for scoring
- Returns bullish/bearish ratio, average sentiment, post volume
- Requires free Reddit developer app (reddit.com/prefs/apps)

**Task 3.4 — Fear & Greed Index**
- Free JSON API: `https://api.alternative.me/fng/?limit=30`
- No auth required
- Maps to signal: < 25 = bullish (contrarian), > 75 = bearish (contrarian)

**Task 3.5 — Unified Sentiment Service**
- Weighted combination: News 0.4, Reddit 0.3, Fear & Greed 0.3
- Returns composite sentiment score (-1.0 to +1.0)
- Endpoint: `GET /api/analysis/{symbol}/sentiment`

### Week 6: LLM Integration

**Task 3.6 — Ollama LLM Setup**
- Connects to local Ollama (`http://localhost:11434`)
- Uses Llama 3.3 8B or Mistral 7B (configurable)
- `analyze_signals()`: interprets combined TA + ML + sentiment, generates narrative summary
- `interpret_news()`: summarizes market-moving headlines
- The LLM is the "explainability layer" — it interprets signals, doesn't generate them
- Bad LLM output degrades explanations but NOT signal quality

**Task 3.7 — LangChain Orchestration**
- Chain: retrieve analysis → format prompt → call Ollama → parse response
- `StructuredOutputParser` for reliable JSON extraction
- Retry logic for malformed LLM output
- Endpoint: `GET /api/analysis/{symbol}/llm-summary`

**Task 3.8 — Graceful Degradation (Critical)**
- Every service works independently with try/except and fallbacks
- Ollama down → system still produces signals from TA + ML + sentiment
- Reddit down → sentiment uses only news + Fear & Greed
- Health checker monitors all service availability

### Phase 3 Definition of Done
- [ ] FinBERT scores crypto headlines in < 5 seconds
- [ ] Reddit scraper fetches and scores posts
- [ ] Fear & Greed Index fetched and mapped to signal
- [ ] Sentiment aggregator produces composite score
- [ ] Ollama produces narrative analysis when running
- [ ] System works when Ollama or Reddit is offline
- [ ] 8+ passing sentiment/LLM tests

---

## 8. Phase 4: Signal Engine & Notifications (Weeks 7–8)

### Week 7: Ensemble Signal Generator

**Task 4.1 — Signal Generator (Core of the System)**
- `generate_signal(symbol) → EnsembleSignal`:
  1. Call Technical Analysis → TA signal + score
  2. Call ML Predictor → ML signal + confidence
  3. Call Sentiment Aggregator → sentiment score
  4. Call LLM Analyzer → narrative (optional, non-blocking)
  5. Combine with weights:
     - **Technical Analysis: 0.35**
     - **ML Prediction: 0.30**
     - **Sentiment: 0.20**
     - **LLM signal: 0.15** (if available)
  6. Map composite score to signal:
     - Score > 0.6 → STRONG_BUY
     - Score 0.2 to 0.6 → BUY
     - Score -0.2 to 0.2 → HOLD
     - Score -0.6 to -0.2 → SELL
     - Score < -0.6 → STRONG_SELL
  7. Store in `AnalysisResult` table
- **Safety overrides**:
  - Complete TA/ML disagreement (STRONG_SELL vs STRONG_BUY) → force HOLD
  - All 3 non-LLM sources agree → boost confidence by 15%
- Endpoints: `GET /api/signals/{symbol}`, `GET /api/signals/{symbol}/history`

**Task 4.2 — Signal Change Detection**
- Alert triggers:
  - Signal direction change (e.g., HOLD → BUY)
  - RSI extreme entry (crosses < 30 or > 70)
  - MACD crossover (bullish or bearish)
  - Price drop > 5% in 24h
  - Fear & Greed extreme (< 20 or > 80)
  - Ensemble confidence spike (> 0.8)

**Task 4.3 — APScheduler Integration**
- `run_analysis_cycle()`: every 30 minutes (configurable)
  - For each symbol: fetch data → generate signal → check alerts → queue emails
- `update_prices()`: every 5 minutes — store latest for charts
- `evaluate_predictions()`: daily — compare past predictions with outcomes
- Integrated into FastAPI lifespan (start/stop with app)

### Week 8: Email Notifications

**Task 4.4 — Email Notification Service (Resend)**
- `send_alert(alert, signal)`: formatted HTML email with:
  - Signal change summary
  - Key indicator values
  - Confidence score
  - Recommended action
  - Link to dashboard
- Rate limiting: max 1 email per symbol per hour (prevents spam in volatile markets)
- Tracks sent emails in `AlertLog` table
- HTML templates with inline CSS (Python string templates — no React Email dependency)

**Task 4.5 — Upstash Redis Integration**
- Replace in-memory cache:
  - Price data cache (TTL: 60s)
  - Analysis results cache (TTL: 300s)
  - API rate limit tracking (CoinGecko, Reddit)
  - Email rate limit tracking

**Task 4.6 — Alert Configuration**
- `PUT /api/settings/alerts`: configure alert types, email, quiet hours
- `GET /api/settings/alerts`: current configuration

### Phase 4 Definition of Done
- [ ] Ensemble signal combines all 4 sources with confidence
- [ ] Signal history stored for both cryptos
- [ ] APScheduler runs analysis every 30 minutes
- [ ] Email alerts sent for signal changes via Resend
- [ ] Rate limiting prevents email spam
- [ ] Redis caching reduces API calls
- [ ] 10+ passing signal/notification tests

---

## 9. Phase 5: Dashboard & Visualization (Weeks 9–10)

### Week 9: Charts & Core Dashboard

**Task 5.1 — TradingView Lightweight Charts**
- Candlestick OHLCV rendering
- Overlays: SMA(50), SMA(200), Bollinger Bands
- Volume bars below price chart
- Signal markers: green triangle (BUY), red triangle (SELL)
- Timeframe selector: 1H, 4H, 1D, 1W
- Indicator panel below: RSI and MACD as separate panes

**Task 5.2 — Dashboard Main Page**
- Top row: 2 signal cards (one per crypto) — signal, confidence, component breakdown
- Middle: Candlestick chart with tab switch between cryptos
- Bottom: Key metrics grid (RSI, MACD status, Fear & Greed, sentiment score)

**Task 5.3 — React Query Data Hooks**
- `useSignal(symbol)`: latest signal, refetch every 60s
- `useOHLCV(symbol, timeframe)`: chart data
- `useMarketData(symbol)`: current price, 24h stats
- `usePredictionHistory(symbol)`: historical accuracy

**Task 5.4 — Zustand Store**
- `selectedSymbol`: which crypto is displayed
- `selectedTimeframe`: chart timeframe
- `sidebarCollapsed`: UI state
- No server data in Zustand — that's React Query's job

### Week 10: Portfolio, Predictions & Real-Time

**Task 5.5 — Portfolio View**
- Manual holdings entry (amount, average buy price per crypto)
- Current value from live prices, P&L calculation
- Allocation pie chart (Recharts)

**Task 5.6 — Predictions History Page**
- Table: past signals, timestamps, predicted vs actual outcome, accuracy
- Rolling 30-day accuracy chart (Recharts)
- Comparison: TA accuracy vs ML accuracy vs ensemble accuracy

**Task 5.7 — WebSocket Real-Time Prices**
- Backend: FastAPI WebSocket at `/ws/prices` relaying Binance stream
- Frontend: WebSocket hook with reconnection and exponential backoff
- Live price display with green/red flash animation on change
- Decision: WebSocket for prices only; signals update every 30 min via polling

**Task 5.8 — Full Settings Page**
- Crypto selection (2 coins), email alerts config, analysis interval
- Ollama status indicator, data management (backfill/retrain triggers)

### Phase 5 Definition of Done
- [ ] Candlestick charts with TA overlays for both cryptos
- [ ] Signal cards with confidence and component breakdown
- [ ] Real-time price updates via WebSocket
- [ ] Portfolio page with holdings and P&L
- [ ] Predictions page with accuracy history
- [ ] Responsive on desktop and mobile
- [ ] 5+ frontend component tests

---

## 10. Phase 6: Deployment & Polish (Weeks 11–12)

### Week 11: Production Deployment

**Task 6.1 — Frontend → Vercel**
- Connect GitHub repo, configure environment variables in Vercel dashboard
- `BACKEND_URL`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`, `NEXT_PUBLIC_BETTER_AUTH_URL`
- Verify Turbopack build succeeds

**Task 6.2 — Backend → Railway**
- Dockerfile: Python 3.12-slim, install requirements, uvicorn entry
- **Ollama in production**: Cannot run on Railway free tier (insufficient RAM)
  - **Option A (recommended)**: Skip LLM in production — TA + ML + sentiment still robust (3 sources)
  - **Option B**: Use Groq free API (30 RPM) as cloud LLM fallback
  - **Option C**: Run Ollama on a home server, expose via Cloudflare Tunnel
- ML model artifacts included in Docker image
- APScheduler runs in-process (no separate worker needed at this scale)

**Task 6.3 — Database Decision**
- **Option A (simpler)**: SQLite on Railway persistent volume
- **Option B (scalable)**: Neon PostgreSQL — update driver to asyncpg
- Recommendation: Start with SQLite, migrate if needed

**Task 6.4 — Redis Production**
- Create Upstash Redis instance, set `REDIS_URL` in Railway environment

### Week 12: Testing, Monitoring & Documentation

**Task 6.5 — End-to-End Tests**
- Playwright: login → dashboard → signal display → crypto switch
- Backend integration: trigger analysis cycle → verify signal stored → verify alerts

**Task 6.6 — Monitoring**
- Global exception handler with proper error responses
- Structured JSON logging with request ID tracing
- Enhanced health check: DB connectivity, Binance reachability, last analysis timestamp
- Railway/Render built-in logs (free monitoring)

**Task 6.7 — Security Hardening**
- CORS allows frontend origin only
- API key auth between frontend and backend (shared secret in header)
- `BACKEND_URL` is server-only (not exposed to client)
- No secrets in code — all in environment variables

**Task 6.8 — Performance Optimization**
- Analysis cycle completes within 2 minutes
- Lazy-load ML models (don't block startup)
- DB connection pooling
- Frontend: lazy-load chart components, verify Core Web Vitals

### Phase 6 Definition of Done
- [ ] Frontend accessible at Vercel URL with auth
- [ ] Backend running on Railway, accessible only to frontend
- [ ] Scheduled analysis running every 30 minutes in production
- [ ] Email alerts sent for signal changes
- [ ] Health endpoint reports all systems operational
- [ ] README provides complete setup instructions
- [ ] 3+ E2E tests passing
- [ ] Lighthouse score > 80

---

## 11. Signal Generation Strategy

### Ensemble Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Technical   │     │     ML       │     │  Sentiment   │     │     LLM      │
│  Analysis    │     │  Prediction  │     │  Analysis    │     │  Analysis    │
│  Weight: 35% │     │  Weight: 30% │     │  Weight: 20% │     │  Weight: 15% │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │                    │
       │  RSI, MACD, BB     │  XGBoost + LSTM    │  FinBERT + Reddit  │  Ollama narrative
       │  SMA, EMA, OBV     │  direction + conf   │  + Fear & Greed    │  interpretation
       │                    │                    │                    │
       └────────────────────┴────────────────────┴────────────────────┘
                                      │
                              ┌───────▼────────┐
                              │   Ensemble     │
                              │   Combiner     │
                              │   Score → Signal│
                              └───────┬────────┘
                                      │
                    ┌─────────────────┬┴┬─────────────────┐
                    │                 │ │                  │
              STRONG_BUY           BUY HOLD              SELL         STRONG_SELL
              (> 0.6)          (0.2-0.6) (-0.2-0.2)   (-0.6 to -0.2)  (< -0.6)
```

### Signal Output Format

```json
{
  "timestamp": "2026-04-07T14:30:00Z",
  "symbol": "BTC",
  "signal": "STRONG_BUY",
  "confidence": 0.78,
  "composite_score": 0.72,
  "components": {
    "technical": {"score": 0.85, "signal": "BUY", "rsi": 28, "macd": "bullish_cross"},
    "ml": {"score": 0.65, "confidence": 0.72, "xgboost": "UP", "lstm": "UP"},
    "sentiment": {"score": 0.55, "news": 0.6, "reddit": 0.4, "fear_greed": 22},
    "llm": {"signal": "BUY", "summary": "Multiple indicators align bullish..."}
  },
  "entry_price": 62500,
  "stop_loss": 61500,
  "take_profit_1": 63500,
  "take_profit_2": 65000
}
```

### Multi-Indicator Confirmation (Research Finding)

When RSI, MACD, and Bollinger Bands all align, backtested strategies show a **77% win rate** on Bitcoin. The real edge is in multi-indicator confirmation across multiple timeframes (1h confirmed by 4h/1d), not in any single indicator.

### Ensemble Voting Logic

- **High-conviction trade**: 3+ signals agree on direction AND confidence > 70%
- **Moderate trade**: 2 signals agree, 1 neutral
- **HOLD**: signals conflict or all neutral
- **Safety override**: complete TA/ML disagreement forces HOLD

---

## 12. Risk Management & Realistic Expectations

### What's Achievable

| Metric | Realistic Range | Notes |
|--------|----------------|-------|
| Directional accuracy | 55-65% | Above random (50%), not perfect |
| Win rate | 55-70% | With proper risk management |
| Profit factor | 1.5-2.5 | More gains than losses |
| Sharpe ratio | 1.0-2.0 | Risk-adjusted returns |

### What's NOT Realistic
- 85-95% accuracy (impossible in noisy markets)
- Consistent 20%+ monthly returns (unsustainable risk)
- Predicting every move (not possible even for institutions)
- Zero losses (all trading involves losing trades)

### Key Principles
1. **Risk management > prediction accuracy** — proper position sizing (1-2% per trade), stop losses on every trade
2. **Ensemble > single model** — combining multiple signals reduces false positives
3. **Backtest rigorously** — out-of-sample testing, account for slippage and fees
4. **Continuous adaptation** — markets change, retrain models periodically

### Recommended Portfolio Strategy
- 60% Core (BTC ~40%, ETH ~20%)
- 25% Mid-caps (configurable)
- 10% Small-caps (high risk)
- 5% Stablecoins (liquidity)

---

## 13. Cost Analysis

### Year 1 Costs (All Free Tiers)

| Component | Cost | Service |
|-----------|------|---------|
| Frontend hosting | $0 | Vercel Hobby |
| Backend hosting | $0 | Railway ($5/mo credit) or Render free |
| Database | $0 | SQLite or Neon free |
| Redis cache | $0 | Upstash free |
| Crypto data | $0 | Binance + CoinGecko free |
| Sentiment data | $0 | Reddit + Alternative.me free |
| LLM inference | $0 | Ollama local (or skip in production) |
| Email alerts | $0 | Resend 3K/month free |
| ML libraries | $0 | All open source |
| **Total** | **$0** | **Custom domain optional: ~$12/year** |

---

## 14. Risk Factors & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Binance API rate limits | Data fetching fails | Aggressive caching, CCXT as fallback exchange |
| CoinGecko 30/min limit | Backfill is slow | Batch requests, backfill once then incremental |
| Railway $5 credit exhausted | Backend offline | Monitor usage, optimize Docker, fallback to Render |
| Vercel 150K invocations | Frontend API routes exhausted | React Query caching (staleTime), reduce polling |
| Ollama unavailable in prod | No LLM analysis | System works without LLM, add Groq API fallback |
| FinBERT model size (~400MB) | Railway container size | Persistent volume, not rebuilt each deploy |
| False signals | Financial loss | Disclaimers, confidence scores, never auto-trade, track accuracy |
| Model degradation over time | Accuracy drops | Weekly retraining, monitor rolling accuracy |

---

## Summary Timeline

| Week | Phase | Key Deliverable |
|------|-------|----------------|
| 1 | Foundation | Backend API skeleton, database, data fetcher |
| 2 | Foundation | Frontend with auth, dashboard shell, live prices |
| 3 | Analysis Engine | Technical analysis indicators, ML model training |
| 4 | Analysis Engine | Backtesting framework, model validation |
| 5 | AI & Sentiment | FinBERT, Reddit scraper, Fear & Greed |
| 6 | AI & Sentiment | Ollama LLM integration, LangChain orchestration |
| 7 | Signal Engine | Ensemble signal generator, APScheduler |
| 8 | Notifications | Email alerts via Resend, Redis caching |
| 9 | Dashboard | TradingView charts, signal cards, metrics |
| 10 | Dashboard | Portfolio tracker, predictions history, WebSocket |
| 11 | Deployment | Vercel + Railway deployment, production config |
| 12 | Polish | Testing, monitoring, documentation, security |

---

## Environment Variables Reference

```env
# Backend
DATABASE_URL=sqlite+aiosqlite:///./investor.db
BINANCE_BASE_URL=https://api.binance.com/api/v3
COINGECKO_API_KEY=                    # Optional, higher rate limits with key
RESEND_API_KEY=re_xxxxxxxxxxxx
REDIS_URL=redis://default:xxx@xxx.upstash.io:6379
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.3
DEFAULT_SYMBOLS=["BTC","ETH","HBAR","IOTA"]
ANALYSIS_INTERVAL_MINUTES=30
ALERT_EMAIL_TO=your@email.com
ALERT_EMAIL_FROM=investor@yourdomain.com
REDDIT_CLIENT_ID=xxxxxxxxxxxx
REDDIT_CLIENT_SECRET=xxxxxxxxxxxx
REDDIT_USER_AGENT=investor-app/1.0

# Frontend
BACKEND_URL=http://localhost:8000     # Server-only, never exposed to client
BETTER_AUTH_SECRET=your-32-char-secret
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

---

*Document Version: 1.0 — April 7, 2026*
*Generated with extensive research across crypto APIs, ML frameworks, and deployment platforms.*
