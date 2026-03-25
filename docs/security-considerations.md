# Security Considerations

## Security Posture Summary

| Area | Status | Details |
|------|--------|---------|
| Authentication | Implemented | Clerk JWT with JWKS verification |
| Authorization | Implemented | Subscription gating via Clerk Protect |
| Transport Security | Implemented | HTTPS via Vercel/App Runner |
| Secrets Management | Implemented | Environment variables, not in code |
| Input Validation | Partial | Pydantic on backend, HTML5 required on frontend |
| Rate Limiting | Not Implemented | No per-user request throttling |
| Audit Logging | Not Implemented | No request logging |
| Data Encryption at Rest | Not Implemented | No database, so not applicable yet |
| HIPAA Compliance | Not Implemented | Landing page claim is aspirational |
| Input Sanitization | Not Implemented | Notes pass directly to LLM |

---

## What Is Implemented

### JWT Authentication Flow

Every API request is authenticated using JSON Web Tokens with JWKS verification:

1. User signs in via Clerk → Clerk issues a signed JWT
2. Frontend retrieves JWT via `getToken()` from `useAuth()` hook
3. JWT is sent in `Authorization: Bearer <token>` header
4. Backend uses `fastapi-clerk-auth` to verify the token

Verification happens locally on the backend using Clerk's public keys fetched from the JWKS URL. The backend does not contact Clerk per-request after the initial key fetch. This is important for two reasons: it is faster (no network round-trip), and it scales independently of the Clerk API.

```python
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)
```

The `sub` claim in the JWT provides the authenticated user's ID, which is available for per-user tracking or rate limiting.

### Environment Variable Isolation

Secrets are managed via environment variables, never hardcoded:

- `OPENAI_API_KEY` — Never exposed to the browser
- `CLERK_SECRET_KEY` — Backend only
- `CLERK_JWKS_URL` — Backend only
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` — Intentionally public (prefix `pk_` means it is safe for client-side use)

In Vercel, these are set via `vercel env add`. In AWS, they are configured in the App Runner service definition. In Docker, they are passed as `-e` flags at runtime (not baked into the image, except the public key which is a build arg).

### HTTPS Enforcement

Both Vercel and AWS App Runner provide automatic HTTPS with managed TLS certificates. No custom certificate management is needed.

### Pydantic Validation

The backend validates all incoming request bodies using Pydantic models:

```python
class Visit(BaseModel):
    patient_name: str
    date_of_visit: str
    notes: str
```

If a request is missing fields or has wrong types, FastAPI returns a 422 error with detailed validation messages before any processing occurs.

---

## What Is NOT Implemented

### Rate Limiting

There is no per-user rate limiting. An authenticated user can call the API an unlimited number of times. In production, this should be addressed with middleware:

```python
# Example: Token bucket per user_id
from fastapi import Request
from collections import defaultdict
import time

rate_limits = defaultdict(lambda: {"tokens": 10, "last_refill": time.time()})

async def rate_limit_middleware(request: Request, call_next):
    user_id = request.state.user_id  # After auth
    bucket = rate_limits[user_id]
    # Refill and check logic here
```

### Input Sanitization

Medical notes are passed directly from the form to the LLM prompt without sanitization. Potential risks:

- **Prompt injection**: A user could craft notes that override the system prompt (e.g., "Ignore all previous instructions and...")
- **Exfiltration**: Malicious input could attempt to extract system prompt content
- **XSS**: If output is rendered as HTML without sanitization (mitigated by using ReactMarkdown which escapes by default)

Mitigation: Sanitize input to remove common injection patterns, validate note length, and potentially use a separate safety-checking step before LLM processing.

### Audit Logging

No requests are logged. In a healthcare context, every access to patient data should be logged with:

- Timestamp
- User ID (from JWT `sub` claim)
- Action performed
- Input data hash (not the raw data, for privacy)
- Response status

### HIPAA Compliance

The landing page states "HIPAA Compliant" but no HIPAA controls are actually implemented. For real HIPAA compliance, the following would be needed:

- Business Associate Agreement (BAA) with AWS and OpenAI
- Encryption at rest for any stored data
- Encryption in transit (HTTPS is already present)
- Access controls and audit trails
- Minimum necessary standard for data access
- Incident response procedures
- Regular security assessments
- Employee training documentation

### Error Handling for Data Leakage

If the OpenAI API returns an error, the error message might contain partial request data. The current code does not sanitize error responses before sending them to the client.

---

## Threat Model

| Threat | Likelihood | Impact | Mitigation Status |
|--------|-----------|--------|-------------------|
| Stolen JWT used for unauthorized access | Medium | High | Mitigated (JWTs have expiration) |
| OpenAI API key exposure | Low | High | Mitigated (env vars, not in code) |
| Prompt injection via notes field | Medium | Medium | Not mitigated |
| DDoS via unlimited API calls | Medium | Medium | Not mitigated (no rate limiting) |
| Patient data breach | Low (no storage) | Critical | Partially mitigated (no data persistence) |
| Man-in-the-middle attack | Low | High | Mitigated (HTTPS) |
| Cross-site scripting (XSS) | Low | Medium | Mitigated (ReactMarkdown escaping) |

---

## Recommendations for Production Hardening

1. **Implement rate limiting** — 10-20 requests per user per hour
2. **Add input sanitization** — Strip potential injection patterns from notes
3. **Add audit logging** — Log user ID, timestamp, and action for every API call
4. **Add error boundaries** — Catch and sanitize error messages before client exposure
5. **Implement HIPAA controls** — If handling real patient data
6. **Add CSP headers** — Content Security Policy to prevent XSS
7. **Add request size limits** — Prevent oversized payloads
8. **Rotate API keys** — Regular rotation schedule for OpenAI and Clerk keys
