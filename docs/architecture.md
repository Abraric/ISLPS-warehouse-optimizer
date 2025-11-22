# ASLPS Architecture Documentation

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  Web Browser     │  │  Mobile App      │  │  API Client  │ │
│  │  (Next.js SSR)   │  │  (Future)        │  │  (External)  │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Django REST Framework                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │   API Views  │  │  Serializers │  │  Middleware  │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              ML Service Layer                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │  Predictor   │  │  Feature Eng. │  │  Model Loader │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │   MongoDB        │  │   Model Storage  │  │  Logs        │   │
│  │   (Atlas)        │  │   (File System)  │  │  (Files)     │   │
│  └──────────────────┘  └──────────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Prediction Request Flow

```
1. User Request
   │
   ▼
2. Frontend (Next.js)
   │  - Form validation
   │  - API call preparation
   │
   ▼
3. Backend API (Django)
   │  - JWT authentication
   │  - Request validation
   │
   ▼
4. ML Service
   │  - Load component data
   │  - Load available shelves
   │  - Load movement logs
   │
   ▼
5. Feature Engineering
   │  - Extract usage frequency
   │  - Calculate category similarity
   │  - Compute shelf proximity
   │  - Analyze pathway congestion
   │  - Check space availability
   │
   ▼
6. ML Model Inference
   │  - Random Forest prediction
   │  - Score calculation
   │  - Ranking
   │
   ▼
7. Edge Case Handling
   │  - Availability verification
   │  - Constraint checking
   │  - Fallback logic
   │
   ▼
8. Response Generation
   │  - Format result
   │  - Add reasoning
   │  - Include alternatives
   │
   ▼
9. Frontend Display
   │  - Render prediction
   │  - Show confidence
   │  - Display alternatives
```

## Microservices Architecture

### Service Breakdown

1. **API Service** (Django)
   - RESTful endpoints
   - Authentication & authorization
   - Request validation
   - Response formatting

2. **ML Service** (Django App)
   - Model loading & inference
   - Feature engineering
   - Prediction logic
   - Edge case handling

3. **Data Service** (MongoDB)
   - Component storage
   - Shelf management
   - Movement log tracking
   - Performance metrics

4. **Frontend Service** (Next.js)
   - UI rendering (SSR)
   - User interaction
   - Data visualization
   - API integration

## Database Schema

### Component Collection
```javascript
{
  component_id: String (unique),
  name: String,
  category: String,
  weight_kg: Float,
  length_m: Float,
  width_m: Float,
  height_m: Float,
  is_hazardous: Boolean,
  requires_climate_control: Boolean,
  temperature_range: [Float, Float],
  total_retrievals: Int,
  last_retrieved_at: DateTime,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Shelf Collection
```javascript
{
  shelf_id: String (unique),
  location: {
    x: Float,
    y: Float,
    z: Float,
    zone: String
  },
  max_weight_kg: Float,
  max_volume_m3: Float,
  current_weight_kg: Float,
  current_volume_m3: Float,
  is_hazardous_zone: Boolean,
  has_climate_control: Boolean,
  adjacent_shelves: [String],
  distance_to_entrance: Float,
  current_congestion_score: Float,
  is_available: Boolean,
  is_restricted: Boolean,
  created_at: DateTime,
  updated_at: DateTime
}
```

### MovementLog Collection
```javascript
{
  log_id: String (unique),
  component_id: String,
  shelf_id: String,
  movement_type: Enum['STORAGE', 'RETRIEVAL'],
  timestamp: DateTime,
  duration_seconds: Float,
  operator_id: String,
  congestion_at_time: Float,
  created_at: DateTime
}
```

## ML Model Architecture

### Feature Vector (12 features)

1. `usage_frequency` - Time-decayed retrieval frequency
2. `category_similarity` - Similarity to components in shelf
3. `shelf_proximity` - Graph distance to entrance
4. `pathway_congestion` - Traffic in adjacent shelves
5. `space_availability` - Available space ratio
6. `distance_to_entrance` - Physical distance (meters)
7. `shelf_congestion_score` - Current congestion level
8. `is_hazardous_match` - Hazardous zone match
9. `climate_control_match` - Climate control match
10. `weight_utilization` - Weight capacity usage
11. `volume_utilization` - Volume capacity usage
12. `zone_preference` - Historical zone preference

### Model Configuration

- **Algorithm**: Random Forest Classifier
- **Estimators**: 100 trees
- **Max Depth**: 15
- **Min Samples Split**: 5
- **Min Samples Leaf**: 2
- **Class Weight**: Balanced

## Security Architecture

### Authentication Flow

```
1. User Login
   │
   ▼
2. JWT Token Generation
   │  - Access token (1 hour)
   │  - Refresh token (7 days)
   │
   ▼
3. Token Storage (Frontend)
   │  - Local storage / Memory
   │
   ▼
4. API Request
   │  - Authorization: Bearer <token>
   │
   ▼
5. Token Validation (Backend)
   │  - Signature verification
   │  - Expiration check
   │
   ▼
6. Request Processing
```

## Deployment Architecture

### Docker Compose Services

```
┌─────────────────────────────────────────┐
│         Docker Network                  │
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │ Frontend │  │ Backend  │  │ MongoDB││
│  │ :3000    │  │ :8000    │  │ :27017 ││
│  └──────────┘  └──────────┘  └────────┘│
│                                         │
└─────────────────────────────────────────┘
```

### Production Considerations

- **Load Balancing**: Nginx reverse proxy
- **Database**: MongoDB Atlas (managed)
- **Caching**: Redis (optional)
- **Monitoring**: Application logs + metrics
- **Scaling**: Horizontal scaling via Docker Swarm/Kubernetes

## Performance Optimization

1. **Database Indexing**
   - Component ID, Category
   - Shelf ID, Zone
   - Movement Log timestamps

2. **Caching Strategy**
   - Model loading (singleton)
   - Shelf data (in-memory)
   - Feature computation (memoization)

3. **Query Optimization**
   - Selective field loading
   - Pagination
   - Time-windowed queries

## Monitoring & Logging

### Logging Levels

- **INFO**: Normal operations
- **WARNING**: Slow requests, edge cases
- **ERROR**: Failures, exceptions
- **DEBUG**: Detailed debugging (dev only)

### Metrics Tracked

- API response times
- Prediction accuracy
- Model performance drift
- Database query performance
- Error rates

---

**Last Updated**: 2024
**Version**: 1.0.0

