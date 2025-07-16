FROM n8nio/n8n:latest

USER root

# Install system dependencies and build tools
RUN apk add --no-cache python3 py3-pip build-base libffi-dev openssl-dev musl-dev cargo

# Upgrade pip, setuptools, wheel
RUN python3 -m pip install --upgrade --break-system-packages pip setuptools wheel


USER node

# Install Python packages locally for node user with break-system-packages flag
RUN python3 -m pip install --user --break-system-packages \
    feedparser \
    requests \
    beautifulsoup4 \
    tldextract \
    fake-useragent \

# Add local bin and site-packages to PATH and PYTHONPATH
ENV PATH="/home/node/.local/bin:$PATH"
ENV PYTHONPATH="/home/node/.local/lib/python3.12/site-packages"

# Install ngrok
RUN apt-get update && apt-get install -y curl && \
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
    apt-get update && apt-get install ngrok

ENV NGROK_AUTHTOKEN=2zaL5A1C7RVtCvvPxt38dYYwvMB_5VvzVVAxL62Qxj55efDYc
ENV NGROK_PORT=5678
ENV NGROK_DOMAIN=logical-bull-destined.ngrok-free.app
