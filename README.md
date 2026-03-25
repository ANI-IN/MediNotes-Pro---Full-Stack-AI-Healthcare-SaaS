# MediNotes Pro — AI-Powered Healthcare Consultation Assistant

> A production-grade, full-stack SaaS application that transforms raw doctor consultation notes into structured medical summaries, actionable next steps, and patient-friendly email drafts — streamed in real time via Server-Sent Events.

[![Tech Stack](https://img.shields.io/badge/Next.js-Pages_Router-black?logo=next.js)](https://nextjs.org/)
[![Backend](https://img.shields.io/badge/FastAPI-Python_3.12-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Auth](https://img.shields.io/badge/Clerk-JWT_Auth-6C47FF?logo=clerk)](https://clerk.com/)
[![AI](https://img.shields.io/badge/OpenAI-GPT--Streaming-412991?logo=openai)](https://openai.com/)
[![Deploy](https://img.shields.io/badge/AWS-App_Runner-FF9900?logo=amazonaws)](https://aws.amazon.com/apprunner/)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED?logo=docker)](https://docker.com/)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Why This Project Exists](#why-this-project-exists)
- [Target Users](#target-users)
- [Use Cases](#use-cases)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [End-to-End Workflow](#end-to-end-workflow)
- [Setup Instructions](#setup-instructions)
- [Running the Project](#running-the-project)
- [Sample Inputs and Outputs](#sample-inputs-and-outputs)
- [API Reference](#api-reference)
- [Deployment Overview](#deployment-overview)
- [Scaling Considerations](#scaling-considerations)
- [Security Considerations](#security-considerations)
- [Testing Strategy](#testing-strategy)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Learning Outcomes](#learning-outcomes)
- [Resume-Worthy Talking Points](#resume-worthy-talking-points)
- [Interview Discussion Points](#interview-discussion-points)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

MediNotes Pro is a full-stack SaaS application designed for healthcare professionals. A doctor enters consultation notes — patient name, visit date, and free-text clinical observations — and the system produces three distinct AI-generated outputs:

1. **A structured medical summary** suitable for electronic health records
2. **Actionable next steps** for the treating physician
3. **A patient-friendly email draft** that translates medical jargon into plain language

The application demonstrates end-to-end software engineering across every layer of the stack: a TypeScript/React frontend with Tailwind CSS, a Python/FastAPI backend with streaming responses, JWT-based authentication via Clerk, subscription billing, multi-stage Docker builds, and dual deployment paths (Vercel serverless and AWS App Runner containers).

The project was built incrementally across five development stages, each adding a production-relevant capability — from a single API endpoint to a fully authenticated, subscription-gated, containerized cloud deployment.

---

## Problem Statement

Physicians spend an estimated 16 minutes per patient encounter on documentation tasks. After a consultation, the doctor must:

1. Write a formal summary for the patient's medical record
2. Identify and document follow-up actions, referrals, and prescriptions
3. Compose a patient-facing communication that explains the visit in non-clinical language

These three outputs serve different audiences (medical records, clinical staff, and patients) and require different writing registers. Doing this manually for every consultation is time-consuming, repetitive, and error-prone — particularly under the time pressure of a busy clinic.

**The core engineering challenge** is not just calling an LLM. It is building a secure, streaming, authenticated, subscription-gated SaaS platform that a healthcare practice could realistically adopt — with proper secrets management, JWT verification, real-time response delivery, and cloud-native deployment.

---

## Why This Project Exists

This project exists at the intersection of three important engineering themes:

**1. AI Integration as a System Design Problem.** Calling an LLM API is trivial. Building a production system around it — with streaming, authentication, error handling, and deployment — is where the real engineering lies. This project forces you to solve those integration problems end-to-end.

**2. Full-Stack SaaS as a Capstone Vehicle.** The application touches every layer a working engineer encounters: frontend state management, backend API design, authentication and authorization, subscription billing, containerization, and cloud deployment. It is a single project that exercises the complete stack.

**3. Healthcare as a High-Stakes Domain.** Healthcare imposes real constraints — data sensitivity, auditability, structured output requirements — that generic demo apps ignore. Building for healthcare forces you to think about security, validation, and reliability in ways that make the project interview-worthy.

---

## Target Users

| Persona | Description | How They Use MediNotes Pro |
|---------|-------------|---------------------------|
| **General Practitioner** | Sees 20-30 patients daily, writes notes quickly between appointments | Enters shorthand notes, receives structured documentation instantly |
| **Specialist Physician** | Handles complex cases requiring detailed summaries | Uses generated summaries as a starting point, edits for accuracy |
| **Clinic Administrator** | Manages patient communications and record-keeping | Uses patient email drafts to standardize outreach |
| **Medical Resident** | Learning documentation practices | Uses generated outputs as templates for proper medical writing |

---

## Use Cases

### Primary: Post-Consultation Documentation

Dr. Patel finishes a 15-minute appointment with a patient experiencing persistent cough. She opens MediNotes Pro, enters the patient name and date, types her shorthand notes, and clicks Generate. Within seconds, three formatted sections stream onto her screen — a formal summary, a checklist of next steps, and a patient email she can review and send.

### Secondary Use Cases

- **Shift Handoff Documentation**: Outgoing physician generates structured summaries for incoming staff.
- **Multi-Language Patient Communication**: Prompt engineering can target different languages for patient emails.
- **Audit Trail Generation**: Each request is tied to an authenticated user ID, enabling usage tracking.
- **Specialty-Specific Templates**: The system prompt can be parameterized per medical specialty.

---

## Key Features

| Feature | Description | Technical Implementation |
|---------|-------------|------------------------|
| **Structured AI Output** | Three-section medical document generation | System prompt engineering with explicit section headings |
| **Real-Time Streaming** | Token-by-token response delivery via SSE | FastAPI `StreamingResponse` + `fetchEventSource` |
| **JWT Authentication** | Every API request cryptographically verified | Clerk JWKS verification via `fastapi-clerk-auth` |
| **Subscription Gating** | Product access requires active paid subscription | Clerk `<Protect>` component with `PricingTable` fallback |
| **Multi-Provider Auth** | Google, GitHub, Email, Apple sign-in | Clerk managed authentication with modal sign-in |
| **Markdown Rendering** | Rich output formatting with headings, lists, emphasis | `react-markdown` + `remark-gfm` + `remark-breaks` |
| **Form Validation** | Client and server-side input validation | HTML5 required attributes + Pydantic `BaseModel` |
| **Date Handling** | Professional date picker with ISO formatting | `react-datepicker` with `yyyy-MM-dd` format |
| **Static Export** | Frontend compiled to static HTML/JS/CSS | Next.js `output: 'export'` for container deployment |
| **Multi-Stage Docker Build** | Optimized container with separate build/runtime stages | Node.js builder → Python slim runtime |
| **Dual Deployment** | Both serverless and container deployment paths | Vercel (serverless) and AWS App Runner (container) |
| **Health Check Endpoint** | Container health monitoring | `/health` endpoint for App Runner probes |
| **CORS Configuration** | Cross-origin request handling | FastAPI `CORSMiddleware` |
| **Cost Controls** | AWS budget alerts at $1, $5, $10 thresholds | CloudWatch Budget notifications |
| **Dark Mode Support** | Responsive UI with dark mode | Tailwind `dark:` variant classes |

---

## System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      CLIENT (Browser)                        │
│                                                              │
│  Landing Page ──► Clerk Auth Modal ──► Subscription Gate     │
│       │                  │                    │              │
│       ▼                  ▼                    ▼              │
│  index.tsx          Clerk.js SDK         product.tsx         │
│  (public)        (JWT + sessions)     (protected form)      │
└──────────────────────────┬───────────────────────────────────┘
                           │ POST + Bearer JWT + JSON body
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  JWT Verification (fastapi-clerk-auth + JWKS)          │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐  │
│  │  Consultation Endpoint                                 │  │
│  │  - Pydantic validation (Visit model)                   │  │
│  │  - Prompt construction (system + user)                 │  │
│  │  - OpenAI streaming completion                         │  │
│  │  - SSE event formatting + StreamingResponse            │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐  │
│  │  Static File Server (AWS mode only)                    │  │
│  │  - Next.js exported HTML/JS/CSS                        │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
          │                              │
          ▼                              ▼
   ┌─────────────┐              ┌──────────────┐
   │ OpenAI API  │              │ Clerk JWKS   │
   │ (streaming) │              │ (public keys)│
   └─────────────┘              └──────────────┘
```

### Deployment Comparison

| Aspect | Vercel | AWS App Runner |
|--------|--------|----------------|
| Frontend | Vercel Edge CDN | FastAPI StaticFiles in container |
| Backend | Vercel Python Serverless | FastAPI in Docker container |
| Routing | Automatic (`/api` → Python) | Single container serves all |
| HTTPS | Automatic | Automatic |
| Scaling | Auto (serverless) | Configurable (min/max instances) |
| Cold Start | Yes (serverless) | No (persistent instance) |
| Cost | Free tier available | ~$5-10/month minimum |

See [docs/architecture.md](docs/architecture.md) for Mermaid sequence diagrams.

---

## Tech Stack

| Layer | Technology | Why This Choice |
|-------|-----------|-----------------|
| **Frontend Framework** | Next.js 14 (Pages Router) | Battle-tested routing, static export support, TypeScript-first |
| **Language (Frontend)** | TypeScript | Type safety, better IDE support, catches errors at compile time |
| **Styling** | Tailwind CSS + Typography plugin | Utility-first CSS, rapid prototyping, built-in dark mode |
| **Markdown Rendering** | react-markdown + remark-gfm | Renders streaming markdown incrementally, supports tables and lists |
| **Date Input** | react-datepicker | Accessible, customizable, ISO format support |
| **SSE Client** | @microsoft/fetch-event-source | Supports POST with SSE (native EventSource is GET-only) |
| **Backend Framework** | FastAPI | Async-ready, Pydantic validation, streaming response support |
| **Language (Backend)** | Python 3.12 | OpenAI SDK ecosystem, Pydantic integration, wide library support |
| **AI Provider** | OpenAI API (streaming) | Token-by-token streaming, structured prompt support |
| **Authentication** | Clerk | Managed auth with JWT, multi-provider, subscription billing |
| **JWT Verification** | fastapi-clerk-auth | JWKS-based verification without per-request Clerk API calls |
| **Containerization** | Docker (multi-stage) | Reproducible builds, separate build and runtime concerns |
| **Serverless Deploy** | Vercel | Zero-config Next.js + Python, automatic HTTPS |
| **Container Deploy** | AWS App Runner + ECR | Managed container hosting, auto-scaling, health checks |
| **Cost Monitoring** | AWS Budgets + CloudWatch | Threshold alerts, prevents runaway spending |

---

## Repository Structure

```
medinotes-pro/
│
├── README.md                       # This file
├── package.json                    # Node.js dependencies
├── tsconfig.json                   # TypeScript configuration
├── next.config.ts                  # Next.js config (static export for AWS)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Multi-stage build (Node + Python)
├── .dockerignore                   # Docker build exclusions
├── .gitignore                      # Git exclusions
├── .env.local                      # Local secrets (git-ignored)
├── .env.example                    # Template for required env vars
│
├── pages/                          # Next.js Pages Router
│   ├── _app.tsx                    # ClerkProvider wrapper, global CSS
│   ├── _document.tsx               # HTML structure, meta tags
│   ├── index.tsx                   # Landing page (auth + pricing)
│   └── product.tsx                 # Protected consultation form
│
├── styles/
│   └── globals.css                 # Tailwind imports + markdown styles
│
├── api/                            # FastAPI backend
│   ├── index.py                    # Vercel-compatible endpoint
│   └── server.py                   # AWS-compatible server
│
├── public/                         # Static assets
│
├── docs/                           # Documentation suite
│   ├── project-overview.md
│   ├── problem-statement.md
│   ├── use-cases.md
│   ├── architecture.md
│   ├── data-flow.md
│   ├── setup-guide.md
│   ├── deployment-guide.md
│   ├── testing-guide.md
│   ├── security-considerations.md
│   ├── scaling-and-production-readiness.md
│   ├── trade-offs-and-design-decisions.md
│   ├── future-roadmap.md
│   ├── capstone-curriculum.md
│   ├── gap-analysis.md
│   └── resume-and-interview-guide.md
│
├── tests/                          # Test suite (recommended)
│   ├── backend/
│   │   ├── test_api.py
│   │   ├── test_models.py
│   │   └── test_prompts.py
│   └── frontend/
│       └── __tests__/
│
└── examples/                       # Sample data
    ├── sample-input.json
    └── sample-output.md
```

---

## End-to-End Workflow

1. **Landing Page** → User arrives, sees product pitch and pricing preview
2. **Authentication** → User clicks "Sign In", authenticates via Clerk (Google/GitHub/Email)
3. **Subscription Gate** → Clerk `<Protect>` checks subscription status on `/product`
4. **Pricing Table** → If no subscription, `<PricingTable>` renders with payment options
5. **Consultation Form** → Subscribed user sees form: patient name, date picker, notes textarea
6. **Form Submission** → Client POSTs JSON body + JWT to `/api` (or `/api/consultation`)
7. **JWT Verification** → Backend verifies token signature against Clerk JWKS public keys
8. **Prompt Construction** → System prompt (format instructions) + user prompt (patient data)
9. **Streaming Response** → OpenAI streams tokens → FastAPI formats SSE → Client renders incrementally
10. **Output Display** → Three markdown sections: summary, next steps, patient email

---

## Setup Instructions

### Prerequisites

| Requirement | Version | Purpose |
|------------|---------|---------|
| Node.js | 18+ | Next.js build and npm |
| Python | 3.9 - 3.12 | FastAPI backend |
| Docker Desktop | 26+ | Container builds (AWS path) |
| AWS CLI | 2+ | ECR push (AWS path) |
| Vercel CLI | Latest | Vercel deployment path |

### Environment Variables

Create `.env.local` in the project root (see `.env.example` for template):

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_JWKS_URL=https://...clerk.accounts.dev/.well-known/jwks.json

# AWS (container deployment only)
DEFAULT_AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
```

### Local Development (Vercel Path)

```bash
git clone https://github.com/your-username/medinotes-pro.git
cd medinotes-pro
npm install
pip install -r requirements.txt
# Add your .env.local
npx vercel dev
```

### Local Development (Docker Path)

```bash
export $(cat .env.local | grep -v '^#' | xargs)

docker build \
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" \
  -t medinotes-pro .

docker run -p 8000:8000 \
  -e CLERK_SECRET_KEY="$CLERK_SECRET_KEY" \
  -e CLERK_JWKS_URL="$CLERK_JWKS_URL" \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  medinotes-pro
```

---

## Running the Project

### Vercel Production Deployment

```bash
vercel env add OPENAI_API_KEY
vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
vercel env add CLERK_SECRET_KEY
vercel env add CLERK_JWKS_URL
vercel --prod
```

### AWS Production Deployment

```bash
# Authenticate, build, tag, push to ECR
aws ecr get-login-password --region $DEFAULT_AWS_REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com

docker build --platform linux/amd64 \
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" \
  -t medinotes-pro .

docker tag medinotes-pro:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com/medinotes-pro:latest

docker push \
  $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com/medinotes-pro:latest
# Then deploy via App Runner console
```

---

## Sample Inputs and Outputs

### Input

```json
{
  "patient_name": "Jane Smith",
  "date_of_visit": "2025-03-15",
  "notes": "Patient presents with persistent cough for 2 weeks. No fever. Chest clear on examination. Blood pressure 120/80. Likely viral bronchitis. Prescribed rest and fluids. Follow up if symptoms persist beyond another week."
}
```

### Output (Streamed as Markdown)

```markdown
### Summary of visit for the doctor's records

Jane Smith presented on March 15, 2025, with a two-week history of persistent
cough. She was afebrile with clear lung fields on auscultation. Blood pressure
was within normal limits at 120/80 mmHg. Clinical assessment is consistent with
viral bronchitis. Conservative management was recommended.

### Next steps for the doctor

- Schedule follow-up appointment in 7-10 days if symptoms persist
- Order chest X-ray if cough continues beyond 3 weeks
- Consider sputum culture if productive cough develops
- Document in patient record: viral bronchitis, conservative management

### Draft of email to patient in patient-friendly language

Dear Jane,

Thank you for visiting us today. Based on our examination, your cough appears
to be caused by a common viral infection (bronchitis). The good news is that
your lungs sound clear and your blood pressure is healthy.

Here is what we recommend:
- Get plenty of rest and stay well hydrated
- If your cough has not improved within a week, please schedule a follow-up
- If you develop a fever or difficulty breathing, contact us right away

Best regards,
Your Healthcare Team
```

---

## API Reference

### `POST /api` (Vercel) or `POST /api/consultation` (AWS)

Generates structured consultation summary from doctor notes.

**Headers:**
| Header | Value |
|--------|-------|
| `Authorization` | `Bearer <clerk-jwt>` |
| `Content-Type` | `application/json` |

**Request Body (Pydantic `Visit` model):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `patient_name` | string | Yes | Full patient name |
| `date_of_visit` | string | Yes | ISO date (YYYY-MM-DD) |
| `notes` | string | Yes | Free-text consultation notes |

**Response:** `text/event-stream` (SSE)

**Error Codes:**
| Status | Meaning |
|--------|---------|
| 401 | Missing or invalid JWT |
| 403 | Expired JWT or invalid signature |
| 422 | Pydantic validation failure |
| 500 | OpenAI API or server error |

### `GET /health` (AWS only)

Returns `{"status": "healthy"}` for App Runner health probes.

---

## Deployment Overview

**Vercel**: Auto-detects Next.js + Python. Environment variables via `vercel env add`. Zero-config HTTPS and CDN.

**AWS App Runner**: Single Docker container (multi-stage build). FastAPI serves static frontend + API. ECR for image storage. Manual deploy or CI/CD. Minimum 1 persistent instance.

See [docs/deployment-guide.md](docs/deployment-guide.md) for comprehensive instructions.

---

## Scaling Considerations

| Dimension | Current State | Production Path |
|-----------|--------------|-----------------|
| Horizontal Scaling | Single instance (max=1) | Increase max, add auto-scaling |
| Database | None (stateless) | PostgreSQL via RDS |
| Caching | None | Redis for JWT key caching |
| CDN | Vercel Edge only | CloudFront for AWS path |
| Rate Limiting | None | Per-user middleware |
| Queue Processing | Synchronous | SQS + async workers |

---

## Security Considerations

**Implemented:** JWT via JWKS, environment variable isolation, HTTPS enforcement, Pydantic validation, user isolation via JWT `sub` claim, public key safety (`pk_` prefix).

**Not Yet Implemented:** HIPAA compliance, rate limiting, input sanitization, audit logging, data retention policies, encryption at rest, penetration testing.

See [docs/security-considerations.md](docs/security-considerations.md) for full analysis.

---

## Testing Strategy

No test suite currently exists. Recommended approach:

| Layer | Tool | Focus |
|-------|------|-------|
| Backend Unit | pytest | Model validation, prompt construction, SSE format |
| Backend Integration | pytest + httpx | Auth rejection, streaming, error responses |
| Frontend Unit | Jest + RTL | Component rendering, form validation |
| E2E | Playwright | Full auth → form → streaming flow |
| Load | k6 or Locust | Concurrent streaming connections |

See [docs/testing-guide.md](docs/testing-guide.md) for implementation details.

---

## Limitations

1. **No persistent storage** — results not saved, no database
2. **No test suite** — no automated tests
3. **No CI/CD** — manual CLI deployments
4. **No retry logic** — incomplete responses on OpenAI failure
5. **No rate limiting** — unlimited API calls per user
6. **No input sanitization** — notes pass directly to LLM
7. **No audit logging** — no request logging for compliance
8. **No error boundaries** — React errors crash without fallback
9. **HIPAA not implemented** — landing page claim is aspirational
10. **Single AI model** — hardcoded to `gpt-5-nano`, no fallback

---

## Future Improvements

**Short Term**: Test suite, error boundaries, retry logic, rate limiting, CI/CD pipeline.

**Medium Term**: PostgreSQL for history, specialty-specific prompts, PDF export, audit logging.

**Long Term**: Multi-language emails, voice-to-text input, EHR integration (FHIR), HIPAA compliance, multi-tenant architecture.

See [docs/future-roadmap.md](docs/future-roadmap.md) for detailed roadmap.

---

## Learning Outcomes

| Skill | What You Practiced |
|-------|-------------------|
| Full-Stack Architecture | React frontend ↔ Python backend across two deployment models |
| TypeScript + React | State management, effects, forms, conditional rendering |
| API Design | REST endpoints, validation, streaming responses |
| Auth and Authz | JWT with JWKS, subscription gating |
| AI/LLM Integration | Prompt engineering, streaming, structured output |
| Server-Sent Events | SSE implementation and consumption |
| Containerization | Multi-stage Docker builds |
| Cloud Deployment | Vercel (serverless) and AWS App Runner (container) |
| Security | Secrets management, CORS, JWT, input validation |
| Cost Engineering | AWS budgets, resource sizing |

---

## Resume-Worthy Talking Points

> **MediNotes Pro** — Full-stack SaaS healthcare consultation assistant
> - Built streaming AI application with Next.js (TypeScript), FastAPI (Python), and OpenAI generating structured medical documentation from free-text notes
> - Implemented JWT authentication with Clerk including JWKS backend verification and subscription-gated access
> - Designed real-time SSE delivery with incremental Markdown rendering
> - Containerized with multi-stage Docker and deployed to Vercel (serverless) and AWS App Runner (container) with ECR
> - Configured AWS cost controls maintaining less than $10/month operational cost

---

## Interview Discussion Points

See [docs/resume-and-interview-guide.md](docs/resume-and-interview-guide.md) for 25+ questions with suggested answers. Key topics: SSE vs WebSockets trade-off, JWT/JWKS auth flow, dual deployment rationale, HIPAA gap analysis, failure handling strategy.

---

## Contributing

1. Fork the repository and create a feature branch
2. Follow existing code style (TypeScript frontend, Python backend)
3. Add tests for new functionality
4. Update documentation for behavior changes
5. Submit a pull request with clear description

---

## License

This project is provided for educational purposes as part of a software engineering capstone curriculum.
