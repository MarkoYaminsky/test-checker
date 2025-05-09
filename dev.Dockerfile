FROM python:3.13

# Set environment variable for Poetry version
ENV POETRY_VERSION=1.8.2
ENV POETRY_HOME="/opt/poetry"
ENV PATH="${POETRY_HOME}/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Install Poetry the right way
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi


# Copy project files
COPY ./app /opt/app
COPY poetry.lock pyproject.toml alembic.ini /opt/

WORKDIR /opt/

# Run the app
CMD ["uvicorn", "app.core.main:app", "--host", "0.0.0.0", "--reload"]
