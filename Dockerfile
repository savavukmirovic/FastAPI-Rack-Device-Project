FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN uv sync --locked

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.app:app", "--port", "8000", "--host", "0.0.0.0"]