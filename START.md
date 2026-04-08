# INVESTOR — Setup & Run

## First-Time Setup

```bash
# 1. Install all dependencies
make install

# 2. Run database migrations
make db-migrate
make auth-migrate

# 3. Start the app
make start

# 4. Create your admin account (app must be running)
make create-user email=you@email.com password=yourpassword name=Admin

# 5. Train ML models (takes ~1 min per symbol)
make train-models
```

## Daily Usage

```bash
make start          # Start backend (port 8000) + frontend (port 3000)
make stop           # Stop everything
make restart        # Stop then start
```

## Other Commands

```bash
make backend-dev    # Run backend only (blocking, with hot reload)
make frontend-dev   # Run frontend only (blocking)
make backend-test   # Run all 49 backend tests
make train-models   # Retrain ML models (BTC, ETH, HBAR, IOTA)
make db-migrate     # Apply backend database migrations
make auth-migrate   # Apply better-auth database migrations
make create-user email=... password=... name=...  # Create login account
make lint           # Lint all code
```

## URLs

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:3000         |
| Backend  | http://localhost:8000         |
| API Docs | http://localhost:8000/docs    |

## Optional: Enable Extra Features

| Feature | What to do |
|---------|------------|
| **Email alerts** | Sign up at https://resend.com (free), add `RESEND_API_KEY` to `backend/.env` |
| **Reddit sentiment** | Create app at https://reddit.com/prefs/apps, add `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` to `backend/.env` |
| **LLM analysis** | Install Ollama (`brew install ollama`), run `ollama pull mistral`, start with `ollama serve` |
| **More CoinGecko data** | Sign up at https://coingecko.com/api, add `COINGECKO_API_KEY` to `backend/.env` |

The app works without any of these — they just add more analysis sources.
