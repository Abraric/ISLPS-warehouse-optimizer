Intelligent Storage Location Prediction System (ISLPS)

Enterprise-ready AI system that predicts the optimal warehouse shelf location for components using demand patterns, congestion, spatial constraints & ML — with full-stack deployment (Next.js + Django + MongoDB + Docker + CI/CD).

Architecture
flowchart TD
    U[📱 Next.js 14 UI<br/>Prediction + Analytics Dashboards] 
        -->|JWT Auth / API Calls| B{{ DRF Backend API }}
    B -->|Predict Request| M[ML Service<br/>Random Forest + Feature Engineering]
    B -->|CRUD + Movements + Logs| D[(MongoDB)]
    M -->|Read/Write| D

    subgraph Backend
        B
        M
    end

    subgraph Database
        D
    end

Features

Real ML Engine (Random Forest) with:

Time-decayed usage frequency

Shelf proximity graph distance

Space availability & hazard compatibility

Path congestion penalty

Category similarity (cold-start)

Edge Case Handling

Sudden demand spike

Restricted/hazard components

Cold-start items

Limited space fallback

Congestion avoidance

Next.js Ops Dashboard

Smart prediction form

Movement trend heatmap (D3.js)

Congestion map viewer

Model drift monitoring

Django API

Full CRUD for components + shelves

Movement logs & metrics

Prediction explanations & alternatives

Observability

Logging, drift tracking, reasoning trace

Dockerized Deployment (CI/CD ready)

Secure

JWT auth + CORS + Index-hardened DB

Folder Overview
ISLPS/
├── backend/                 # Django API + ML microservice
│   ├── api/                # CRUD endpoints
│   ├── ml_service/         # Feature engineering + RF model
│   ├── tests/              # pytest backend coverage
│   └── Dockerfile*
├── frontend/               # Next.js 14 dashboards
│   ├── app/               # Prediction & analytics UI
│   ├── lib/               # Auth + API client
│   └── Dockerfile*
├── ml_model/              # Training scripts + stored models
├── db/                    # MongoDB seed data scripts
├── docs/                  # API + architecture + ops docs
├── .github/workflows/     # CI/CD pipeline
├── docker-compose.yml     # Full system deploy
├── ENV_SETUP.md
└── QUICKSTART.md

Quickstart
git clone <repo-url>
cd "Intelligent Storage Location Prediction System (ISLPS)"
cp ENV_SETUP.md .env   # Fill environment values

Train the ML Model
cd ml_model/scripts
python train_model.py


Retrains Random Forest and stores models under ml_model/models/.

Run the Full Stack
docker-compose up --build


Services come alive:

Frontend: http://localhost:3000

Backend API: http://localhost:8000/api

Seed sample warehouse data:

docker-compose exec backend python db/seeds/seed_data.py

API Endpoints (Examples)

POST /api/predict/ → Predict best shelf + reasoning

GET /api/components/ → Components CRUD

GET /api/movement/trends/ → Heatmap

GET /api/model/drift/ → Performance monitoring

Swagger-style docs located in /docs/.

Tests

Backend:

pytest


Frontend:

npm test

Recruiter-Friendly Highlights

Zero boilerplate — all components are production-functional

Complete ML + Full-stack integration

Performance monitoring & fallback logic

Covers entire pipeline:

real warehouse logic → ML prediction → UI visualization → deploy

Enterprise-aligned architecture

Modular backend

Containerized services

GitHub Actions CI/CD

MongoDB performance indexes
