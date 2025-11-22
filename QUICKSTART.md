# ASLPS Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Prerequisites
- Docker & Docker Compose installed
- Git installed

### Step 2: Clone and Setup
```bash
git clone <repository-url>
cd "Intelligent Storage Location Prediction System (ISLPS)"
```

### Step 3: Create Environment File
```bash
# Copy example (or create manually)
cat > .env << EOF
DEBUG=True
DJANGO_SECRET_KEY=dev-secret-key-change-in-production
MONGODB_HOST=mongodb://mongodb:27017/
MONGODB_DB=aslps_db
MONGODB_USERNAME=admin
MONGODB_PASSWORD=admin123
MONGODB_AUTH_SOURCE=admin
ML_MODEL_PATH=/app/ml_model/models/rf_model.pkl
CORS_ALLOWED_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api
EOF
```

### Step 4: Train ML Model (Optional but Recommended)
```bash
# This will create the model file needed for predictions
cd ml_model/scripts
python train_model.py
cd ../..
```

### Step 5: Start Everything
```bash
docker-compose up --build
```

### Step 6: Seed Database (In a new terminal)
```bash
# Wait for services to be ready (30 seconds), then:
docker-compose exec backend python db/seeds/seed_data.py
```

### Step 7: Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Health Check**: http://localhost:8000/api/health/

## 🎯 First Prediction

1. Open http://localhost:3000
2. Go to "1️⃣ Predict Storage Location" tab
3. Enter component ID: `COMP-001`
4. Click "Predict Optimal Location"

## 🔑 Authentication

For API access, you'll need to create a Django user first:

```bash
docker-compose exec backend python manage.py createsuperuser
```

Then login via:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

## 🐛 Troubleshooting

### MongoDB Connection Issues
```bash
# Check MongoDB is running
docker-compose ps mongodb

# View MongoDB logs
docker-compose logs mongodb
```

### Backend Not Starting
```bash
# Check backend logs
docker-compose logs backend

# Rebuild backend
docker-compose up --build backend
```

### Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up --build frontend
```

### Model Not Found
```bash
# Train the model
cd ml_model/scripts
python train_model.py
```

## 📝 Next Steps

1. Read the full [README.md](README.md)
2. Review [Architecture Documentation](docs/architecture.md)
3. Explore the API endpoints
4. Customize for your warehouse

---

**Happy Predicting! 🎉**

