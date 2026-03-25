"""Tests for Pydantic data models."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from pydantic import ValidationError
from api.server import Visit


class TestVisitModel:

    def test_valid_visit(self):
        visit = Visit(patient_name="Jane Smith", date_of_visit="2026-03-15", notes="Cough for 2 weeks.")
        assert visit.patient_name == "Jane Smith"
        assert visit.date_of_visit == "2026-03-15"
        assert visit.notes == "Cough for 2 weeks."

    def test_missing_patient_name(self):
        with pytest.raises(ValidationError):
            Visit(date_of_visit="2026-03-15", notes="Some notes")

    def test_missing_date_of_visit(self):
        with pytest.raises(ValidationError):
            Visit(patient_name="Jane Smith", notes="Some notes")

    def test_missing_notes(self):
        with pytest.raises(ValidationError):
            Visit(patient_name="Jane Smith", date_of_visit="2026-03-15")

    def test_all_fields_missing(self):
        with pytest.raises(ValidationError):
            Visit()

    def test_accepts_any_string_for_date(self):
        """Current implementation accepts any string for date - no format validation."""
        visit = Visit(patient_name="Jane", date_of_visit="not-a-real-date", notes="Notes")
        assert visit.date_of_visit == "not-a-real-date"

    def test_accepts_long_notes(self):
        long_notes = "A" * 50000
        visit = Visit(patient_name="Jane", date_of_visit="2026-03-15", notes=long_notes)
        assert len(visit.notes) == 50000
