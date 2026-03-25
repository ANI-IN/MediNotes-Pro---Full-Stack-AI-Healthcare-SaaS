# Resume and Interview Guide

## Resume Presentation

### Single Bullet Version (For Dense Resumes)

> Built a full-stack healthcare SaaS with Next.js/TypeScript, FastAPI, Clerk (JWT auth + billing), and OpenAI streaming, deployed via Docker to Vercel and AWS App Runner.

### Three-Bullet Version (Recommended)

> **MediNotes Pro** — AI-Powered Healthcare Consultation Assistant
> - Designed and built a streaming AI application (Next.js, FastAPI, OpenAI) that generates structured medical summaries, clinical next steps, and patient emails from doctor consultation notes
> - Implemented end-to-end authentication with JWT/JWKS verification, multi-provider sign-in (Google/GitHub/Email), and subscription-gated access via Clerk Billing
> - Containerized with multi-stage Docker builds and deployed to both Vercel (serverless) and AWS App Runner (container) with cost controls under $10/month

### Five-Bullet Version (For Detailed Portfolios)

> **MediNotes Pro** — Full-Stack AI Healthcare SaaS
> - Architected a streaming pipeline using Server-Sent Events: FastAPI generates SSE events from OpenAI's streaming API, the React frontend buffers tokens and renders incremental Markdown in real time
> - Implemented stateless JWT authentication: Clerk issues tokens on the frontend, the Python backend verifies signatures using JWKS public keys without per-request API calls — enabling independent scaling
> - Integrated subscription billing with Clerk's Protect component, gating product access with a PricingTable fallback for non-subscribers
> - Built a multi-stage Dockerfile: Node.js stage exports Next.js as static HTML/JS, Python stage serves the API and static files from a single container
> - Deployed to AWS App Runner with ECR image registry, health check probes, and three-tier budget alerts ($1/$5/$10) for cost governance

---

## Portfolio Page Structure

### Recommended Layout

```
# MediNotes Pro

[Screenshot of consultation form and streaming output]

## What It Does
One paragraph explaining the user experience.

## Architecture
[Mermaid diagram or architecture image]

## Key Engineering Decisions
- SSE over WebSockets: unidirectional streaming fits the LLM response pattern
- JWT/JWKS verification: stateless auth that scales independently
- Single-container deployment: FastAPI serves both API and static frontend

## Tech Stack
Next.js · TypeScript · Tailwind · FastAPI · Python · OpenAI · Clerk · Docker · AWS

## Links
[Live Demo] [GitHub Repository]
```

---

## Interview Questions and Suggested Answers

### Q1: "Walk me through the system architecture."

**Good Answer**: "The frontend is a Next.js application using Pages Router. All pages are client-side rendered — they use Clerk's React components for authentication and the `fetchEventSource` library to make POST requests to the backend. The backend is a FastAPI server that verifies JWTs using Clerk's JWKS public keys, validates the request body with Pydantic, constructs a prompt, and streams the OpenAI response as Server-Sent Events back to the browser. For deployment, Vercel handles this natively — it serves the frontend from its CDN and routes `/api` to a Python serverless function. For AWS, I packaged everything into a single Docker container using a multi-stage build — Node.js exports the frontend as static files, and the Python stage serves both the API and the static files."

### Q2: "Why SSE over WebSockets?"

**Good Answer**: "SSE is a better fit for this use case because the communication is unidirectional — the server streams tokens to the client. WebSockets support bidirectional communication, which adds protocol complexity (handshake, frame management, ping/pong) that we don't need. SSE works over standard HTTP, is natively supported by browsers, and auto-reconnects on failure. The one limitation is that the native `EventSource` API only supports GET, but the `fetchEventSource` library from Microsoft adds POST support with custom headers, which we need for sending the JWT and JSON body."

### Q3: "How does your authentication work?"

**Good Answer**: "Clerk handles the frontend auth — the user signs in via a modal (Google, GitHub, or email), and Clerk manages the session. When the frontend needs to call the API, it calls `getToken()` from Clerk's `useAuth` hook, which returns a JWT. This JWT is sent as a Bearer token in the Authorization header. On the backend, `fastapi-clerk-auth` acts as middleware — it fetches Clerk's JWKS (JSON Web Key Set) from a public URL, caches the public keys, and verifies the JWT's cryptographic signature and expiration. The `sub` claim in the token gives us the user ID. Importantly, the backend never contacts Clerk per-request after the initial JWKS fetch — it verifies tokens locally using the cached public keys. This means the backend scales independently of Clerk's API."

### Q4: "What is JWKS and why do you use it?"

