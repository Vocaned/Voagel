# syntax=docker/dockerfile:1

FROM python:bullseye
WORKDIR /app

RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		ffmpeg \
	; \
	rm -rf /var/lib/apt/lists/*

COPY poetry.lock pyproject.toml /app
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# requires mounting src to /app
CMD ["poetry", "run", "bot"]
