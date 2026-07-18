# Observability & Monitoring Guide (Prometheus, Grafana, & Loki)

The **Cultural & Venue Smart Copilot Platform** includes an integrated, production-grade observability stack composed of **Prometheus** for metrics collection, **Grafana** for visual dashboards, and **Loki** for centralized structured JSON logging.

---

## 1. Accessing Observability Services

When running locally via `make docker-up` or in production:
- **Grafana Dashboards**: `http://localhost:3001` (Default credentials: `admin` / `admin`)
- **Prometheus Targets & Queries**: `http://localhost:9090`
- **Loki Log Query Endpoint**: `http://localhost:3100`

---

## 2. Key Prometheus PromQL Queries

Our FastAPI backend exposes pre-instrumented metrics at `/metrics` using custom middleware and `prometheus-fastapi-instrumentator`.

| Metric Name & Query | Description |
| :--- | :--- |
| `sum(rate(http_requests_total[1m])) by (method, status)` | Total HTTP request throughput per second, grouped by HTTP method and status code. |
| `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` | 95th percentile response latency across all backend API endpoints. |
| `rate(ai_agent_invocations_total[5m])` | Rate of multi-agent invocations (`OrchestratorAgent`, `NavigationAgent`, etc.). |
| `sum(ai_token_usage_total) by (provider, model)` | Total token consumption tracked across Google Gemini and OpenAI models (`CostTracker`). |
| `rate(security_rate_limit_exceeded_total[1m])` | Frequency of rate-limited or blocked requests by the security tier. |

---

## 3. Centralized Structured JSON Logging (Loki)

All logs emitted by our backend services (`structured_logging.py`) follow a standardized JSON format containing critical trace context:

```json
{
  "timestamp": "2026-07-16T14:05:22.104Z",
  "level": "INFO",
  "message": "Executed tool check_parking_status successfully for Lot B",
  "trace_id": "8f3e2b1a-9c4d-5e6f-7a8b-9c0d1e2f3a4b",
  "user_id": "c1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c",
  "agent_name": "ParkingAgent",
  "latency_ms": 14.2
}
```

### Example LogQL Queries in Grafana:
- **Filter logs by user ID and agent**:
  `{container="cultural_copilot_backend_dev"} |= "ParkingAgent" | json | user_id="c1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c"`
- **Trace an exact request flow across services**:
  `{container=~"cultural_copilot_.*"} |= "8f3e2b1a-9c4d-5e6f-7a8b-9c0d1e2f3a4b"`
- **Detect AI hallucination guardrail triggers or security blocks**:
  `{container="cultural_copilot_backend_dev"} | json | level="WARNING" | message=~".*PromptGuard.*"`