**Good Answer**: "JWKS stands for JSON Web Key Set. It's a standardized format for publishing public keys at a well-known URL. Clerk signs JWTs with its private key and publishes the corresponding public key at the JWKS URL. My backend fetches this public key set once, caches it, and uses it to verify every incoming JWT's signature. This is better than a shared secret because the verification key is public — it can't be used to forge tokens, only to verify them. And it's better than calling Clerk's API per-request because it eliminates that network dependency."

### Q5: "What would break under high load?"

**Good Answer**: "Three things. First, each streaming response holds a connection open for 10-30 seconds, so with a single instance, practical concurrency is limited to maybe 5-10 simultaneous users. I'd scale horizontally with App Runner's auto-scaling. Second, OpenAI has rate limits per API key — at high volume, we'd need request queuing and potentially multiple API keys. Third, there's no rate limiting per user, so a single user could theoretically exhaust the OpenAI quota. I'd add a token bucket rate limiter keyed on the JWT's `sub` claim."

### Q6: "How would you add a database?"

**Good Answer**: "I'd add PostgreSQL via Amazon RDS. The schema would have a `consultations` table with columns for `id`, `user_id` (from the JWT `sub` claim), `patient_name`, `date_of_visit`, `notes`, `generated_output`, and `created_at`. After the streaming response completes, I'd insert the full output into the database. I'd use SQLAlchemy as the ORM and Alembic for migrations. For the frontend, I'd add a `/history` page that queries the user's past consultations. The database connection string would be another environment variable, and I'd use connection pooling to handle concurrent requests."

### Q7: "What would you change for HIPAA compliance?"

**Good Answer**: "Several things. First, I'd need a Business Associate Agreement with AWS, OpenAI, and Clerk — they're all processing protected health information. Second, encryption at rest: RDS supports transparent encryption, and I'd enable it. Third, audit logging: every data access needs to be logged with who accessed what, when, and from where. Fourth, access controls: role-based permissions so only authorized physicians can view specific patient data. Fifth, data retention: define how long consultation records are kept and automate deletion. Sixth, the landing page currently says 'HIPAA Compliant' which is aspirational — I'd remove that until compliance is actually achieved."

### Q8: "Your OpenAI API starts failing intermittently. How do you handle it?"

**Good Answer**: "I'd add three things. First, retry with exponential backoff — if a call fails, wait 1 second, retry, wait 2 seconds, retry, up to 3 attempts. Second, a circuit breaker — if failures exceed a threshold (say 5 in 60 seconds), stop making calls for a cooldown period and return a cached or fallback response. Third, I'd add model fallback — if the primary model is unavailable, try a different model. On the frontend, I'd add an error boundary that shows a user-friendly message instead of a broken UI, and a retry button."

### Q9: "Explain the Docker multi-stage build."

**Good Answer**: "The Dockerfile has two stages. Stage 1 uses `node:22-alpine` — it installs npm dependencies, copies the source code, receives the Clerk public key as a build argument, and runs `npm run build`, which produces a static export in the `/out` directory. Stage 2 uses `python:3.12-slim` — it installs Python dependencies, copies the FastAPI server file, and then copies the static export from Stage 1 into a `static` directory. The final image only contains the Python runtime, the FastAPI server, and the pre-built static files. The Node.js tools and `node_modules` are discarded — they were only needed at build time. This keeps the production image small and reduces attack surface."

### Q10: "Why two deployment paths? When would you choose each?"

**Good Answer**: "Vercel is ideal for rapid iteration and developer experience — `vercel --prod` deploys in seconds, it handles HTTPS and CDN automatically, and the free tier is generous. I'd choose it for prototyping, demos, and small-scale production. AWS App Runner gives me container-level control — I can specify exact CPU/memory, run persistent instances without cold starts, and integrate with other AWS services. I'd choose it for production workloads where I need predictable performance, longer timeout windows (Vercel has a 60-second limit), or compliance requirements that mandate a specific cloud provider. Demonstrating both shows I can work with serverless and container paradigms."

---

## What NOT to Say in an Interview

- "I just followed a tutorial" — Frame it as "I built this as part of a structured capstone, making decisions about architecture and trade-offs along the way"
- "It's HIPAA compliant" — Be honest: "The architecture supports HIPAA compliance with additional hardening, but the current implementation does not include all required controls"
- "It uses AI" (as the selling point) — Lead with the engineering: "The interesting part is not the AI call — it's the streaming pipeline, authentication, and dual deployment architecture"
- "It works perfectly" — Show maturity: "Here are the known limitations and what I would prioritize improving"
