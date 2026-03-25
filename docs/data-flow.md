# Data Flow

## Overview

MediNotes Pro has a straightforward request-response data flow with one important characteristic: the response is streamed. Data enters the system as a JSON POST body, passes through authentication and validation, is transformed into an LLM prompt, and returns as a stream of Server-Sent Events that the frontend renders incrementally.

There is no persistent data store. All data exists only for the duration of a single request-response cycle.

---

## Request Data Flow

### Step 1: Client-Side Form Collection

**Component**: `pages/product.tsx` — `ConsultationForm`

The user fills in three fields managed by React `useState`:

```typescript
const [patientName, setPatientName] = useState('');
const [visitDate, setVisitDate] = useState<Date | null>(new Date());
const [notes, setNotes] = useState('');
```

On form submission, these are assembled into a JSON payload:

```json
{
  "patient_name": "Jane Smith",
  "date_of_visit": "2025-03-15",
  "notes": "Persistent cough 2 weeks, no fever, chest clear, BP 120/80..."
}
```

The date is converted from a JavaScript `Date` object to ISO string using `.toISOString().slice(0, 10)`.

### Step 2: JWT Retrieval

**Component**: `pages/product.tsx` — `useAuth()` hook from Clerk

Before sending the request, the frontend retrieves a fresh JWT from Clerk:

```typescript
const jwt = await getToken();
```

This JWT contains the user's identity (`sub` claim), expiration time, and is signed with Clerk's private key.

### Step 3: HTTP Request Transmission

**Library**: `@microsoft/fetch-event-source`

The request is sent as a POST with SSE connection:

```typescript
await fetchEventSource('/api', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${jwt}`,
    },
    body: JSON.stringify({ patient_name, date_of_visit, notes }),
    onmessage(ev) { /* handle streaming */ },
});
```

This establishes a persistent connection that stays open until the stream completes.

### Step 4: Backend JWT Verification

**Component**: `api/index.py` or `api/server.py` — `ClerkHTTPBearer` dependency

FastAPI's dependency injection system runs the auth guard before the endpoint handler:

```python
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)

@app.post("/api")
def consultation_summary(
    visit: Visit,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard),
):
```

The guard fetches Clerk's JWKS public keys (cached after first fetch), verifies the JWT signature, checks expiration, and extracts the decoded payload. If verification fails, FastAPI returns 401/403 before reaching the endpoint handler.

### Step 5: Request Body Validation

**Library**: Pydantic

The JSON body is automatically parsed and validated against the `Visit` model:

```python
class Visit(BaseModel):
    patient_name: str
    date_of_visit: str
    notes: str
```

If any field is missing or has the wrong type, FastAPI returns a 422 response with validation error details. This happens before any LLM call is made.

### Step 6: Prompt Construction

**Component**: `api/index.py` — `system_prompt` + `user_prompt_for()`

Two prompt messages are constructed:

**System Prompt** (static, defines output format):
```
You are provided with notes written by a doctor from a patient's visit.
Your job is to summarize the visit for the doctor and provide an email.
Reply with exactly three sections with the headings:
### Summary of visit for the doctor's records
### Next steps for the doctor
### Draft of email to patient in patient-friendly language
```

**User Prompt** (dynamic, includes patient data):
```
Create the summary, next steps and draft email for:
Patient Name: Jane Smith
Date of Visit: 2025-03-15
Notes:
Persistent cough 2 weeks, no fever, chest clear, BP 120/80...
```

These are sent to OpenAI as a `messages` array with `role: "system"` and `role: "user"`.

### Step 7: OpenAI Streaming Call

**Library**: `openai` Python SDK

```python
stream = client.chat.completions.create(
    model="gpt-5-nano",
    messages=prompt,
    stream=True,
)
```

With `stream=True`, OpenAI returns an iterator of `ChatCompletionChunk` objects. Each chunk contains `choices[0].delta.content` — a small text fragment (typically 1-5 tokens).

### Step 8: SSE Event Formatting

**Component**: `event_stream()` generator function

Each text fragment is formatted as an SSE event:

```python
def event_stream():
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            lines = text.split("\n")
            for line in lines[:-1]:
                yield f"data: {line}\n\n"
                yield "data:  \n"
            yield f"data: {lines[-1]}\n\n"
```

The newline handling is significant: SSE uses `\n\n` as the event delimiter, so literal newlines in the content must be split across separate `data:` lines. A space character (`"data:  \n"`) is yielded to preserve blank lines in the markdown output.

### Step 9: Streaming Response Delivery

**Library**: FastAPI `StreamingResponse`

```python
return StreamingResponse(event_stream(), media_type="text/event-stream")
```

FastAPI sends the HTTP response with `Content-Type: text/event-stream` and keeps the connection open. Each `yield` in the generator pushes data to the client immediately.

### Step 10: Client-Side Buffering and Rendering

**Component**: `pages/product.tsx` — `onmessage` callback

```typescript
let buffer = '';
onmessage(ev) {
    buffer += ev.data;
    setOutput(buffer);
}
```

Each SSE event appends to a running buffer. The entire buffer is set as React state, triggering a re-render. `ReactMarkdown` processes the complete buffer on every update, rendering whatever valid markdown exists so far.

This means the user sees partial markdown rendering update in real time — headings appear as soon as the `###` tokens arrive, bullet points render as they stream in, and text fills in token by token.

---

## Data Transformation Summary

```
User Input (form fields)
    ↓
JSON Object {patient_name, date_of_visit, notes}
    ↓
HTTP POST body (with JWT header)
    ↓
Pydantic Visit model (validated)
    ↓
Prompt messages [{system}, {user}]
    ↓
OpenAI API call (streaming)
    ↓
Token stream (delta.content fragments)
    ↓
SSE events (data: <token>\n\n)
    ↓
Client buffer (concatenated string)
    ↓
ReactMarkdown → HTML rendering
```

---

## Data That Is NOT Stored

The following data passes through the system but is not persisted anywhere:

- Patient name
- Date of visit
- Consultation notes
- Generated summaries
- User ID (extracted from JWT but not logged)
- Request timestamps
- Token counts / usage metrics

For a production healthcare system, several of these would need to be stored in an encrypted database with audit logging. This is documented as a future improvement.
