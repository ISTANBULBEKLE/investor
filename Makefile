.PHONY: start stop restart backend-dev frontend-dev backend-test install-backend install-frontend install lint auth-migrate create-user

# ─── Start / Stop ────────────────────────────────────────────
start:
	@echo "Starting backend and frontend..."
	@cd backend && . .venv/bin/activate && OMP_NUM_THREADS=1 uvicorn app.main:app --reload --port 8000 --timeout-keep-alive 30 & echo $$! > .backend.pid
	@cd frontend && npm run dev & echo $$! > .frontend.pid
	@echo "Backend → http://localhost:8000"
	@echo "Frontend → http://localhost:3000"
	@echo "PIDs saved to .backend.pid / .frontend.pid"

stop:
	@echo "Stopping services..."
	@if [ -f .backend.pid ]; then kill $$(cat .backend.pid) 2>/dev/null; rm -f .backend.pid; echo "Backend stopped"; fi
	@if [ -f .frontend.pid ]; then kill $$(cat .frontend.pid) 2>/dev/null; rm -f .frontend.pid; echo "Frontend stopped"; fi
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@pkill -f "next dev" 2>/dev/null || true
	@echo "All services stopped."

restart: stop start

# ─── Individual dev servers ──────────────────────────────────
backend-dev:
	cd backend && . .venv/bin/activate && OMP_NUM_THREADS=1 uvicorn app.main:app --reload --port 8000 --timeout-keep-alive 30

frontend-dev:
	cd frontend && npm run dev

# ─── Install ─────────────────────────────────────────────────
install-backend:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

install: install-backend install-frontend

# ─── Auth ────────────────────────────────────────────────────
auth-migrate:
	cd frontend && echo "y" | npx @better-auth/cli migrate

create-user:
	cd frontend && npx tsx scripts/create-user.ts $(email) $(password) $(name)

# ─── Testing ─────────────────────────────────────────────────
backend-test:
	cd backend && . .venv/bin/activate && python -m pytest tests/ -v

# ─── Database ────────────────────────────────────────────────
db-migrate:
	cd backend && . .venv/bin/activate && alembic upgrade head

db-revision:
	cd backend && . .venv/bin/activate && alembic revision --autogenerate -m "$(msg)"

# ─── Model training ──────────────────────────────────────────
train-models:
	cd backend && . .venv/bin/activate && OMP_NUM_THREADS=1 python -m scripts.train_models

# ─── Linting ─────────────────────────────────────────────────
lint-backend:
	cd backend && . .venv/bin/activate && python -m ruff check .

lint-frontend:
	cd frontend && npm run lint

lint: lint-backend lint-frontend
