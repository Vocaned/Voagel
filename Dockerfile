# syntax=docker/dockerfile:1

FROM debian:bookworm
WORKDIR /app

RUN apt update
RUN apt install -y python3 python3-pip git ffmpeg
# optional packages for eval usage
RUN apt install -y xonsh dnsutils

COPY --chown=1000:1000 requirements.txt /app
RUN pip install --break-system-packages -r requirements.txt

# Get rid of git warnings
RUN git config --global pull.rebase false
RUN git config --global safe.directory '*'

USER 1000
# requires mounting src to /app
CMD ["python3", "-m", "voagel.main"]
