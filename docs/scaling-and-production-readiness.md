# Scaling and Production Readiness

## Current Production Readiness Assessment

| Criterion | Status | Score (1-5) |
|-----------|--------|-------------|
| Functional correctness | Working end-to-end | 4 |
| Authentication | JWT with JWKS | 4 |
| Authorization | Subscription gating | 4 |
| Input validation | Pydantic + HTML5 | 3 |
| Error handling | Minimal | 1 |
| Logging and observability | CloudWatch only | 1 |
| Testing | None | 0 |
| CI/CD | Manual deployment | 1 |
| Scalability design | Single instance | 2 |
| Data persistence | None (stateless) | 1 |
| Cost management | AWS Budget alerts | 3 |
| Documentation | Comprehensive | 4 |

**Overall: Functional prototype with strong auth, weak on reliability and observability.**

---

## Scaling Dimensions

### Vertical Scaling (Bigger Instances)

The AWS App Runner service is currently configured at the minimum: 0.25 vCPU, 0.5 GB memory. This is sufficient for development and light use. For higher load, increase to 1 vCPU / 2 GB memory. This handles more concurrent streaming connections per instance.

The primary bottleneck is not CPU or memory — it is the OpenAI API response time. Each request occupies a connection for the duration of the streaming response (10-30 seconds). With a single instance, this limits practical concurrency to approximately 5-10 simultaneous users.

### Horizontal Scaling (More Instances)

App Runner supports auto-scaling with configurable min/max instances. Currently set to min=1, max=1 for cost control.

For production:
- min: 2 (for availability during deployments)
- max: 10 (or based on expected peak load)
- Scale trigger: concurrent requests per instance

Each instance is stateless, so horizontal scaling requires no coordination between instances.

### Database Scaling

No database exists currently. When added:
- Start with a managed PostgreSQL instance (AWS RDS, db.t3.micro)
- Connection pooling via PgBouncer or built-in RDS proxy
- Read replicas for query-heavy analytics
- Vertical scaling (larger RDS instance) before horizontal

### AI API Scaling

OpenAI rate limits are the external constraint. Strategies:
- Request queuing with backpressure
- Model fallback (try primary model, fall back to cheaper/faster model on rate limit)
- Response caching for identical or similar inputs
- Batch processing for non-real-time use cases

---

## Production Hardening Checklist

### Must Have (Before Real Users)

- [ ] Error boundaries in React (catch component crashes)
- [ ] Retry logic for OpenAI API (exponential backoff)
- [ ] Rate limiting per user (prevent abuse)
- [ ] Request timeout handling (kill long-running requests)
- [ ] Health check improvements (verify OpenAI connectivity)
- [ ] Structured logging (JSON format for CloudWatch parsing)
- [ ] Basic test suite (model validation, auth rejection, health check)

### Should Have (Before Paying Customers)

- [ ] Database for consultation history
- [ ] Audit logging (user ID, timestamp, action)
- [ ] CI/CD pipeline (GitHub Actions → ECR → App Runner)
- [ ] Input sanitization (prompt injection prevention)
- [ ] Error reporting (Sentry or similar)
- [ ] Custom domain with SSL
- [ ] Response caching for repeated queries
- [ ] Graceful degradation (message when AI unavailable)

### Nice to Have (Production Polish)

- [ ] Multi-region deployment
- [ ] CDN for static assets (CloudFront)
- [ ] A/B testing for prompt variations
- [ ] Analytics dashboard (usage metrics)
- [ ] Automated alerting (PagerDuty/Opsgenie)
- [ ] Blue/green deployments
- [ ] Database migrations (Alembic)
- [ ] API versioning (`/api/v1/consultation`)

---

## Reliability Patterns Not Yet Implemented

### Circuit Breaker

If OpenAI is down, the system should stop trying after N failures and return a cached response or error message, rather than making users wait for timeouts.

### Retry with Backoff

```python
import time

def call_openai_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model="gpt-5-nano", messages=prompt, stream=True
            )
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
```

### Dead Letter Queue

Failed requests should be logged to a dead letter queue (SQS) for later analysis, rather than silently dropped.

### Graceful Shutdown

The Docker container should handle SIGTERM signals and finish active streaming responses before shutting down during deployments.

---

## Cost Scaling Model

| Users | Instances | OpenAI Cost/mo | App Runner Cost/mo | Total |
|-------|-----------|---------------|-------------------|-------|
| 1-5 | 1 | ~$2 | ~$5 | ~$7 |
| 5-20 | 1-2 | ~$10 | ~$10 | ~$20 |
| 20-100 | 2-5 | ~$50 | ~$25 | ~$75 |
| 100-500 | 5-10 | ~$250 | ~$50 | ~$300 |

OpenAI token costs dominate at scale. The primary cost optimization lever is prompt efficiency (shorter system prompts, concise outputs).
