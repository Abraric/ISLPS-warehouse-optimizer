# Adaptive Storage Location Prediction System (ASLPS)

## 📌 Project Overview

**ASLPS** is a production-grade intelligent warehouse management system that predicts optimal storage locations for incoming industrial components to minimize retrieval time using machine learning.

### 🎯 Objective

Predict optimal storage location for incoming industrial components to minimize retrieval time.

### 🏭 Domain

Smart Warehouse Logistics (Industrial Manufacturing)

### 🤖 AI Model

Random Forest Classifier (scikit-learn) with comprehensive feature engineering

---

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Next.js 14    │────────▶│  Django + DRF   │────────▶│  MongoDB Atlas  │
│   Frontend      │  HTTP    │    Backend      │  ODM    │    Database     │
│   (SSR)         │          │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                      │
                                      │ ML Inference
                                      ▼
                            ┌─────────────────┐
                            │ Random Forest  │
                            │   Classifier   │
                            └─────────────────┘
```

### Technology Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: Next.js 14 (App Router) with TypeScript
- **Database**: MongoDB Atlas (via mongoengine)
- **ML Model**: scikit-learn Random Forest
- **Deployment**: Docker + Docker Compose
- **Authentication**: JWT (djangorestframework-simplejwt)

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- MongoDB (or use Docker Compose)

### Running with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Intelligent Storage Location Prediction System (ISLPS)"
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - API Health: http://localhost:8000/api/health/

### Local Development Setup

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export DJANGO_SECRET_KEY="your-secret-key"
export MONGODB_HOST="mongodb://localhost:27017/"
export MONGODB_DB="aslps_db"

# Run migrations (if using Django ORM)
python manage.py migrate

# Start development server
python manage.py runserver
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

#### ML Model Training

```bash
cd ml_model/scripts
python train_model.py
```

#### Seed Database

```bash
cd db/seeds
python seed_data.py
```

---

## 📊 Features

### 1. Predict Storage Location
- ML-powered location recommendation
- Real-time feature extraction
- Confidence scoring
- Alternative location suggestions

### 2. Movement Trends Heatmap
- D3.js visualization
- Time-window filtering
- Movement pattern analysis

### 3. Congestion Map
- Real-time warehouse layout
- Zone-based filtering
- Congestion level indicators

### 4. Model Monitoring
- Accuracy drift tracking
- Performance metrics dashboard
- Historical trend analysis

---

## 🔧 ML Feature Engineering

The system implements comprehensive feature engineering:

1. **Usage Frequency** (time-decayed)
   - Exponential decay weighting
   - Handles sudden demand spikes

2. **Category Similarity** (cold-start)
   - Similarity matching for new components
   - Category-based recommendations

3. **Shelf Proximity** (graph distance)
   - BFS-based path calculation
   - Distance to entrance optimization

4. **Pathway Congestion** (real-time)
   - Time-windowed movement analysis
   - Adjacent shelf traffic consideration

5. **Availability Constraints** (space)
   - Weight and volume capacity checks
   - Real-time availability tracking

---

## 🛡️ Edge Case Handling

The system handles 5 critical edge cases:

1. **Sudden Demand Spike**
   - Time-decayed frequency calculation
   - Recent movements weighted higher

2. **Limited Availability**
   - Fallback to alternative shelves
   - Real-time capacity checking

3. **Restricted/Hazard Components**
   - Constraint-based filtering
   - Zone requirement validation

4. **New Components (Cold-Start)**
   - Category similarity matching
   - Default feature values

5. **Congestion Avoidance**
   - Pathway traffic analysis
   - Congestion penalty in scoring

---

## 📡 API Documentation

### Authentication

All endpoints (except health check) require JWT authentication.

**Login:**
```http
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Endpoints

#### Health Check
```http
GET /api/health/
```

#### Predict Location
```http
POST /api/ml/predict-location/
Authorization: Bearer <token>
Content-Type: application/json

{
  "component_id": "COMP-001",
  "consider_congestion": true,
  "preferred_zones": ["A", "B"]
}
```

**Response:**
```json
{
  "component_id": "COMP-001",
  "recommended_shelf_id": "SHELF-A-12",
  "confidence_score": 0.85,
  "alternative_shelves": [
    {
      "shelf_id": "SHELF-A-13",
      "score": 0.78,
      "zone": "A"
    }
  ],
  "reasoning": "Similar components stored here; Good space availability; Low pathway congestion",
  "feature_vector": {
    "usage_frequency": 0.65,
    "category_similarity": 0.72,
    ...
  }
}
```

#### Components CRUD
```http
GET    /api/components/
POST   /api/components/
GET    /api/components/<component_id>/
PUT    /api/components/<component_id>/
DELETE /api/components/<component_id>/
```

#### Shelves CRUD
```http
GET    /api/shelves/
POST   /api/shelves/
GET    /api/shelves/<shelf_id>/
PUT    /api/shelves/<shelf_id>/
DELETE /api/shelves/<shelf_id>/
```

#### Movement Logs
```http
GET /api/movements/?component_id=COMP-001&hours=24
POST /api/movements/
```

#### Model Performance
```http
GET /api/model-performance/?version=latest&hours=168
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=.
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## 📈 Model Performance

The Random Forest model achieves:

- **Accuracy**: ~85-90%
- **Precision**: ~82-88%
- **Recall**: ~80-86%
- **F1 Score**: ~81-87%

*Metrics vary based on training data and warehouse configuration*

---

## 🐳 Docker Services

- **mongodb**: MongoDB 7.0 database
- **backend**: Django REST API
- **frontend**: Next.js application

### Docker Compose Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build
```

---

## 📁 Repository Structure

```
.
├── backend/                 # Django backend
│   ├── api/                # Main API app
│   ├── ml_service/         # ML prediction service
│   ├── config/             # Django settings
│   ├── utils/              # Utilities & middleware
│   ├── tests/              # Unit tests
│   └── Dockerfile
├── frontend/               # Next.js frontend
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   ├── lib/               # API client
│   └── Dockerfile
├── ml_model/              # ML model training
│   ├── scripts/          # Training scripts
│   ├── models/           # Saved models
│   └── data/             # Training data
├── db/                   # Database
│   └── seeds/           # Seed data scripts
├── docs/                 # Documentation
├── .github/workflows/    # CI/CD pipelines
├── docker-compose.yml    # Docker orchestration
└── README.md
```

---

## 🔐 Security

- JWT authentication for all API endpoints
- Environment variable configuration
- CORS protection
- Input validation and sanitization
- Secure password handling

---

## 📝 License

This project is proprietary software for industrial warehouse management.

---

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request

---

## 📧 Support

For issues and questions, please contact the development team.

---

## 🎯 Roadmap

- [ ] Real-time WebSocket updates
- [ ] Advanced ML models (XGBoost, Neural Networks)
- [ ] Multi-warehouse support
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard

---

**Built with ❤️ for Smart Warehouse Logistics**

