# Use Cases

## Primary Use Case: Post-Consultation Documentation

### Scenario

Dr. Anita Patel is a general practitioner at a busy urban clinic. She sees 28 patients today. After her 2:15 PM appointment with Jane Smith (persistent cough, 2 weeks), she has 5 minutes before her next patient arrives.

### Workflow Without MediNotes Pro

1. Dr. Patel opens her EHR system
2. She types a clinical note from memory (3-4 minutes)
3. She creates a follow-up task in the EHR (1 minute)
4. After clinic hours, she drafts a patient email (3-4 minutes per patient, across all 28 patients)
5. Total documentation time per patient: ~8-10 minutes
6. Total documentation backlog at end of day: ~2-3 hours

### Workflow With MediNotes Pro

1. Dr. Patel opens MediNotes Pro between appointments
2. She types her shorthand notes: "persistent cough 2wk, no fever, chest clear, BP 120/80, viral bronchitis, rx rest/fluids, f/u 1wk"
3. She clicks Generate
4. Three sections stream onto her screen within 10-15 seconds
5. She reviews, adjusts any details, and copies each section to the appropriate system
6. Total time: 2-3 minutes

### Technical Mapping

| User Action | Frontend Component | Backend Processing | External Service |
|------------|-------------------|-------------------|-----------------|
| Opens app | `pages/product.tsx` renders form | None | None |
| Enters patient name | `<input>` → `setPatientName` state | None | None |
| Selects date | `<DatePicker>` → `setVisitDate` state | None | None |
| Types notes | `<textarea>` → `setNotes` state | None | None |
| Clicks Generate | `fetchEventSource` POST with JWT | Pydantic validates `Visit` model | Clerk JWKS verification |
| Sees streaming output | `buffer += ev.data; setOutput(buffer)` | `StreamingResponse` yields SSE events | OpenAI streaming completion |
| Reviews markdown | `<ReactMarkdown>` renders buffer | None | None |

---

## Use Case 2: Shift Handoff Documentation

### Scenario

Dr. Patel's shift ends at 5 PM. Dr. Chen takes over. Three patients from Dr. Patel's afternoon require follow-up monitoring. Dr. Patel needs to provide Dr. Chen with clear, structured summaries.

### How It Works

Dr. Patel generates summaries for each patient using MediNotes Pro. The "Summary of visit" section provides Dr. Chen with clinical context, and the "Next steps" section explicitly lists what monitoring is needed. This is faster and more structured than a verbal handoff or handwritten notes.

### Why This Matters Engineering-Wise

This use case demonstrates that the structured prompt engineering (forcing three distinct sections with headers) has practical workflow value. The system prompt in `api/index.py` explicitly requests:

```
### Summary of visit for the doctor's records
### Next steps for the doctor
### Draft of email to patient in patient-friendly language
```

This structure is not cosmetic — it maps to distinct downstream uses.

---

## Use Case 3: New Subscriber Onboarding

### Scenario

A new physician, Dr. Torres, discovers MediNotes Pro online. She wants to try it before committing to a subscription.

### User Journey

1. Dr. Torres visits the landing page (`pages/index.tsx`)
2. She sees the product description, feature cards, and pricing preview
3. She clicks "Start Free Trial" which triggers the Clerk `<SignInButton>` modal
4. She signs in with Google (one of Clerk's configured providers)
5. She is redirected back to the landing page, now authenticated
6. She clicks "Access Premium Features" which navigates to `/product`
7. The `<Protect>` component detects she has no active subscription
8. The `<PricingTable>` renders with the Premium Subscription option ($10/month)
9. She subscribes via Clerk Billing
10. The page re-renders, now showing the consultation form inside `<IdeaGenerator>` (actually `<ConsultationForm>` in Day 4)
11. She enters test data and sees her first streaming result

### Technical Mapping

| Step | Component | Gate |
|------|-----------|------|
| Unauthenticated landing | `<SignedOut>` → Sign In button visible | None |
| Post-auth landing | `<SignedIn>` → "Go to App" visible | Clerk session |
| Product page (no sub) | `<Protect>` fallback → `<PricingTable>` | `plan="premium_subscription"` |
| Product page (subscribed) | `<Protect>` children → `<ConsultationForm>` | Active subscription |

---

## Use Case 4: Specialty-Specific Documentation

### Scenario (Extension Point)

A pediatrician wants the patient email to use child-friendly language and address parents. A psychiatrist wants the summary to include mental health screening scores.

### How The System Supports This

The current system prompt is hardcoded in `api/index.py`. However, the architecture supports parameterization:

```python
def get_system_prompt(specialty: str) -> str:
    prompts = {
        "pediatrics": "...use child-friendly language, address parents...",
        "psychiatry": "...include PHQ-9 scores, safety assessments...",
        "cardiology": "...emphasize cardiovascular risk factors...",
    }
    return prompts.get(specialty, default_system_prompt)
```

This is documented as a future improvement. The `Visit` Pydantic model could be extended with a `specialty` field, and the frontend form could include a specialty dropdown. No architectural changes are needed — only prompt and model changes.

---

## Use Case 5: Audit and Compliance Review

### Scenario (Extension Point)

A clinic administrator needs to verify that all consultations from the past month have been documented. They need to know which doctor generated which summary, when, and for which patient.

### Current State

The backend extracts `user_id` from the JWT but does not persist it. The code has a comment acknowledging this:

```python
user_id = creds.decoded["sub"]  # Available for tracking/auditing
# You could use user_id to:
# - Track usage per user
# - Store generated ideas in a database
# - Apply user-specific limits or customization
```

### Production Path

Adding a database (PostgreSQL via Amazon RDS) would enable storing each request with `user_id`, timestamp, input hash, and output. This transforms the system from stateless to auditable — a critical requirement for healthcare compliance.

---

## Use Case Summary Matrix

| Use Case | Implemented | Requires Extension | Key Concept Demonstrated |
|----------|------------|-------------------|------------------------|
| Post-consultation documentation | Yes | No | End-to-end streaming pipeline |
| Shift handoff | Yes | No | Structured prompt output |
| New subscriber onboarding | Yes | No | Auth + billing flow |
| Specialty-specific templates | Partially (architecture supports it) | Prompt parameterization | System design extensibility |
| Audit and compliance | Partially (user_id extracted) | Database + logging | Production hardening |
