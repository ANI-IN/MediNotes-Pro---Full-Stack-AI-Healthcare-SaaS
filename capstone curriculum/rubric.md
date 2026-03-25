# Evaluation Rubric — MediNotes Pro Capstone

## Quick Reference Scoring

| Grade | Score Range | Description |
|-------|-----------|-------------|
| **A** | 3.5 – 4.0 | Exceeds expectations; production-quality with enhancements |
| **B** | 2.5 – 3.4 | Meets all requirements; solid implementation |
| **C** | 1.5 – 2.4 | Approaching; most features work, notable gaps |
| **F** | Below 1.5 | Below expectations; major components non-functional |

## Detailed Rubric

### 1. Functionality (30% weight)

| Score | Criteria |
|-------|----------|
| **4 — Exceeds** | All 5 milestones complete AND at least 2 enhancements (e.g., copy button, history, "new consultation" button, error messages, loading animations). Application handles edge cases gracefully. |
| **3 — Meets** | All 5 milestones fully functional. User can sign in, subscribe, fill the form, see streaming output, and the app is deployed to at least one platform. |
| **2 — Approaching** | 4 of 5 milestones complete. One milestone has issues (e.g., auth works but subscription doesn't, or Docker builds but AWS deploy fails). |
| **1 — Below** | Fewer than 4 milestones. Core functionality (form → streaming output) may be broken. |

### 2. Code Quality (20% weight)

| Score | Criteria |
|-------|----------|
| **4 — Exceeds** | TypeScript used with strict types (no `any`). Python functions have docstrings. Consistent naming conventions. No dead code. Clear separation between components. Linting passes cleanly. |
| **3 — Meets** | TypeScript used correctly. Pydantic models are defined. Code is readable and follows project conventions. Minor style inconsistencies acceptable. |
| **2 — Approaching** | Mix of typed and untyped code. Some copied code without understanding. Unused imports or variables. Inconsistent formatting. |
| **1 — Below** | No TypeScript types. Functions are overly long. Copy-paste without adaptation. Code doesn't follow project structure. |

### 3. Architecture Understanding (15% weight)

| Score | Criteria |
|-------|----------|
| **4 — Exceeds** | Can explain every architecture decision and its trade-offs. Has identified and addressed at least one gap (e.g., added backend subscription check, improved error handling). Can propose a scaling strategy. |
| **3 — Meets** | Understands the data flow end-to-end: form → JWT → FastAPI → OpenAI → SSE → Markdown. Can explain why SSE was chosen over WebSockets. Knows why static export is used for AWS. |
| **2 — Approaching** | Can describe what each component does but struggles to explain why. Cannot articulate trade-offs or what would change at scale. |
| **1 — Below** | Cannot trace a request through the system. Doesn't understand the role of JWT or why JWKS verification exists. |

### 4. Security Awareness (10% weight)

| Score | Criteria |
|-------|----------|
| **4 — Exceeds** | Added backend subscription verification. Input validation with length limits. CORS restricted to production domain. Can discuss prompt injection risks and mitigations. |
| **3 — Meets** | JWT authentication works. Secrets in environment variables (not hardcoded). HTTPS enforced. Understands the frontend-only subscription gap. |
| **2 — Approaching** | Auth works but cannot explain JWT verification flow. Secrets are in env vars but might have committed them previously. |
| **1 — Below** | Secrets hardcoded in source. Auth not functioning. Does not understand the security model. |

### 5. Deployment (15% weight)

| Score | Criteria |
|-------|----------|
| **4 — Exceeds** | Both Vercel and AWS deployments working. Health checks pass. Budget alerts configured. Docker image optimized (small size, multi-stage verified). Can deploy updates reliably. |
| **3 — Meets** | At least one deployment target fully working with HTTPS. Environment variables configured correctly. Application accessible at a public URL. |
| **2 — Approaching** | Deployment partially works (e.g., static pages load but API fails). Or only works locally in Docker but not on AWS. |
| **1 — Below** | Application only runs on localhost. No deployment to any platform. |

### 6. Documentation (10% weight)

| Score | Criteria |
|-------|----------|
| **4 — Exceeds** | Comprehensive README with architecture diagram, setup instructions, API reference, trade-offs, and future improvements. Additional docs in `/docs` folder. `.env.example` provided. |
| **3 — Meets** | README includes project overview, setup instructions, tech stack, and how to run. Environment variables documented. |
| **2 — Approaching** | README exists but minimal (just a project title and basic setup). Missing key information like environment variable list. |
| **1 — Below** | No README or only the auto-generated Next.js README. |

## Score Calculation

```
Final Score = (Functionality × 0.30) + (Code Quality × 0.20) + (Architecture × 0.15)
            + (Security × 0.10) + (Deployment × 0.15) + (Documentation × 0.10)

Example — Meets all criteria:
  = (3 × 0.30) + (3 × 0.20) + (3 × 0.15) + (3 × 0.10) + (3 × 0.15) + (3 × 0.10)
  = 0.90 + 0.60 + 0.45 + 0.30 + 0.45 + 0.30
  = 3.00 (B — Meets expectations)
```

## Milestone Checklist (Quick Verification)

### Milestone 1: Hello Production
- [ ] Public URL returns a response
- [ ] Response includes AI-generated content
- [ ] API key is NOT in source code

### Milestone 2: Full-Stack Streaming
- [ ] React page renders in browser
- [ ] API call returns streaming response
- [ ] Markdown renders with formatting (headings, lists)
- [ ] Deployed to Vercel

### Milestone 3: Auth + Subscription
- [ ] Sign-in modal works
- [ ] Signed-in user sees different UI than signed-out
- [ ] API verifies JWT (test: call API without token → 401)
- [ ] Pricing table appears for unsubscribed users
- [ ] Subscribed users access the product

### Milestone 4: Healthcare Domain
- [ ] Form has name, date picker, notes fields
- [ ] API accepts POST (not GET)
- [ ] Output has three sections with correct headings
- [ ] Streaming works with form data

### Milestone 5: Docker + AWS
- [ ] `docker build` succeeds
- [ ] Container runs locally (http://localhost:8000 works)
- [ ] `/health` returns `{"status": "healthy"}`
- [ ] Image visible in ECR
- [ ] App Runner service shows "Running"
- [ ] Full flow works on AWS URL
- [ ] Budget alerts exist in AWS Billing
