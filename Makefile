.PHONY: dev dev-backend dev-frontend db seed test lint build clean

# ─── Development ───
dev: db dev-backend dev-frontend

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && pnpm dev

db:
	docker-compose up -d db

# ─── Database ───
migrate:
	cd backend && alembic upgrade head

migration:
	cd backend && alembic revision --autogenerate -m "$(msg)"

seed:
	cd backend && python scripts/seed_dsr.py

# ─── Testing ───
test:
	cd backend && pytest tests/ -v --cov=app

test-parser:
	cd backend && pytest tests/test_parser/ -v

test-api:
	cd backend && pytest tests/test_api/ -v

# ─── Linting ───
lint:
	cd backend && ruff check app/ && mypy app/
	cd frontend && pnpm lint

# ─── Build ───
build:
	docker-compose build

build-frontend:
	cd frontend && pnpm build

# ─── Cleanup ───
clean:
	docker-compose down -v
	rm -rf backend/.venv backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/.next frontend/node_modules
