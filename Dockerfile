FROM python:3.11

COPY ./app /opt/app
COPY requirements.txt alembic.ini /opt/

WORKDIR /opt/

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD uvicorn app.core.main:app --host 0.0.0.0 --reload
