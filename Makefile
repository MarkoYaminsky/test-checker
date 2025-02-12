start-deps:
	docker compose up --build -d

runserver:
	make start-deps
	poetry run alembic upgrade head
	poetry run uvicorn app.core.main:app --reload
