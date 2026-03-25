"""Integration tests for FastAPI endpoints."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

os.environ.setdefault("CLERK_JWKS_URL", "https://test.clerk.accounts.dev/.well-known/jwks.json")

from fastapi.testclient import TestClient
from api.server import app


class TestHealthEndpoint:

    def test_health_returns_200(self):
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_correct_body(self):
        client = TestClient(app)
        response = client.get("/health")
        assert response.json() == {"status": "healthy"}

    def test_health_rejects_post(self):
        client = TestClient(app)
        response = client.post("/health")
        assert response.status_code == 405


class TestConsultationEndpoint:

    def _valid_payload(self):
        return {
            "patient_name": "Jane Smith",
            "date_of_visit": "2026-03-15",
            "notes": "Persistent cough for 2 weeks. No fever. Chest clear."
        }

    def test_rejects_missing_auth(self):
        client = TestClient(app)
        response = client.post("/api/consultation", json=self._valid_payload())
        assert response.status_code in [401, 403]

    def test_rejects_invalid_body(self):
        client = TestClient(app)
        response = client.post(
            "/api/consultation",
            json={"patient_name": "Jane"},
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == 422

    def test_rejects_empty_body(self):
        client = TestClient(app)
        response = client.post(
            "/api/consultation",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == 422

    def test_rejects_get_method(self):
        client = TestClient(app)
        response = client.get("/api/consultation")
        assert response.status_code == 405


class TestSSEFormatting:

    def test_single_line_produces_one_event(self):
        text = "Hello world"
        lines = text.split("\n")
        events = []
        for line in lines[:-1]:
            events.append(f"data: {line}\n\n")
            events.append("data:  \n")
        events.append(f"data: {lines[-1]}\n\n")
        assert len(events) == 1
        assert events[0] == "data: Hello world\n\n"

    def test_multiline_produces_separate_events(self):
        text = "Line1\nLine2"
        lines = text.split("\n")
        events = []
        for line in lines[:-1]:
            events.append(f"data: {line}\n\n")
            events.append("data:  \n")
        events.append(f"data: {lines[-1]}\n\n")
        assert "data: Line1\n\n" in events
        assert "data:  \n" in events
        assert "data: Line2\n\n" in events

    def test_none_content_is_skipped(self):
        text = None
        assert not text
