backend-install:
	cd backend && python -m pip install -e '.[dev]'
backend-run:
	cd backend && uvicorn app.main:app --reload
backend-test:
	cd backend && pytest -q
backend-lint:
	cd backend && ruff check . && ruff format --check .
frontend-install:
	cd frontend && npm install
frontend-run:
	cd frontend && npm run dev
frontend-test:
	cd frontend && npm test
frontend-build:
	cd frontend && npm run build
