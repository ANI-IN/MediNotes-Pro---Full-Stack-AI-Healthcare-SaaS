# Testing Guide

## Current State

The codebase does not include any automated tests. This document provides a comprehensive testing strategy that should be implemented to bring the project to production quality.

---

## Recommended Test Structure

```
tests/
├── backend/
│   ├── conftest.py              # Shared fixtures (mock OpenAI, mock auth)
│   ├── test_models.py           # Pydantic model validation tests
│   ├── test_prompts.py          # Prompt construction tests
│   ├── test_api.py              # API endpoint integration tests
│   └── test_streaming.py        # SSE formatting tests
├── frontend/
│   └── __tests__/
│       ├── index.test.tsx       # Landing page rendering
│       ├── product.test.tsx     # Consultation form behavior
│       └── streaming.test.tsx   # SSE buffering and rendering
└── e2e/
    └── consultation.spec.ts     # End-to-end Playwright tests
```

---

## Backend Tests (pytest)

### Model Validation Tests

```python
# tests/backend/test_models.py
import pytest
from pydantic import ValidationError

# Import from your API module
from api.index import Visit

def test_valid_visit():
    visit = Visit(
        patient_name="Jane Smith",
        date_of_visit="2025-03-15",
        notes="Persistent cough for 2 weeks"
    )
    assert visit.patient_name == "Jane Smith"
    assert visit.date_of_visit == "2025-03-15"

def test_missing_patient_name():
    with pytest.raises(ValidationError):
        Visit(date_of_visit="2025-03-15", notes="Some notes")

def test_missing_notes():
    with pytest.raises(ValidationError):
        Visit(patient_name="Jane", date_of_visit="2025-03-15")

def test_empty_string_fields():
    # Pydantic allows empty strings by default
    visit = Visit(patient_name="", date_of_visit="", notes="")
    assert visit.patient_name == ""
```

### Prompt Construction Tests

```python
# tests/backend/test_prompts.py
from api.index import user_prompt_for, Visit, system_prompt

def test_user_prompt_contains_patient_data():
    visit = Visit(
        patient_name="Jane Smith",
        date_of_visit="2025-03-15",
        notes="Cough for 2 weeks"
    )
    prompt = user_prompt_for(visit)
    assert "Jane Smith" in prompt
    assert "2025-03-15" in prompt
    assert "Cough for 2 weeks" in prompt

def test_system_prompt_has_required_sections():
    assert "Summary of visit" in system_prompt
    assert "Next steps" in system_prompt
    assert "Draft of email" in system_prompt

def test_user_prompt_structure():
    visit = Visit(
        patient_name="Test Patient",
        date_of_visit="2025-01-01",
        notes="Test notes"
    )
    prompt = user_prompt_for(visit)
    assert "Patient Name:" in prompt
    assert "Date of Visit:" in prompt
    assert "Notes:" in prompt
```

### SSE Formatting Tests

```python
# tests/backend/test_streaming.py

def test_sse_event_format():
    """SSE events must follow the format: data: <content>\n\n"""
    # Simulate the event_stream generator logic
    text = "Hello world"
    lines = text.split("\n")
    events = []
    for line in lines[:-1]:
        events.append(f"data: {line}\n\n")
        events.append("data:  \n")
    events.append(f"data: {lines[-1]}\n\n")
    
    assert events == [f"data: Hello world\n\n"]

def test_sse_multiline_handling():
    """Newlines in content must be split across SSE events"""
    text = "Line 1\nLine 2"
    lines = text.split("\n")
    events = []
    for line in lines[:-1]:
        events.append(f"data: {line}\n\n")
        events.append("data:  \n")
    events.append(f"data: {lines[-1]}\n\n")
    
    assert "data: Line 1\n\n" in events
    assert "data: Line 2\n\n" in events
```

### API Integration Tests

```python
# tests/backend/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

def test_health_endpoint():
    """Health check should return 200 with status healthy"""
    from api.server import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_api_rejects_missing_auth():
    """POST /api without JWT should return 401/403"""
    from api.server import app
    client = TestClient(app)
    response = client.post("/api/consultation", json={
        "patient_name": "Test",
        "date_of_visit": "2025-01-01",
        "notes": "Test"
    })
    assert response.status_code in [401, 403]

def test_api_rejects_invalid_body():
    """POST with missing fields should return 422"""
    from api.server import app
    client = TestClient(app)
    # Mock the auth dependency to bypass JWT
    # (requires dependency override setup)
    response = client.post("/api/consultation", json={
        "patient_name": "Test"
        # Missing date_of_visit and notes
    })
    assert response.status_code == 422
```

---

## Frontend Tests (Jest + React Testing Library)

### Setup

```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

### Landing Page Tests

```typescript
// tests/frontend/__tests__/index.test.tsx
import { render, screen } from '@testing-library/react';

// Mock Clerk components
jest.mock('@clerk/nextjs', () => ({
  SignInButton: ({ children }: any) => children,
  SignedIn: ({ children }: any) => children,
  SignedOut: ({ children }: any) => children,
  UserButton: () => <div data-testid="user-button" />,
}));

import Home from '../../../pages/index';

describe('Landing Page', () => {
  it('renders the product name', () => {
    render(<Home />);
    expect(screen.getByText('MediNotes Pro')).toBeInTheDocument();
  });

  it('renders the hero heading', () => {
    render(<Home />);
    expect(screen.getByText(/Transform Your/)).toBeInTheDocument();
  });

  it('renders feature cards', () => {
    render(<Home />);
    expect(screen.getByText('Professional Summaries')).toBeInTheDocument();
    expect(screen.getByText('Action Items')).toBeInTheDocument();
    expect(screen.getByText('Patient Emails')).toBeInTheDocument();
  });
});
```

---

## End-to-End Tests (Playwright)

### Setup

```bash
npm install --save-dev @playwright/test
npx playwright install
```

### Example E2E Test

```typescript
// tests/e2e/consultation.spec.ts
import { test, expect } from '@playwright/test';

test('landing page loads and shows sign-in', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('MediNotes Pro')).toBeVisible();
  await expect(page.getByText('Sign In')).toBeVisible();
});

test('product page requires authentication', async ({ page }) => {
  await page.goto('/product');
  // Should show either sign-in prompt or pricing table
  // (exact behavior depends on Clerk state)
});
```

---

## Load Testing (k6)

For testing streaming under concurrent load:

```javascript
// tests/load/streaming.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,           // 10 concurrent users
  duration: '30s',
};

export default function () {
  const payload = JSON.stringify({
    patient_name: 'Load Test Patient',
    date_of_visit: '2025-01-01',
    notes: 'Test notes for load testing',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${__ENV.TEST_JWT}`,
    },
  };

  const res = http.post('https://your-app.vercel.app/api', payload, params);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

---

## What To Test First (Priority Order)

1. **Pydantic model validation** — Quick wins, catches input edge cases
2. **Prompt construction** — Ensures patient data is correctly embedded
3. **Health endpoint** — Verifies server starts correctly
4. **Auth rejection** — Confirms unauthenticated requests are blocked
5. **SSE formatting** — Ensures streaming events parse correctly on the client
6. **Landing page rendering** — Basic smoke test for frontend
7. **E2E auth flow** — Full sign-in → form → output cycle
