# (SPDX info)
#

# Base image
FROM alpine:latest

# set work directory
WORKDIR /usr/src/app

# set environment variables
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

# Copy configuration file
COPY .env .

#test
#RUN ls -lah .
#RUN ls -lah ./osrs-bluesky-bot

# Run
COPY main.py .
#CMD [ "python", "main.py" ]
CMD source ./osrs-bluesky-bot/bin/activate && exec python main.py
