# Build multi_stage
FROM python:3.10 AS builder

WORKDIR /fast_api

COPY ./requirements.txt /fast_api/

# Install build dependencies and cleanup
RUN set -ex && \
    pip install --no-cache-dir --upgrade pip && \
    # pip install psutil && \
    pip install --no-cache-dir --prefix=/install -r /fast_api/requirements.txt

# Production stage
FROM python:3.10-slim

WORKDIR /fast_api
# Install libmagic package and other required system packages
RUN echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends libmagic1 && \
    apt-get clean && \
    rm -rf /var/cache/apt/*


# Copy only the necessary files from the builder stage, including updated requirements
COPY --from=builder /install /usr/local
COPY ./fast_api /fast_api/app

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7777", "--reload"]
