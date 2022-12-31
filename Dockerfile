FROM python:3.11-slim AS telegram-mastodon-bridge

# Global python env vars
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

# Bridge env vars
ENV MASTODON_TOKEN ${MASTODON_TOKEN}
ENV TELEGRAM_TOKEN ${TELEGRAM_TOKEN}
ENV MASTODON_INSTANCE ${MASTODON_INSTANCE}
ENV MASTODON_VISIBILITY ${MASTODON_VISIBILITY}
ENV MASTODON_CHARACTER_LIMIT ${MASTODON_CHARACTER_LIMIT}

# Install global packages
RUN apt-get update
RUN apt-get install -y python3 python3-pip python-dev build-essential python3-venv

# Add codebase
RUN mkdir -p /bot
ADD . /bot
WORKDIR /bot

# Install dependencies
RUN pip3 install -r requirements.txt
RUN chmod +x ./bot.py

# Run bridge
CMD python3 ./bot.py;
