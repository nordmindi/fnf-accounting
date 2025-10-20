#!/bin/bash

echo "🔍 Docker Troubleshooting Script"
echo "================================"

echo "1. Checking Docker version..."
docker --version
docker-compose --version

echo -e "\n2. Checking if Docker daemon is running..."
if docker info >/dev/null 2>&1; then
    echo "✅ Docker daemon is running"
else
    echo "❌ Docker daemon is not running. Please start Docker Desktop or Docker daemon."
    exit 1
fi

echo -e "\n3. Cleaning up any existing containers and volumes..."
docker-compose down -v 2>/dev/null || true
docker system prune -f

echo -e "\n4. Building images step by step..."
echo "Building app image..."
docker-compose build app

echo -e "\n5. Starting services one by one..."
echo "Starting database..."
docker-compose up -d db
sleep 10

echo "Starting Redis..."
docker-compose up -d redis
sleep 5

echo "Starting MinIO..."
docker-compose up -d minio
sleep 10

echo "Starting app..."
docker-compose up -d app

echo -e "\n6. Checking service status..."
docker-compose ps

echo -e "\n7. Checking logs..."
echo "App logs:"
docker-compose logs app --tail=20

echo -e "\n✅ Troubleshooting complete!"
echo "If you still have issues, check the logs with: make logs"
