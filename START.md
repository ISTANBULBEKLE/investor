# INVESTOR — Start / Stop Commands

## Local Development — First-Time Setup

```bash
# 1. Install all dependencies
make install

# 2. Run database migrations (backend + auth)
make db-migrate
make auth-migrate

# 3. Start the app
make start

# 4. Create your admin account (server must be running)
make create-user email=admin@investor.local password=admin123 name=Admin
```

## Local Development — Daily Usage

```bash
make start          # Start backend (port 8000) + frontend (port 3000)
make stop           # Stop everything
make restart        # Stop then start
make backend-dev    # Run backend only (blocking)
make frontend-dev   # Run frontend only (blocking)
make backend-test   # Run 49 backend tests
make train-models   # Train ML models for all symbols (BTC, ETH, HBAR, IOTA)
```

## Local URLs

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:3000         |
| Backend  | http://localhost:8000         |
| API Docs | http://localhost:8000/docs    |

---

## Production Deployment

### Architecture

```
Vercel (free)                    Oracle Cloud (free forever)
─────────────                    ──────────────────────────
Next.js frontend                 FastAPI backend
https://your-app.vercel.app      http://VM_IP:8000
```

### Step 1: Push code to GitHub

```bash
git add -A
git commit -m "Full INVESTOR app — Phases 1-5 complete"
git push origin main
```

### Step 2: Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from frontend directory
cd frontend
vercel

# Set environment variables in Vercel dashboard:
#   BACKEND_URL           = http://YOUR_ORACLE_VM_IP:8000
#   BETTER_AUTH_SECRET    = (generate: openssl rand -base64 32)
#   BETTER_AUTH_URL       = https://your-app.vercel.app
#   NEXT_PUBLIC_BETTER_AUTH_URL = https://your-app.vercel.app
```

### Step 3: Set up Oracle Cloud Always-Free VM

1. Create account at https://cloud.oracle.com (no credit card needed)
2. Create Compute Instance:
   - Shape: **VM.Standard.A1.Flex** (Ampere ARM)
   - OCPUs: **4**, Memory: **24 GB**
   - Boot volume: **200 GB**
   - OS: Ubuntu 22.04 (aarch64)
3. Open firewall: Ingress rules for ports **22** (SSH) and **8000** (API)
4. SSH into the VM and run:

```bash
# Download and run the setup script
curl -fsSL https://raw.githubusercontent.com/ISTANBULBEKLE/investor/main/scripts/oracle-setup.sh | bash

# Edit production environment variables
nano /data/investor/.env

# Pull Ollama LLM model (optional, 4GB)
ollama pull mistral

# Train ML models (uses 365 days of data)
docker exec investor-backend python -m scripts.train_models --days 365

# Verify
curl http://localhost:8000/health
```

### Step 4: Create Production User

```bash
curl -X POST https://your-app.vercel.app/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -H "Origin: https://your-app.vercel.app" \
  -d '{"email":"you@email.com","password":"yourpassword","name":"Admin"}'
```

### Step 5: Verify

- Open https://your-app.vercel.app
- Login with your email/password
- Dashboard should show live crypto prices
- Signals generate every 30 minutes automatically

### Useful Production Commands (on Oracle VM)

```bash
docker logs investor-backend --tail 100     # View logs
docker restart investor-backend             # Restart backend
docker exec investor-backend python -m scripts.train_models  # Retrain models

# Update to latest code
cd ~/investor && git pull
cd backend && docker build -t investor-backend . && docker restart investor-backend
```
