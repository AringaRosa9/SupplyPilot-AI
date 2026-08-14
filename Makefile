.PHONY: dev check backend-check frontend-check demo-reset

dev:
	docker compose up --build

check: backend-check frontend-check

backend-check:
	cd backend && ruff check . && ruff format --check . && mypy app && pytest

frontend-check:
	cd frontend && npm run lint && npm run typecheck && npm test && npm run build

demo-reset:
	docker compose exec api python -m app.cli.seed_demo --reset
