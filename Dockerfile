# SPDX-FileCopyrightText: 2024 Deren Vural derenvural@outlook.com
# SPDX-License-Identifier: MIT

# Base image
FROM alpine:latest

# Author settings
LABEL org.opencontainers.image.authors="Deren Vural derenvural@outlook.com"

# Set work directory
WORKDIR /usr/src/app

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install python/pip
RUN apk update \
    && apk add --update --no-cache python3 py3-pip

# Set up VENV
RUN python -m venv ./osrs-bluesky-bot

# Install dependancies
COPY ./requirements.txt .
RUN source ./osrs-bluesky-bot/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Set environment variables
#(SET BLUESKY_PASSWORD IN FLY)
ENV BLUESKY_USERNAME=osrsbot-unofficial.bsky.social
ENV OSRS_RSS_URL=https://secure.runescape.com/m=news/latest_news.rss?oldschool=true

# Run
COPY main.py .
CMD ["source", "./osrs-bluesky-bot/bin/activate", "&&", "exec", "python", "main.py"]
