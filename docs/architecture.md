# Architecture — MediNotes Pro

## High-Level Architecture

MediNotes Pro follows a **client-rendered frontend + API backend** pattern with third-party services for authentication, billing, and AI inference.

```mermaid
graph TB
    subgraph Browser
        NX[Next.js Static Pages]
        CK[Clerk SDK]
        FES[fetchEventSource]
        RM[ReactMarkdown]
    end

    subgraph Backend
        API[POST /api/consultation]
        HC[GET /health]
        SF[StaticFiles - AWS mode]
        PV[Pydantic Validation]
        JV[JWT Verification]
    end

    subgraph External
        CL[Clerk Cloud]
        OA[OpenAI API]
    end

    NX -->|getToken| CK
    CK -->|JWT| CL
    CK -->|Bearer JWT| FES
    FES -->|POST with JWT| API
    API --> JV
    JV -->|Fetch JWKS| CL
    API --> PV
    API -->|stream=True| OA
    OA -->|SSE chunks| API
    API -->|text/event-stream| FES
    FES -->|buffer += data| RM
```

## Component Architecture

### Frontend Components — Next.js Pages Router

```mermaid
graph TD
    APP["_app.tsx — ClerkProvider + Global CSS"]
    DOC["_document.tsx — HTML Shell + Meta"]

    APP --> IDX["index.tsx — Landing Page"]
    APP --> PRD["product.tsx — Product Page"]

    IDX --> SO["SignedOut: SignInButton"]
    IDX --> SI["SignedIn: Go to App + UserButton"]

    PRD --> PT["Protect — plan check"]
    PT -->|No subscription| PRC["PricingTable fallback"]
    PT -->|Has subscription| CF["ConsultationForm"]

    CF --> DP[DatePicker]
    CF --> TA["TextArea — notes"]
    CF --> FE["fetchEventSource — SSE"]
    CF --> RMD[ReactMarkdown]
```

### Backend Components — FastAPI

```mermaid
graph TD
    REQ[Incoming Request] --> MW[CORS Middleware]
    MW --> RT{Route?}

    RT -->|POST /api/consultation| AUTH[ClerkHTTPBearer]
    RT -->|GET /health| HEALTH["Return status: healthy"]
    RT -->|"GET /*"| STATIC["StaticFiles — Next.js export"]

    AUTH -->|Verify JWT via JWKS| VAL[Pydantic Validation]
    VAL -->|Valid Visit model| PROMPT[Construct Prompt]
    PROMPT -->|system + user messages| OAI[OpenAI Streaming Call]
    OAI -->|Token chunks| SSE["StreamingResponse — SSE"]
    SSE -->|"data: text"| CLIENT[Browser]

    AUTH -->|Invalid JWT| E401[401 Unauthorized]
    VAL -->|Invalid body| E422[422 Validation Error]
```

## Deployment Architecture

### Vercel Deployment — Days 1 through 4

```mermaid
graph LR
    DEV[Developer] -->|vercel --prod| VC[Vercel Platform]
    VC --> FE_BUILD[Build Next.js]
    VC --> BE_DEPLOY[Deploy Python as Serverless Function]
    FE_BUILD --> CDN[Vercel CDN]
    BE_DEPLOY --> FUNC["Vercel Function — api/index.py"]
    CDN --> USER[User Browser]
    FUNC --> USER
```

### AWS Deployment — Day 5

```mermaid
graph LR
    DEV[Developer] -->|docker build| IMG[Docker Image]
    IMG -->|docker push| ECR[Amazon ECR]
    ECR -->|Pull on deploy| AR[AWS App Runner]

    AR --> CONTAINER[Container on port 8000]
    CONTAINER --> API_ROUTES[/api/consultation]
    CONTAINER --> HEALTH_EP[/health]
    CONTAINER --> STATIC_SRV["Static Files — Next.js export"]
```

### Docker Multi-Stage Build

