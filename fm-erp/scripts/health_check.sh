#!/bin/bash

echo "Running health checks..."

services=(
    "postgres:5432"
    "influxdb:8086"
    "redis:6379"
    "kafka:9092"
    "fl-server:8080"
    "digital-twin:8081"
    "api-gateway:8000"
    "prometheus:9090"
    "grafana:3000"
)

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if nc -z localhost "$port"; then
        echo "✅ $name is healthy"
    else
        echo "❌ $name is unhealthy"
    fi
done
