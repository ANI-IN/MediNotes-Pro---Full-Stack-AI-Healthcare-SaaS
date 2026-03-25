"""Tests for prompt construction logic."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from api.server import user_prompt_for, Visit, system_prompt


class TestUserPromptConstruction:

    def test_contains_patient_name(self):
        visit = Visit(patient_name="Jane Smith", date_of_visit="2026-03-15", notes="Cough for 2 weeks")
        prompt = user_prompt_for(visit)
        assert "Jane Smith" in prompt

    def test_contains_date_of_visit(self):
        visit = Visit(patient_name="Jane", date_of_visit="2026-03-15", notes="Routine checkup")
        prompt = user_prompt_for(visit)
        assert "2026-03-15" in prompt

    def test_contains_consultation_notes(self):
        visit = Visit(patient_name="Jane", date_of_visit="2026-03-15", notes="Persistent cough. No fever.")
        prompt = user_prompt_for(visit)
        assert "Persistent cough" in prompt
        assert "No fever" in prompt

    def test_handles_special_characters(self):
        visit = Visit(patient_name="O'Brien", date_of_visit="2026-03-15", notes="BP 120/80.")
        prompt = user_prompt_for(visit)
        assert "O'Brien" in prompt
        assert "120/80" in prompt

    def test_handles_multiline_notes(self):
        visit = Visit(patient_name="Jane", date_of_visit="2026-03-15", notes="Line 1\nLine 2\nLine 3")
        prompt = user_prompt_for(visit)
        assert "Line 1\nLine 2\nLine 3" in prompt

    def test_handles_empty_notes(self):
        visit = Visit(patient_name="Jane", date_of_visit="2026-03-15", notes="")
        prompt = user_prompt_for(visit)
        assert "Jane" in prompt
        assert "2026-03-15" in prompt


class TestSystemPrompt:

    def test_requests_three_sections(self):
        assert "Summary of visit" in system_prompt
        assert "Next steps" in system_prompt
        assert "Draft of email" in system_prompt

    def test_specifies_exact_headings(self):
        assert "### Summary of visit for the doctor's records" in system_prompt
        assert "### Next steps for the doctor" in system_prompt
        assert "### Draft of email to patient in patient-friendly language" in system_prompt
