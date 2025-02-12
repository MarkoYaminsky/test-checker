FROM python:3.13

COPY ./app /opt/app
COPY poetry.lock pyproject.toml alembic.ini /opt/

WORKDIR /opt/

RUN pip install poetry
RUN poetry install

ENV PYTHONUNBUFFERED=1

CMD uvicorn app.core.main:app --host 0.0.0.0 --reload
