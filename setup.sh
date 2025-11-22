#!/bin/bash

# ASLPS Setup Script
# This script helps set up the development environment

set -e

echo "=========================================="
echo "ASLPS Setup Script"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DEBUG=True
DJANGO_SECRET_KEY=dev-secret-key-$(openssl rand -hex 32)
MONGODB_HOST=mongodb://mongodb:27017/
MONGODB_DB=aslps_db
MONGODB_USERNAME=admin
MONGODB_PASSWORD=admin123
MONGODB_AUTH_SOURCE=admin
ML_MODEL_PATH=/app/ml_model/models/rf_model.pkl
CORS_ALLOWED_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api
EOF
    echo "✅ Created .env file"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

# Train ML model if it doesn't exist
if [ ! -f "ml_model/models/rf_model.pkl" ]; then
    echo "Training ML model..."
    cd ml_model/scripts
    python train_model.py
    cd ../..
    echo "✅ ML model trained"
else
    echo "ℹ️  ML model already exists"
fi
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p ml_model/models
mkdir -p ml_model/data
echo "✅ Directories created"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start services: docker-compose up --build"
echo "2. Seed database: docker-compose exec backend python db/seeds/seed_data.py"
echo "3. Access frontend: http://localhost:3000"
echo "4. Access backend: http://localhost:8000/api"
echo ""

