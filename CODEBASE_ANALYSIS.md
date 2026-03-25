# Codebase Analysis — MediNotes Pro

## A. What the Project Does

MediNotes Pro is a full-stack, AI-powered Healthcare Consultation Assistant. It accepts a doctor's free-text visit notes and returns three structured outputs:

1. **Professional Summary** — a concise medical-record-ready summary of the consultation.
2. **Next Steps** — actionable follow-up items for the physician.
3. **Patient Email Draft** — a patient-friendly communication written in plain language.

The application is built progressively across five days, evolving from a single-file FastAPI endpoint into a production-deployed, authenticated, subscription-gated SaaS product running on AWS.

## B. Main Workflow

```
Doctor opens browser → Lands on marketing page → Signs in via Clerk (Google/GitHub/Email)
→ Subscription gate checks plan → If subscribed, sees consultation form
→ Fills patient name, visit date, consultation notes → Submits form
→ Frontend sends POST with JWT to FastAPI backend → Backend verifies JWT via JWKS
→ Backend constructs system + user prompt → Calls OpenAI streaming API (gpt-5-nano)
→ Streams SSE chunks back to browser → Frontend renders Markdown in real time
→ Doctor reviews summary, next steps, and patient email draft
```

## C. Technical Components

### Frontend (Next.js / TypeScript / Tailwind)
- **Framework**: Next.js with Pages Router (not App Router)
- **Rendering**: Client-side (`"use client"` directive on all pages)
- **Styling**: Tailwind CSS with `@tailwindcss/typography` plugin
- **Auth UI**: `@clerk/nextjs@6.39.0` — `SignInButton`, `SignedIn`, `SignedOut`, `UserButton`, `Protect`, `PricingTable`
- **Streaming**: `@microsoft/fetch-event-source` for authenticated SSE
- **Markdown**: `react-markdown` with `remark-gfm` and `remark-breaks`
- **Date Input**: `react-datepicker` with type definitions
- **Static Export**: `output: 'export'` in `next.config.ts` for AWS deployment

### Backend (FastAPI / Python)
- **Framework**: FastAPI with Pydantic models
- **Auth**: `fastapi-clerk-auth` — JWKS-based JWT verification
- **AI**: OpenAI Python SDK with streaming (`stream=True`)
- **Response**: `StreamingResponse` with `text/event-stream` media type
- **Validation**: Pydantic `BaseModel` for `Visit` schema
- **Static Serving**: `StaticFiles` + `FileResponse` for serving Next.js export
- **Health Check**: `/health` endpoint for App Runner

### Infrastructure
- **Vercel**: Serverless deployment (auto-detects Next.js + Python)
- **Docker**: Multi-stage build (Node 22 Alpine → Python 3.12 slim)
- **AWS ECR**: Private container registry
- **AWS App Runner**: Serverless container hosting with HTTPS and auto-scaling
- **AWS IAM**: Dedicated user with scoped policies

## D. Core Modules

| Module | File | Responsibility |
|--------|------|----------------|
| Landing Page | `pages/index.tsx` | Marketing page, auth buttons, pricing preview |
| Product Page | `pages/product.tsx` | Subscription gate, consultation form, streaming output |
| App Wrapper | `pages/_app.tsx` | ClerkProvider, global CSS, date picker styles |
| Document | `pages/_document.tsx` | HTML metadata, page title |
| API (Vercel) | `api/index.py` | POST endpoint, JWT auth, OpenAI streaming |
| API (AWS) | `api/server.py` | Same + CORS, health check, static file serving |
| Styles | `styles/globals.css` | Tailwind imports + markdown base styles |
| Docker | `Dockerfile` | Multi-stage build |

## E. External Integrations

| Service | Purpose | Integration Method |
|---------|---------|-------------------|
| OpenAI | LLM inference (gpt-5-nano) | Python SDK, streaming completions |
| Clerk | Auth + billing | `@clerk/nextjs` (frontend), `fastapi-clerk-auth` (backend) |
| Vercel | Serverless deployment | CLI |
| AWS ECR | Container registry | Docker push via CLI |
| AWS App Runner | Container hosting | Console-based service creation |

## F. Database Design

**No database exists.** The application is entirely stateless. No consultation history, no user profiles beyond Clerk, no usage tracking.

## G. Testing Setup

**No tests exist.** Zero unit, integration, or E2E tests. No test frameworks installed. All testing is manual.

## H. What Is Production-Aligned

1. JWT authentication with JWKS verification
2. Subscription gating via Clerk Billing
3. Environment variables for all secrets
4. Docker multi-stage builds with platform-specific flags
5. AWS IAM with scoped policies (not root)
6. Health check endpoint for orchestration
7. CORS middleware
8. Pydantic input validation
9. Budget alerts at $1, $5, $10
10. SSE streaming for real-time UX
11. HTTPS on both deployment targets

## I. What Is Still Prototype-Level

| Area | Gap |
|------|-----|
| Database | None — all data ephemeral |
| Testing | Zero tests of any kind |
| Error handling | Minimal; no global handlers or retry logic |
| Logging | Only stdout / console |
| Rate limiting | None |
| Backend subscription check | Frontend-only; API can be called directly |
| Prompt management | Hardcoded strings |
| CI/CD | Manual deployments only |
| API versioning | None |
| Monitoring | CloudWatch logs only |
| HIPAA compliance | Claimed on UI but not implemented |