```mermaid
graph TD
    subgraph Stage1["Stage 1: node 22 alpine"]
        S1A[COPY package files] --> S1B[npm ci]
        S1B --> S1C[COPY source files]
        S1C --> S1D[Set CLERK_PUBLISHABLE_KEY build arg]
        S1D --> S1E["npm run build — produces /app/out/"]
    end

    subgraph Stage2["Stage 2: python 3.12 slim"]
        S2A[COPY requirements.txt] --> S2B[pip install]
        S2B --> S2C[COPY api/server.py]
        S2C --> S2D["COPY static files from Stage 1"]
        S2D --> S2E[EXPOSE 8000]
        S2E --> S2F["uvicorn server:app --port 8000"]
    end

    Stage1 -->|Static files| Stage2
```

## Sequence Diagrams

### Authentication and Request Flow

```mermaid
sequenceDiagram
    participant U as User Browser
    participant C as Clerk
    participant FE as Frontend
    participant BE as Backend
    participant OA as OpenAI API

    U->>FE: Visit landing page
    FE-->>U: Render marketing page

    U->>C: Click Sign In via OAuth
    C-->>U: Session established

    U->>FE: Navigate to /product
    FE->>FE: Protect component checks subscription

    alt No subscription
        FE-->>U: Show PricingTable
        U->>C: Subscribe to premium plan
        C-->>U: Subscription activated
    end

    U->>FE: Fill form and click Generate Summary
    FE->>C: Call getToken
    C-->>FE: JWT signed with RS256

    FE->>BE: POST /api/consultation with Bearer JWT
    BE->>C: Fetch JWKS public keys
    C-->>BE: RSA public keys
    BE->>BE: Verify JWT signature and expiry
    BE->>BE: Validate Visit model with Pydantic
    BE->>OA: Streaming completions request

    loop Token streaming
        OA-->>BE: Chunk with delta content
        BE-->>FE: SSE data event
        FE->>FE: Append to buffer and re-render Markdown
    end

    FE-->>U: Display complete summary with 3 sections
```

### Subscription State Flow

```mermaid
stateDiagram-v2
    [*] --> Unauthenticated: Visit site
    Unauthenticated --> Authenticated: Sign in via Clerk
    Authenticated --> SubscriptionCheck: Navigate to /product

    SubscriptionCheck --> PricingTable: No subscription
    SubscriptionCheck --> ProductAccess: Has subscription

    PricingTable --> PaymentFlow: Click Subscribe
    PaymentFlow --> ProductAccess: Payment successful
    PaymentFlow --> PricingTable: Payment failed

    ProductAccess --> ConsultationForm: Render form
    ConsultationForm --> StreamingOutput: Submit
    StreamingOutput --> ConsultationForm: Generate again

    Authenticated --> Unauthenticated: Sign out
```

## Data Flow Summary

```mermaid
flowchart LR
    A["Doctor Notes"] -->|JSON POST| B["JWT Verify"]
    B -->|Valid| C["Pydantic"]
    C --> D["OpenAI"]
    D -->|Stream| E["SSE"]
    E -->|Token by token| F["Markdown"]
    F --> G["Doctor Reviews"]

    B -->|Invalid| X1["401 Error"]
    C -->|Invalid| X2["422 Error"]
```

## Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Pages Router over App Router | Pages Router | More stable, better community support, simpler mental model for client-side rendering |
| Client-side rendering | "use client" on all pages | Direct browser-to-API calls without Next.js middleware; simpler for Python backend |
| Static export for AWS | output: export | Eliminates Node.js server dependency; everything served from Python container |
| Single container | FastAPI serves API + static files | Simpler deployment; one port, one health check, one scaling unit |
| SSE over WebSockets | Server-Sent Events | Unidirectional server-to-client fits LLM streaming; simpler than WebSocket lifecycle |
| Clerk over Auth0/NextAuth | Clerk | Integrated billing, UI components, JWKS endpoint; minimal configuration |
| Pydantic over manual parsing | Pydantic BaseModel | Automatic validation, type coercion, clear error messages, OpenAPI schema generation |
| Manual deployment | CLI-based push | Appropriate for learning; CI/CD is a recommended enhancement |
