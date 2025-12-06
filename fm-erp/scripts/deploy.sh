#!/bin/bash

set -e

echo "🚀 FM-ERP Deployment Script"
echo "============================="

# Check prerequisites
echo "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker not installed"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose not installed"; exit 1; }
echo "✅ Prerequisites satisfied"

# Generate blockchain crypto materials
echo "Generating blockchain certificates..."
./scripts/generate_crypto.sh

# Initialize databases
echo "Initializing databases..."
docker-compose up -d postgres influxdb redis
sleep 10

# Start blockchain network
echo "Starting Hyperledger Fabric network..."
docker-compose up -d fabric-orderer fabric-peer
sleep 15

# Deploy chaincode
echo "Deploying smart contracts..."
./scripts/deploy_chaincode.sh

# Start message queue
echo "Starting Kafka..."
docker-compose up -d zookeeper kafka
sleep 10

# Start application services
echo "Starting application services..."
docker-compose up -d fl-server digital-twin iot-processor api-gateway

# Start monitoring
echo "Starting monitoring stack..."
docker-compose up -d prometheus grafana

# Health check
echo "Running health checks..."
sleep 30
./scripts/health_check.sh

echo "✅ FM-ERP deployment complete!"
echo "📊 Grafana: http://localhost:3000 (admin / $GF_SECURITY_ADMIN_PASSWORD)"
echo "🔧 API Gateway: http://localhost:8000"
echo "📈 Prometheus: http://localhost:9090"
echo "🌐 FL Server: http://localhost:8080"
