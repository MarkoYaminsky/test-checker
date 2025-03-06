start-deps:
	docker compose up --build -d
	poetry install

runserver:
	make start-deps
	poetry run alembic upgrade head
	poetry run uvicorn app.core.main:app --reload
