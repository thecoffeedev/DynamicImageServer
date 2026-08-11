#!/bin/bash
set -e

IMAGE_NAME="og_banner_gen:v2"
CONTAINER_NAME="og_banner_generator_v2"
PORT_MAPPING="5000:5000"

echo "Pulling latest code..."
git pull origin main

echo "Stopping and removing old container: $CONTAINER_NAME"
docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true

echo "Removing old image: $IMAGE_NAME"
docker rmi "$IMAGE_NAME" >/dev/null 2>&1 || true

echo "Building new image: $IMAGE_NAME"
docker build --no-cache -t "$IMAGE_NAME" .

echo "Running new container: $CONTAINER_NAME"
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart always \
  -p "$PORT_MAPPING" \
  "$IMAGE_NAME"

echo ""
echo "Deployment complete. Checking status..."
docker ps --filter "name=$CONTAINER_NAME"
