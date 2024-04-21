# syntax=docker/dockerfile:1

FROM python:bullseye
WORKDIR /app

RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		ffmpeg \
	; \
	rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app
RUN pip install -U .

# Get rid of git warnings
RUN git config --global pull.rebase false
RUN git config --global safe.directory '*'

# requires mounting src to /app
CMD ["python", "/app/main/voagel.py"]
