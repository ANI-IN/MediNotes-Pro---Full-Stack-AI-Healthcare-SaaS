# Future Roadmap

## Phase 1: Reliability (Weeks 1-2)

### Error Handling

Add React error boundaries to prevent white-screen crashes:

```typescript
// components/ErrorBoundary.tsx
class ErrorBoundary extends React.Component {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }
  render() {
    if (this.state.hasError) {
      return <div>Something went wrong. Please refresh.</div>;
    }
    return this.props.children;
  }
}
```

Add retry logic for OpenAI API failures with exponential backoff on the backend. Add timeout handling for streaming connections that exceed 60 seconds.

### Test Suite

Implement the testing strategy from `docs/testing-guide.md`. Priority: Pydantic validation tests, auth rejection tests, health check tests, and landing page smoke tests.

### Rate Limiting

Add per-user rate limiting using the `user_id` from the JWT `sub` claim. Start with 20 requests per hour per user.

---

## Phase 2: Data Persistence (Weeks 3-4)

### Database

Add PostgreSQL (Amazon RDS for AWS, Vercel Postgres for Vercel path):

```python
# models.py
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Consultation(Base):
    __tablename__ = "consultations"
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)  # From JWT sub claim
    patient_name = Column(String)
    date_of_visit = Column(String)
    notes = Column(Text)
    generated_output = Column(Text)
    created_at = Column(DateTime)
```

### Consultation History Page

Add `pages/history.tsx` — a protected page showing the authenticated user's past consultations, sorted by date, with the ability to view and re-generate outputs.

### Audit Logging

Log every API request with user ID, timestamp, input hash (not raw data), and response status. Store in a separate audit table for compliance.

---

## Phase 3: Product Features (Weeks 5-8)

### Specialty-Specific Templates

Extend the `Visit` model with a `specialty` field:

```python
class Visit(BaseModel):
    patient_name: str
    date_of_visit: str
    notes: str
    specialty: str = "general"  # New field
```

Map specialties to customized system prompts (pediatrics, cardiology, psychiatry, etc.).

### PDF Export

Add a "Download as PDF" button that exports the generated markdown as a formatted PDF. Use `jsPDF` or `html2pdf.js` on the frontend, or generate PDFs server-side with `reportlab`.

### Copy-to-Clipboard

Add buttons for each output section (summary, next steps, email) to copy content to clipboard independently.

### Multi-Language Patient Emails

Add a language selector to the form. Modify the system prompt to instruct the LLM to write the patient email in the selected language while keeping the medical summary in English.

---

## Phase 4: CI/CD and Operations (Weeks 9-10)

### GitHub Actions Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/backend/
          npm ci && npm test
      - name: Build and push Docker image
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URL
          docker build --platform linux/amd64 -t app .
          docker tag app:latest $ECR_URL/medinotes-pro:latest
          docker push $ECR_URL/medinotes-pro:latest
      - name: Deploy to App Runner
        run: aws apprunner start-deployment --service-arn $SERVICE_ARN
```

### Monitoring

Add structured JSON logging for CloudWatch Logs Insights queries. Set up CloudWatch alarms for error rate and response latency. Consider Datadog or Prometheus/Grafana for more advanced monitoring.

---

## Phase 5: Advanced Features (Months 3+)

### Voice-to-Text Input

Add a microphone button to the consultation form that uses the Web Speech API or OpenAI Whisper to transcribe spoken notes into text.

### EHR Integration (FHIR)

Build a FHIR R4 adapter that can push generated summaries to compatible EHR systems. This requires understanding the FHIR DocumentReference and Composition resources.

### Multi-Tenant Architecture

Support multiple clinics/organizations with tenant-level isolation:
- Separate data per tenant
- Organization-level billing (Clerk Organizations)
- Admin dashboard per organization
- Role-based access (doctor vs admin vs billing)

### HIPAA Compliance

Full HIPAA implementation:
- BAA agreements with AWS and OpenAI
- Encryption at rest (RDS encryption, S3 server-side encryption)
- Audit trail for all data access
- Incident response procedures
- Regular security assessments
- Data retention and disposal policies
