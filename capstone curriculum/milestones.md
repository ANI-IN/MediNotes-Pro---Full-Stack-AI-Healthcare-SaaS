# Milestones and Challenge Tiers — MediNotes Pro

## Project Milestones

### Milestone 1: "Hello, Production" (Day 1) — ~4 hours
**Goal**: Deploy a working API endpoint to production.

**Acceptance Criteria**:
- [ ] FastAPI endpoint returns a response at a public Vercel URL
- [ ] OpenAI integration returns dynamic AI-generated content
- [ ] `OPENAI_API_KEY` stored as environment variable (not in code)

**Key Skills**: Python, FastAPI basics, Vercel CLI, environment variables

---

### Milestone 2: Full-Stack with Streaming (Day 2) — ~8 hours
**Goal**: Build a React frontend connected to a Python backend with real-time streaming.

**Acceptance Criteria**:
- [ ] Next.js frontend renders in the browser with Tailwind styling
- [ ] Frontend calls FastAPI backend and displays the response
- [ ] AI response streams token-by-token via SSE (not all-at-once)
- [ ] Markdown renders with proper formatting (headings, lists, bold)
- [ ] Application deployed to Vercel with both frontend and backend working

**Key Skills**: Next.js Pages Router, TypeScript, SSE, `react-markdown`, Tailwind CSS

---

### Milestone 3: Authentication and Subscription (Day 3) — ~8 hours
**Goal**: Add enterprise-grade auth and subscription billing.

**Acceptance Criteria**:
- [ ] Unauthenticated users see a marketing landing page with sign-in button
- [ ] Clerk sign-in modal works with at least one OAuth provider
- [ ] Authenticated users see "Go to App" and `UserButton`
- [ ] API endpoint verifies JWT tokens (returns 401 for invalid/missing)
- [ ] Users without subscription see the `PricingTable`
- [ ] Subscribed users see the product page

**Key Skills**: OAuth, JWT, JWKS verification, Clerk SDK, subscription gating

---

### Milestone 4: Healthcare Domain (Day 4) — ~6 hours
**Goal**: Transform the app into a healthcare consultation assistant.

**Acceptance Criteria**:
- [ ] Consultation form has patient name, date picker, and notes textarea
- [ ] Form submits via POST (not GET)
- [ ] Backend validates the `Visit` model with Pydantic
- [ ] AI output has three distinct sections with correct headings (Summary, Next Steps, Email)
- [ ] Streaming works with POST body data
- [ ] Landing page reflects the healthcare theme

**Key Skills**: Form design, Pydantic, prompt engineering, domain-specific UX

---

### Milestone 5: Docker and AWS Deployment (Day 5) — ~10 hours
**Goal**: Containerize and deploy to AWS.

**Acceptance Criteria**:
- [ ] Docker image builds successfully with multi-stage Dockerfile
- [ ] Container runs locally and serves both API and static frontend on `:8000`
- [ ] `/health` endpoint returns `{"status": "healthy"}`
- [ ] Image pushed to ECR
- [ ] App Runner service is running and accessible via HTTPS
- [ ] Full flow works on AWS (sign in → form → streaming output)
- [ ] Budget alerts configured at $1, $5, $10

**Key Skills**: Docker, ECR, App Runner, IAM, health checks, cost management

---

## Challenge Tiers

### Beginner Challenges
For learners solidifying fundamentals:

1. **"Generate Again" button** — clear output and re-submit the form without page refresh
2. **Character counter** — show `{current}/{max}` below the notes textarea
3. **Display user email** — use Clerk's `useUser()` hook to show the logged-in user's email
4. **Loading spinner** — replace "Generating Summary..." text with an animated SVG spinner
5. **Mobile responsiveness** — verify and fix the layout on mobile viewport sizes (375px width)

### Intermediate Challenges
Require deeper architecture understanding:

1. **Backend subscription verification** — check JWT claims for subscription status on every API request
2. **Input validation hardening** — `max_length=10000` on notes, date format regex, error messages displayed in UI
3. **Copy-to-clipboard** — individual copy buttons for each of the three output sections
4. **Browser localStorage history** — persist the last 10 consultations in localStorage with a history sidebar
5. **Error handling** — display user-friendly error messages when API fails, OpenAI times out, or JWT expires
6. **5 backend unit tests** — pytest tests for prompt construction, Pydantic validation, health check

### Advanced Challenges (Stretch Goals)
For learners pushing beyond the baseline:

1. **PostgreSQL persistence** — add a database, store consultations, build a history page with server-rendered data
2. **CI/CD pipeline** — GitHub Actions: lint → test → Docker build → ECR push → App Runner deploy
3. **Rate limiting** — 10 requests/user/hour with clear error message; Redis-backed for multi-instance
4. **Specialty-specific prompts** — dropdown for medical specialty, load different system prompts per specialty
5. **PDF export** — generate downloadable PDF of the consultation summary (WeasyPrint or ReportLab)
6. **Voice input** — integrate Whisper API for dictation (browser MediaRecorder → audio upload → transcription)
7. **Structured logging** — `structlog` with JSON output, create a CloudWatch Logs Insights dashboard
8. **Playwright E2E tests** — automated tests for sign-in → form submission → output verification

### Bonus Extensions
For learners who finish early:

1. **Multi-language patient emails** — language selector, system prompt includes translation instruction
2. **Dark mode toggle** — user-controlled theme switching (CSS custom properties)
3. **Admin dashboard** — usage stats, user count, request volume (requires database)
4. **Webhook integration** — receive and process Clerk webhook events for subscription changes
5. **Custom domain** — configure a custom domain on App Runner with ACM certificate

---

## Common Mistakes

| # | Mistake | Symptom | Fix |
|---|---------|---------|-----|
| 1 | Missing `--platform linux/amd64` on Apple Silicon | "exec format error" on AWS | Add `--platform linux/amd64` to `docker build` |
| 2 | Using Clerk v7 instead of v6.39.0 | `SignedIn` / `SignedOut` not found | `npm install @clerk/nextjs@6.39.0` |
| 3 | Empty `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` build arg | Clerk modal fails silently | Load env vars before `docker build` |
| 4 | Confusing `api/index.py` vs `api/server.py` | Wrong endpoint paths | `index.py` = Vercel (`/api`); `server.py` = AWS (`/api/consultation`) |
| 5 | AWS free-tier sandbox | App Runner "needs subscription" error | Upgrade to full AWS account |
| 6 | Missing `IAMFullAccess` policy | Permission errors in later steps | Add policy to IAM group |
| 7 | No date picker CSS import | Unstyled date picker | Import CSS in `_app.tsx` |
| 8 | JWT expires during long OpenAI call | 403 error after ~60 seconds | See community JWT timeout fix |
| 9 | Committing `.env.local` to Git | Secrets exposed | Check `.gitignore` before pushing |
| 10 | CORS not configured for AWS | API calls blocked | Add `CORSMiddleware` in `server.py` |
