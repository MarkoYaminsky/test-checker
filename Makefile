start-deps:
	docker compose up --build -d
	poetry install

runserver:
	make start-deps
	poetry run alembic upgrade head
	poetry run uvicorn app.core.main:app --reload

run-dev:
	docker compose -f docker-compose-dev.yaml up --build -d
	docker exec -it backend poetry install
	docker exec -it backend alembic upgrade head
