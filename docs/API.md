# API Specification & OpenAPI Documentation Guide

The **Cultural & Venue Smart Copilot Platform** exposes RESTful endpoints and real-time Server-Sent Events (SSE) / WebSockets under `/api/v1/`. All endpoints strictly adhere to **OpenAPI 3.1.0** standards and are fully documented interactive via Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## 🔐 Authentication & Headers

All protected endpoints require an `Authorization` header with a valid JWT Bearer token:
```http
Authorization: Bearer <your_jwt_access_token>
X-Request-ID: d5b82a7f-94d3-4a1e-8b1a-2c3d4e5f6a7b
```

### Response Formats & Error Schema
In case of validation failures, authorization errors, or domain exceptions, the API returns standardized error structures:
```json
{
  "error": "INSUFFICIENT_PERMISSIONS",
  "message": "User lacks required permission: venue:update",
  "status_code": 403,
  "trace_id": "8f3e2b1a-9c4d-5e6f-7a8b-9c0d1e2f3a4b",
  "timestamp": "2026-07-16T14:00:00Z"
}
```

---

## 🏛️ Core API Endpoint Summary

### 1. Authentication & Token Management (`/api/v1/auth`)

| Method | Endpoint | Description | Permissions Required | Rate Limit |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register a new user account | None (Public) | `5/minute` |
| `POST` | `/api/v1/auth/login` | Authenticate and receive access/refresh token pair | None (Public) | `5/minute` |
| `POST` | `/api/v1/auth/refresh` | Rotate refresh token and receive new access token | Valid Refresh Token | `10/minute` |
| `POST` | `/api/v1/auth/logout` | Revoke current refresh token and blacklist in Redis | Authenticated | `20/minute` |
| `GET` | `/api/v1/auth/me` | Get currently authenticated user profile and roles | Authenticated | `60/minute` |

#### Example Request (`POST /api/v1/auth/login`)
```json
{
  "email": "admin@cultural-copilot.org",
  "password": "SecurePassword123!"
}
```

#### Example Response (`200 OK`)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "a8f9d3e2-1b2c-3d4e-5f6a-7b8c9d0e1f2a",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "c1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c",
    "email": "admin@cultural-copilot.org",
    "full_name": "System Administrator",
    "role": "ADMIN"
  }
}
```

---

### 2. AI Multi-Agent Assistant & Chat (`/api/v1/assistant`)

| Method | Endpoint | Description | Permissions Required | Rate Limit |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/assistant/chat` | Send a query to the LangGraph multi-agent orchestrator | Authenticated | `30/minute` |
| `GET` | `/api/v1/assistant/chat/stream` | SSE endpoint for real-time streaming AI chat | Authenticated | `30/minute` |
| `GET` | `/api/v1/assistant/sessions` | List user conversation history and session summaries | Authenticated | `60/minute` |
| `POST` | `/api/v1/assistant/faq/search` | Semantic FAQ search using vector embeddings | Public / Authenticated | `100/minute` |

#### Example Request (`POST /api/v1/assistant/chat`)
```json
{
  "session_id": "f2e3d4c5-b6a7-8f9e-0a1b-2c3d4e5f6a7b",
  "message": "Where is the nearest wheelchair accessible restroom on the 2nd floor, and what is the current parking situation at Lot B?",
  "preferred_language": "en"
}
```

#### Example Response (`200 OK`)
```json
{
  "session_id": "f2e3d4c5-b6a7-8f9e-0a1b-2c3d4e5f6a7b",
  "response": "The nearest accessible restroom on the 2nd floor is next to Hall C (Room 204). Regarding parking, Lot B currently has 14 available spots, including 3 accessible spaces right by the North Entrance.",
  "active_agents": ["NavigationAgent", "ParkingAgent"],
  "executed_tools": [
    {"name": "find_poi", "args": {"category": "restroom", "accessible": true, "floor": 2}},
    {"name": "check_parking_status", "args": {"lot_name": "Lot B"}}
  ],
  "grounding_score": 0.96,
  "token_usage": {"prompt_tokens": 312, "completion_tokens": 84, "total_tokens": 396}
}
```

---

### 3. Navigation & Venue Operations (`/api/v1/venue`)

| Method | Endpoint | Description | Permissions Required | Rate Limit |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/venue/pois` | Filter and list points of interest (restrooms, exits, food) | Public / Authenticated | `100/minute` |
| `POST` | `/api/v1/venue/route` | Calculate shortest step-by-step route (with accessible option) | Public / Authenticated | `60/minute` |
| `GET` | `/api/v1/venue/crowd-density` | Get real-time crowd density metrics across halls | `venue:read` | `60/minute` |
| `POST` | `/api/v1/venue/alert` | Trigger high-priority emergency evacuation broadcast | `emergency:trigger` | `10/minute` |

---

### 4. Parking & Logistics (`/api/v1/parking`)

| Method | Endpoint | Description | Permissions Required | Rate Limit |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/parking/status` | Real-time capacity and EV availability across parking lots | Public / Authenticated | `100/minute` |
| `POST` | `/api/v1/parking/reserve` | Reserve an accessible or EV parking space | Authenticated | `20/minute` |

---

### 5. Health & Readiness Check Endpoints (`/api/v1/health`)

| Endpoint | Purpose | Returned Status Code |
| :--- | :--- | :--- |
| `GET /api/v1/health` | Overall system diagnostic check | `200 OK` or `503 Service Unavailable` |
| `GET /api/v1/readiness` | Verifies DB, Redis, and AI Provider connectivity before receiving traffic | `200 OK` or `503 Service Unavailable` |
| `GET /api/v1/liveness` | Basic container heartbeat check for Kubernetes / Docker restart probes | `200 OK` |
