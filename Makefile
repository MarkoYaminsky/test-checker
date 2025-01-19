start-deps:
	docker compose up --build -d

runserver:
	alembic upgrade head
	uvicorn app.core.main:app --reload
