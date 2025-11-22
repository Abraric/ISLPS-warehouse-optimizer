# Environment Variables Setup Guide

## Root Directory `.env` File

Create a `.env` file in the root directory with the following variables:

```bash
# Django Settings
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-change-in-production-min-50-chars
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# MongoDB Configuration
MONGODB_HOST=mongodb://localhost:27017/
MONGODB_DB=aslps_db
MONGODB_USERNAME=admin
MONGODB_PASSWORD=admin123
MONGODB_AUTH_SOURCE=admin

# ML Model Configuration
ML_MODEL_PATH=./ml_model/models/rf_model.pkl
ML_MODEL_VERSION=1.0.0

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Frontend API URL (for Next.js)
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Backend `.env` File (for local development)

If running backend locally (not in Docker), create `backend/.env`:

```bash
DEBUG=True
DJANGO_SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

MONGODB_HOST=mongodb://localhost:27017/
MONGODB_DB=aslps_db
MONGODB_USERNAME=
MONGODB_PASSWORD=
MONGODB_AUTH_SOURCE=admin

ML_MODEL_PATH=../ml_model/models/rf_model.pkl
ML_MODEL_VERSION=1.0.0

CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## Frontend `.env.local` File (for local development)

If running frontend locally (not in Docker), create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Production Environment Variables

For production deployment, ensure:

1. `DEBUG=False`
2. Strong `DJANGO_SECRET_KEY` (generate with: `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
3. Secure MongoDB credentials
4. Proper `ALLOWED_HOSTS` with your domain
5. HTTPS URLs in `CORS_ALLOWED_ORIGINS`

## Quick Setup Script

```bash
# Create root .env file
cat > .env << 'EOF'
DEBUG=True
DJANGO_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
ALLOWED_HOSTS=localhost,127.0.0.1
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

