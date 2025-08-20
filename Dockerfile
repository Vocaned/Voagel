# syntax=docker/dockerfile:1

FROM debian:bookworm
WORKDIR /app

RUN sed -i 's/^Components: main$/& contrib non-free/' /etc/apt/sources.list.d/debian.sources
RUN apt update
RUN apt install -y python3 python3-pip git ffmpeg xonsh

# optional packages for eval usage
COPY extra_packages.txt /tmp/packages.txt
RUN xargs -a /tmp/packages.txt apt-get install -y

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --chown=1000:1000 requirements.txt /app
RUN pip install --break-system-packages -r requirements.txt

# Get rid of git warnings
RUN git config --global pull.rebase false
RUN git config --global safe.directory '*'

USER 1000
# requires mounting src to /app
CMD ["python3", "-m", "voagel.main"]
