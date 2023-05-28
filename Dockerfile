# syntax=docker/dockerfile:1

FROM python:bullseye
WORKDIR /app

RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		ffmpeg \
	; \
	rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==1.4.2"

COPY poetry.lock pyproject.toml /app
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --only main

# Get rid of git warnings
RUN git config --global pull.rebase false

# requires mounting src to /app
CMD ["poetry", "run", "bot"]