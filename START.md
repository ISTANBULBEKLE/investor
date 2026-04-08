# INVESTOR — Start / Stop Commands

## First-Time Setup

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

## Daily Usage

```bash
# Start both backend (port 8000) and frontend (port 3000)
make start

# Stop everything
make stop

# Restart both
make restart
```

## Individual Servers

```bash
# Run backend only (blocking)
make backend-dev

# Run frontend only (blocking)
make frontend-dev
```

## Testing

```bash
# Run backend tests
make backend-test
```

## Other Commands

```bash
# Run better-auth DB migrations (creates user/session tables)
make auth-migrate

# Create a new user
make create-user email=you@example.com password=yourpass name=YourName

# Run database migration after model changes
make db-migrate

# Create a new migration
make db-revision msg="add new table"

# Lint all code
make lint
```

## URLs

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:3000         |
| Backend  | http://localhost:8000         |
| API Docs | http://localhost:8000/docs    |
