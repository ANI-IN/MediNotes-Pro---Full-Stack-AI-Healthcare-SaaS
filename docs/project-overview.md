# Project Overview

## What Is MediNotes Pro?

MediNotes Pro is a full-stack SaaS application that automates post-consultation medical documentation. It accepts free-text doctor notes and produces three structured outputs: a formal medical summary, clinical next steps, and a patient-friendly email — all delivered in real time via streaming.

## How The Project Was Built

The application was developed incrementally across five stages, each introducing a production-relevant engineering concept:

### Stage 1: API Foundation (Day 1)

The project began as a single FastAPI endpoint deployed to Vercel. A `GET /` route returned a static string, demonstrating the minimal viable deployment pipeline: write a Python file, configure `vercel.json`, deploy via Vercel CLI.

OpenAI integration was added immediately after — the endpoint called the chat completions API and returned HTML with the AI-generated response. This established the pattern of environment variable management (`OPENAI_API_KEY` via `vercel env add`) that persists throughout the project.

**Key files**: `instant.py`, `requirements.txt`, `vercel.json`

### Stage 2: Full-Stack Application (Day 2)

The project was rebuilt as a proper full-stack application using Next.js (Pages Router) with TypeScript for the frontend and FastAPI for the backend. The initial version used a simple `fetch` call to a `GET /api` endpoint. This was then upgraded to support Server-Sent Events for real-time streaming.

React Markdown rendering was added using `react-markdown` with `remark-gfm` and `remark-breaks` plugins. Tailwind CSS provided styling, with the Typography plugin handling markdown-generated HTML. Custom CSS in `globals.css` restored default HTML element styles that Tailwind strips.

**Key files**: `pages/index.tsx`, `api/index.py`, `styles/globals.css`

### Stage 3: Authentication and Billing (Day 3)

Clerk was integrated for user authentication. The frontend was split into a public landing page (`pages/index.tsx`) with `<SignInButton>`, `<SignedIn>`, and `<SignedOut>` components, and a protected product page (`pages/product.tsx`).

The backend was secured with `fastapi-clerk-auth`, which verifies JWTs by fetching Clerk's public keys from a JWKS URL. The `user_id` is extracted from the JWT `sub` claim on every request.

Subscription billing was added using Clerk's built-in billing. The `<Protect>` component gates access to the product page, showing a `<PricingTable>` fallback for non-subscribers. The `@microsoft/fetch-event-source` library replaced the native `EventSource` to support POST requests with custom headers (the JWT bearer token).

**Key files**: `pages/_app.tsx` (ClerkProvider), `pages/index.tsx`, `pages/product.tsx`, `api/index.py`

### Stage 4: Healthcare Domain (Day 4)

The application was pivoted from a generic business idea generator to a healthcare consultation assistant. The backend endpoint changed from `GET` to `POST`, accepting a structured `Visit` model via Pydantic:

```python
class Visit(BaseModel):
    patient_name: str
    date_of_visit: str
    notes: str
```

The system prompt was engineered to produce three specific sections: medical summary, next steps, and patient email draft. The frontend form uses `react-datepicker` for date input and submits the structured data via `fetchEventSource` with POST method and JSON body.

**Key files**: `pages/product.tsx`, `api/index.py`

### Stage 5: Containerization and AWS Deployment (Day 5)

The application was containerized using a multi-stage Dockerfile. Stage 1 (Node.js Alpine) builds the Next.js static export. Stage 2 (Python 3.12 slim) runs the FastAPI server and serves the static files.

`next.config.ts` was updated with `output: 'export'` to generate static HTML/JS/CSS. A new `api/server.py` was created that serves both the API endpoints and the static frontend. A `/health` endpoint was added for App Runner health probes.

The deployment pipeline involves: build Docker image → push to Amazon ECR → create App Runner service with environment variables. Cost controls were implemented via three AWS Budget alerts at $1, $5, and $10 thresholds.

**Key files**: `Dockerfile`, `.dockerignore`, `api/server.py`, `next.config.ts`

## Technical Components Summary

| Component | Technology | Role |
|-----------|-----------|------|
| Landing Page | Next.js + Clerk components | Public entry point with auth |
| Product Page | React + fetchEventSource | Protected form with SSE rendering |
| API Endpoint | FastAPI + Pydantic + OpenAI | Authenticated streaming AI generation |
| Auth Layer | Clerk (frontend) + fastapi-clerk-auth (backend) | JWT issuance and verification |
| Billing | Clerk Billing | Subscription management |
| Container | Docker multi-stage | Reproducible packaging |
| Hosting (Option A) | Vercel | Serverless deployment |
| Hosting (Option B) | AWS App Runner + ECR | Container deployment |

## What The Project Does Not Have

Being transparent about scope: the project does not include a database, test suite, CI/CD pipeline, retry logic, rate limiting, audit logging, or HIPAA compliance implementation. These are documented as future improvements and serve as extension points for capstone learners.
