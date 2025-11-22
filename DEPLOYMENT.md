# ASLPS Deployment Guide

## Production Deployment

### Prerequisites

- Docker & Docker Compose installed
- Domain name configured (optional)
- SSL certificate (for HTTPS)
- MongoDB Atlas account (or self-hosted MongoDB)

### Step 1: Environment Configuration

1. Create `.env` file in root directory:

```bash
DEBUG=False
DJANGO_SECRET_KEY=<generate-strong-secret-key>
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
MONGODB_HOST=mongodb+srv://<username>:<password>@cluster.mongodb.net/
MONGODB_DB=aslps_production
MONGODB_USERNAME=<atlas-username>
MONGODB_PASSWORD=<atlas-password>
MONGODB_AUTH_SOURCE=admin
ML_MODEL_PATH=/app/ml_model/models/rf_model.pkl
CORS_ALLOWED_ORIGINS=https://your-domain.com
NEXT_PUBLIC_API_URL=https://api.your-domain.com/api
```

2. Generate secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Step 2: Train ML Model

```bash
cd ml_model/scripts
python train_model.py
cd ../..
```

### Step 3: Build Production Images

```bash
# Build backend
docker build -f backend/Dockerfile.production -t aslps-backend:latest ./backend

# Build frontend
docker build -f frontend/Dockerfile.production -t aslps-frontend:latest ./frontend
```

### Step 4: Update docker-compose.yml for Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  mongodb:
    # Use MongoDB Atlas instead of local
    # Remove this service if using Atlas
    
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    environment:
      - DEBUG=False
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - MONGODB_HOST=${MONGODB_HOST}
      - MONGODB_DB=${MONGODB_DB}
      - MONGODB_USERNAME=${MONGODB_USERNAME}
      - MONGODB_PASSWORD=${MONGODB_PASSWORD}
    restart: always
    command: >
      sh -c "gunicorn config.wsgi:application 
             --bind 0.0.0.0:8000 
             --workers 4 
             --timeout 120 
             --access-logfile - 
             --error-logfile -"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.production
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: always
```

### Step 5: Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # API endpoints
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### Step 6: Deploy

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Step 7: Seed Database

```bash
docker-compose -f docker-compose.prod.yml exec backend python db/seeds/seed_data.py
```

### Step 8: Create Admin User

```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## Monitoring

### Health Checks

- Backend: `https://your-domain.com/api/health/`
- Frontend: `https://your-domain.com/`

### Logs

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Backup

```bash
# Backup MongoDB
docker-compose -f docker-compose.prod.yml exec mongodb mongodump --out /backup

# Backup ML model
cp ml_model/models/rf_model.pkl backups/
```

## Scaling

### Horizontal Scaling

```yaml
services:
  backend:
    deploy:
      replicas: 3
    # Use load balancer
```

### Database Scaling

- Use MongoDB Atlas with replica sets
- Configure read preferences
- Enable sharding for large datasets

## Security Checklist

- [ ] Strong Django secret key
- [ ] HTTPS enabled
- [ ] CORS configured properly
- [ ] MongoDB authentication enabled
- [ ] Firewall rules configured
- [ ] Regular security updates
- [ ] Log monitoring enabled
- [ ] Backup strategy in place

## Troubleshooting

### High Memory Usage

- Reduce Gunicorn workers
- Enable caching (Redis)
- Optimize database queries

### Slow Response Times

- Enable CDN for static files
- Use database indexes
- Implement caching layer

### Connection Issues

- Check firewall rules
- Verify DNS settings
- Test MongoDB connectivity

---

**For detailed architecture, see [architecture.md](docs/architecture.md)**

