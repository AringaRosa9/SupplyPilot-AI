.PHONY: dev check backend-check frontend-check

dev:
	docker compose up --build

check: backend-check frontend-check

backend-check:
	cd backend && ruff check . && ruff format --check . && mypy app && pytest

frontend-check:
	cd frontend && npm run lint && npm run typecheck && npm test && npm run build
