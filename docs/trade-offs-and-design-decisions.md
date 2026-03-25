# Trade-offs and Design Decisions

## Decision 1: Pages Router vs App Router

**Choice**: Next.js Pages Router

**Alternatives Considered**: Next.js App Router (recommended by Next.js docs)

**Why Pages Router**: The Pages Router is stable and battle-tested. The App Router introduced server components, streaming, and new data fetching patterns that add complexity without benefit for this use case — all our components are client-side (`"use client"`), and the backend is a separate Python server. The Clerk SDK also had version compatibility issues with newer patterns (v7 removed `SignedIn`/`SignedOut` components that v6 supports).

**Trade-off**: We miss out on React Server Components and built-in streaming, but gain simplicity, stability, and compatibility with static export.

---

## Decision 2: fetchEventSource vs Native EventSource

**Choice**: `@microsoft/fetch-event-source`

**Why Not Native EventSource**: The browser's built-in `EventSource` API only supports GET requests. Our consultation endpoint requires POST (to send the JSON body with patient data and the JWT token). `fetchEventSource` supports POST, custom headers, and provides `onmessage`, `onerror` callbacks.

**Trade-off**: Additional dependency (~15KB), but it solves a fundamental API limitation that would otherwise require restructuring the endpoint (e.g., query string encoding of patient data, which is impractical).

---

## Decision 3: Static Export vs Server-Side Rendering

**Choice**: `output: 'export'` for AWS, standard build for Vercel

**Why Static Export for AWS**: Serving static files from FastAPI's `StaticFiles` middleware means a single container handles everything. No need for a separate Node.js process, no need for two containers, no need for a reverse proxy. This reduces operational complexity significantly.

**Why Not Static Export for Vercel**: Vercel handles Next.js natively — it knows how to serve pages and route to Python serverless functions. Static export would remove Vercel's optimization capabilities.

**Trade-off**: Static export means no server-side rendering, no ISR, no API routes within Next.js. All rendering is client-side. For this application (a form that calls a Python backend), this is acceptable.

---

## Decision 4: Single Container vs Microservices

**Choice**: Single Docker container running FastAPI (serves both API and static files)

**Why Not Separate Containers**: At this stage, separating frontend and backend into two containers adds operational complexity (two ECR images, two App Runner services, cross-origin configuration, two deployment pipelines) without meaningful benefit. The application is simple enough that a single container is the right choice.

**Trade-off**: Frontend and backend deploy together. A CSS change requires a full container rebuild. At scale, you would separate them — serve static files from S3/CloudFront and the API from its own container.

---

## Decision 5: Clerk vs Custom Auth (Passport.js, Auth0, etc.)

**Choice**: Clerk for authentication and billing

**Why Clerk**: Clerk provides authentication, user management, and subscription billing as a single integrated service. The Clerk React SDK (`@clerk/nextjs`) offers components (`<SignInButton>`, `<Protect>`, `<PricingTable>`) that handle complex UI flows with minimal code. The backend library (`fastapi-clerk-auth`) handles JWT verification with JWKS.

**Why Not Auth0**: Auth0 is more established but does not include billing. Would need to integrate Stripe separately, adding another integration point.

**Why Not Custom Auth**: Building JWT issuance, session management, OAuth flows, and billing from scratch would be a project in itself. This is a documentation tool, not an auth system.

**Trade-off**: Vendor lock-in. If Clerk changes pricing or discontinues, migrating requires replacing auth components, JWT verification, and billing. The JWT standard itself is portable, but the SDK integration is not.

---

## Decision 6: Streaming vs Request-Response

**Choice**: Server-Sent Events for real-time streaming

**Why Streaming**: LLM responses take 5-20 seconds to generate fully. Without streaming, the user stares at a loading spinner for the entire duration. With streaming, tokens appear in real time, giving immediate feedback and allowing the user to start reading before generation completes.

**Why SSE over WebSockets**: SSE is simpler (unidirectional, server-to-client), works over standard HTTP, and naturally fits the LLM streaming pattern. WebSockets would add bidirectional communication complexity that we do not need — the client sends one request and receives a stream of responses.

**Trade-off**: SSE connections are long-lived. Each streaming response occupies a connection for 10-30 seconds. This limits per-instance concurrency more than quick request-response endpoints would.

---

## Decision 7: Hardcoded System Prompt vs Configurable

**Choice**: Hardcoded system prompt in `api/index.py`

**Why Not Configurable**: For a single-purpose application (healthcare consultation summaries), the system prompt is part of the product definition, not a user-configurable setting. Making it configurable adds complexity (prompt storage, version management, A/B testing) without clear benefit at this stage.

**Trade-off**: Changing the output format requires a code change and redeployment. A prompt management system would allow non-engineers to iterate on output quality without deployments.

---

## Decision 8: No Database

**Choice**: Stateless design with no persistent storage

**Why**: Adding a database introduces significant complexity: schema design, migrations, connection management, backup, encryption at rest, and HIPAA considerations for healthcare data. For a capstone focused on the streaming pipeline and deployment, the database is a distraction from the core learning objectives.

**Trade-off**: No consultation history, no usage analytics, no audit trail. Users cannot retrieve past results. This is the most significant limitation of the current design and the most important future improvement.

---

## Decision 9: Pydantic Validation Only

**Choice**: Use Pydantic for request validation, no additional validation layer

**Why Not More Validation**: Pydantic handles type checking and required field enforcement. Additional validation (note length limits, date format verification, character restrictions) would add defensive depth but was not prioritized.

**Trade-off**: Empty strings pass validation. The `date_of_visit` field accepts any string, not just ISO dates. Medical notes are not length-limited. These are edge cases that should be addressed for production but are acceptable for a capstone.

---

## Decision 10: Manual Deployment vs CI/CD

**Choice**: Manual CLI-based deployment (`vercel --prod`, `docker push` + App Runner deploy)

**Why Not CI/CD**: Setting up GitHub Actions with ECR authentication, App Runner deployment, and environment variable management adds operational complexity. The focus of the project is on the application code and architecture, not on DevOps automation.

**Trade-off**: Every deployment requires manual steps, increasing the risk of deployment errors and making continuous delivery impossible. For a production service, CI/CD is essential.
