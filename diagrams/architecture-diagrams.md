# Architecture Diagrams — MediNotes Pro

All diagrams are written in Mermaid syntax. Render them using:
- GitHub — auto-renders in `.md` files
- [mermaid.live](https://mermaid.live)
- VS Code with Mermaid extension

---

## 1. High-Level System Architecture

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
        SF[Static File Server]
        PV[Pydantic Validation]
        JV[JWT Verification]
    end

    subgraph External
        CL[Clerk Cloud - Auth + Billing]
        OA[OpenAI API - gpt-5-nano]
    end

    NX -->|getToken| CK
    CK -->|JWT| CL
    FES -->|POST with Bearer JWT| API
    API --> JV
    JV -->|Fetch JWKS| CL
    API --> PV
    API -->|stream=True| OA
    OA -->|SSE chunks| API
    API -->|text/event-stream| FES
    FES -->|buffer += data| RM
```

---

## 2. Authentication Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant CK as Clerk Cloud
    participant F as FastAPI
    participant O as OpenAI API

    U->>B: Click Sign In
    B->>CK: OAuth or Email flow
    CK-->>B: Session established

    U->>B: Submit consultation form
    B->>CK: Request JWT token
    CK-->>B: JWT signed with RS256

    B->>F: POST /api/consultation with Bearer JWT
    F->>CK: GET JWKS endpoint
    CK-->>F: Public keys for RSA
    F->>F: Verify JWT signature and expiry
    F->>F: Validate Visit model via Pydantic
    F->>O: Streaming completions request
    loop For each token
        O-->>F: Chunk with delta content
        F-->>B: SSE data event
        B->>B: Render Markdown incrementally
    end
```

---

## 3. Frontend Component Tree

```mermaid
graph TD
    APP["_app.tsx — ClerkProvider"]
    DOC["_document.tsx — HTML + Meta"]

    APP --> IDX["pages/index.tsx — Landing Page"]
    APP --> PRD["pages/product.tsx — Product Page"]

    IDX --> SO["SignedOut: Sign In Button"]
    IDX --> SI["SignedIn: Go to App + UserButton"]

    PRD --> UB["UserButton — Top Right"]
    PRD --> PT["Protect plan=premium_subscription"]
    PT -->|No sub| PRC["PricingTable"]
    PT -->|Has sub| CF["ConsultationForm"]

    CF --> INP[Patient Name Input]
    CF --> DP[DatePicker]
    CF --> TA[Notes Textarea]
    CF --> BTN[Submit Button]
    CF --> OUT[Output Section]
    OUT --> RMD["ReactMarkdown"]
```

---

## 4. Backend Request Pipeline

```mermaid
graph TD
    REQ["Incoming POST /api/consultation"] --> CORS[CORS Middleware]
    CORS --> ROUTE{Route Match?}

    ROUTE -->|"/api/consultation"| AUTH[ClerkHTTPBearer]
    ROUTE -->|"/health"| HEALTH[Return 200 OK]
    ROUTE -->|"/*"| STATIC[Serve Static Files]

    AUTH -->|Invalid or Missing JWT| E401[401 Unauthorized]
    AUTH -->|Valid JWT| PYDANTIC[Pydantic Validation]

    PYDANTIC -->|Invalid body| E422[422 Unprocessable Entity]
    PYDANTIC -->|Valid Visit| PROMPT[Build system + user prompt]

    PROMPT --> OPENAI[OpenAI streaming call]
    OPENAI --> SSE["event_stream generator"]
    SSE --> RESP["StreamingResponse — text/event-stream"]
```

---

## 5. Docker Build Pipeline

```mermaid
graph LR
    subgraph S1["Stage 1: node 22 alpine"]
        A1[npm ci] --> A2[npm run build]
        A2 --> A3["/app/out — static files"]
    end

    subgraph S2["Stage 2: python 3.12 slim"]
        B1[pip install] --> B2[COPY server.py]
        B2 --> B3["COPY /app/out to /app/static"]
        B3 --> B4["uvicorn on port 8000"]
    end

    A3 -->|COPY --from| B3
```

---

## 6. Deployment Comparison

```mermaid
graph TB
    subgraph Vercel["Vercel Deployment"]
        V1[vercel --prod]
        V1 --> V2[Next.js Build]
        V1 --> V3[Python Function]
        V2 --> V4[CDN Edge]
        V3 --> V5[Serverless Runtime]
    end

    subgraph AWS["AWS Deployment"]
        A1[docker build] --> A2[docker push]
        A2 --> ECR[Amazon ECR]
        ECR --> AR[App Runner]
        AR --> CONT[Single Container]
        CONT --> API_S[FastAPI on port 8000]
        CONT --> STAT_S[Static Files]
    end
```

---

## 7. Data Flow - Simplified

```mermaid
flowchart LR
    A["Doctor Notes"] -->|JSON POST| B["JWT Verify"]
    B -->|Valid| C["Pydantic"]
    C --> D["OpenAI"]
    D -->|Stream| E["SSE"]
    E -->|Token by token| F["Markdown"]
    F --> G["Doctor Reviews"]

    B -->|Invalid| X1["401"]
    C -->|Invalid| X2["422"]
```

---

## 8. Subscription Flow

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

---

## How to Use These Diagrams

### In GitHub README
GitHub natively renders Mermaid in `.md` files. Simply include the code blocks with the `mermaid` language tag.

### In Presentations
1. Visit [mermaid.live](https://mermaid.live)
2. Paste the diagram code
3. Export as SVG or PNG
4. Insert into slides

### In VS Code
Install the "Mermaid Markdown Syntax Highlighting" extension for preview support.
