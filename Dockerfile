FROM python:3-slim-bookworm
LABEL authors="anthony"

ENV LANG=C.UTF-8
ENV PATH="/home/anonymousbot/.local/bin:${PATH}"

# Install system dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Install system dependencies
RUN apt-get update -y
RUN apt-get install -y --no-install-recommends gcc
RUN rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd -rm anonymousbot
USER anonymousbot
WORKDIR /home/anonymousbot

# Install python dependencies
COPY --chown=anonymousbot:anonymousbot requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --break-system-packages -r requirements.txt --no-warn-script-location

# Copy rest of the project files
COPY --chown=anonymousbot:anonymousbot . .

# Copy entrypoint script and set permissions
USER root
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "main.py"]