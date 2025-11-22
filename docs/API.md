# ASLPS API Documentation

## Base URL

- Development: `http://localhost:8000/api`
- Production: `https://api.your-domain.com/api`

## Authentication

All endpoints (except health check) require JWT authentication.

### Login

**Endpoint:** `POST /api/token/`

**Request:**
```json
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

**Usage:**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### Refresh Token

**Endpoint:** `POST /api/token/refresh/`

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using Token

Include the token in the Authorization header:

```bash
Authorization: Bearer <access_token>
```

---

## Health Check

**Endpoint:** `GET /api/health/`

**Authentication:** Not required

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "service": "ASLPS Backend",
  "version": "1.0.0"
}
```

---

## Components

### List Components

**Endpoint:** `GET /api/components/`

**Response:**
```json
[
  {
    "component_id": "COMP-001",
    "name": "Steel Bearing 6205",
    "category": "Mechanical",
    "weight_kg": 0.5,
    "length_m": 0.05,
    "width_m": 0.05,
    "height_m": 0.02,
    "is_hazardous": false,
    "requires_climate_control": false,
    "total_retrievals": 10,
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### Get Component

**Endpoint:** `GET /api/components/{component_id}/`

**Response:**
```json
{
  "component_id": "COMP-001",
  "name": "Steel Bearing 6205",
  "category": "Mechanical",
  ...
}
```

### Create Component

**Endpoint:** `POST /api/components/`

**Request:**
```json
{
  "component_id": "COMP-002",
  "name": "New Component",
  "category": "Electronics",
  "weight_kg": 2.5,
  "length_m": 0.3,
  "width_m": 0.2,
  "height_m": 0.05,
  "is_hazardous": false,
  "requires_climate_control": true,
  "temperature_range": [15.0, 25.0]
}
```

### Update Component

**Endpoint:** `PUT /api/components/{component_id}/`

**Request:** Same as create (all fields required)

**Endpoint:** `PATCH /api/components/{component_id}/`

**Request:** Partial update (only fields to update)

### Delete Component

**Endpoint:** `DELETE /api/components/{component_id}/`

**Response:** `204 No Content`

---

## Shelves

### List Shelves

**Endpoint:** `GET /api/shelves/`

**Response:**
```json
[
  {
    "shelf_id": "SHELF-A-01-01",
    "location": {
      "x": 2.0,
      "y": 3.0,
      "z": 0.0,
      "zone": "A"
    },
    "max_weight_kg": 100.0,
    "max_volume_m3": 5.0,
    "current_weight_kg": 50.0,
    "current_volume_m3": 2.5,
    "available_space_m3": 2.5,
    "is_hazardous_zone": false,
    "has_climate_control": false,
    "distance_to_entrance": 5.0,
    "is_available": true,
    "is_restricted": false
  }
]
```

### Get Shelf

**Endpoint:** `GET /api/shelves/{shelf_id}/`

### Create Shelf

**Endpoint:** `POST /api/shelves/`

**Request:**
```json
{
  "shelf_id": "SHELF-B-01-01",
  "location": {
    "x": 10.0,
    "y": 20.0,
    "z": 5.0,
    "zone": "B"
  },
  "max_weight_kg": 200.0,
  "max_volume_m3": 10.0,
  "is_hazardous_zone": false,
  "has_climate_control": true,
  "temperature_range": [15.0, 25.0],
  "adjacent_shelves": ["SHELF-B-01-02"],
  "distance_to_entrance": 15.0
}
```

### Update Shelf

**Endpoint:** `PUT /api/shelves/{shelf_id}/` or `PATCH /api/shelves/{shelf_id}/`

### Delete Shelf

**Endpoint:** `DELETE /api/shelves/{shelf_id}/`

---

## Movement Logs

### List Movement Logs

**Endpoint:** `GET /api/movements/`

**Query Parameters:**
- `component_id` (optional): Filter by component
- `shelf_id` (optional): Filter by shelf
- `hours` (optional, default: 24): Time window in hours

**Example:**
```
GET /api/movements/?component_id=COMP-001&hours=48
```

**Response:**
```json
[
  {
    "log_id": "uuid-here",
    "component_id": "COMP-001",
    "shelf_id": "SHELF-A-01-01",
    "movement_type": "STORAGE",
    "timestamp": "2024-01-01T12:00:00Z",
    "duration_seconds": 180.0,
    "operator_id": "OP-01",
    "congestion_at_time": 0.3
  }
]
```

### Create Movement Log

**Endpoint:** `POST /api/movements/`

**Request:**
```json
{
  "component_id": "COMP-001",
  "shelf_id": "SHELF-A-01-01",
  "movement_type": "STORAGE",
  "timestamp": "2024-01-01T12:00:00Z",
  "duration_seconds": 180.0,
  "operator_id": "OP-01",
  "congestion_at_time": 0.3
}
```

---

## ML Prediction

### Predict Storage Location

**Endpoint:** `POST /api/ml/predict-location/`

**Request:**
```json
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
  "recommended_shelf_id": "SHELF-A-12-03",
  "confidence_score": 0.85,
  "alternative_shelves": [
    {
      "shelf_id": "SHELF-A-13-01",
      "score": 0.78,
      "zone": "A"
    },
    {
      "shelf_id": "SHELF-B-05-02",
      "score": 0.72,
      "zone": "B"
    }
  ],
  "reasoning": "Similar components stored here; Good space availability; Low pathway congestion",
  "feature_vector": {
    "usage_frequency": 0.65,
    "category_similarity": 0.72,
    "shelf_proximity": 15.0,
    "pathway_congestion": 0.25,
    "space_availability": 0.80,
    "distance_to_entrance": 15.0,
    "shelf_congestion_score": 0.20,
    "is_hazardous_match": 1.0,
    "climate_control_match": 1.0,
    "weight_utilization": 0.45,
    "volume_utilization": 0.50,
    "zone_preference": 0.75
  }
}
```

**Error Response:**
```json
{
  "error": "Component COMP-001 not found",
  "recommended_shelf_id": null,
  "confidence_score": 0.0
}
```

---

## Model Performance

### Get Model Performance Metrics

**Endpoint:** `GET /api/model-performance/`

**Query Parameters:**
- `version` (optional, default: "latest"): Model version
- `hours` (optional, default: 168): Time window in hours

**Response:**
```json
{
  "model_version": "1.0.0",
  "accuracy": 0.87,
  "precision": 0.85,
  "recall": 0.83,
  "f1_score": 0.84,
  "sample_size": 1000,
  "evaluated_at": "2024-01-01T12:00:00Z",
  "history": [
    {
      "evaluated_at": "2024-01-01T12:00:00Z",
      "accuracy": 0.87,
      "f1_score": 0.84
    },
    {
      "evaluated_at": "2023-12-31T12:00:00Z",
      "accuracy": 0.86,
      "f1_score": 0.83
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "error": "Component not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production, consider:
- 100 requests/minute per IP
- 1000 requests/hour per authenticated user

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page` (default: 1)
- `page_size` (default: 50, max: 100)

**Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/components/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** (not in localStorage for sensitive apps)
3. **Handle token expiration** (refresh before expiry)
4. **Validate input** on client side before sending
5. **Handle errors gracefully** with user-friendly messages
6. **Use appropriate HTTP methods** (GET for read, POST for create, etc.)
7. **Implement retry logic** for transient failures

---

**For more details, see [README.md](../README.md) and [architecture.md](architecture.md)**

