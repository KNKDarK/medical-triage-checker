"""
Unit tests for Medical Entity Extractor
"""

import unittest
import json
from medical_entity_extractor import (
    MedicalEntityExtractor,
    MedicalEntity,
    extract_medical_entities,
    extract_medical_entities_json,
)


class TestMedicalEntityExtractor(unittest.TestCase):
    """Test cases for MedicalEntityExtractor."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = MedicalEntityExtractor()

    def test_extract_age_valid(self):
        """Test age extraction with valid ages."""
        assert self.extractor._extract_age("i'm a 42 year old") == 42
        assert self.extractor._extract_age("35 yo") == 35
        assert self.extractor._extract_age("age 72 years") == 72
        assert self.extractor._extract_age("my dad is 68") == 68

    def test_extract_age_invalid(self):
        """Test age extraction with invalid ages."""
        assert self.extractor._extract_age("i'm 200 years old") is None
        assert self.extractor._extract_age("no age mentioned") is None
        assert self.extractor._extract_age("-5 years") is None

    def test_extract_sex_female(self):
        """Test sex extraction for female."""
        assert self.extractor._extract_sex("i'm a woman") == "female"
        assert self.extractor._extract_sex("she is feeling ill") == "female"
        assert self.extractor._extract_sex("the girl has fever") == "female"

    def test_extract_sex_male(self):
        """Test sex extraction for male."""
        assert self.extractor._extract_sex("i'm a man") == "male"
        assert self.extractor._extract_sex("he has a cough") == "male"
        assert self.extractor._extract_sex("my son is sick") == "male"

    def test_extract_sex_none(self):
        """Test sex extraction when not specified."""
        assert self.extractor._extract_sex("symptoms started today") is None

    def test_extract_chief_complaint(self):
        """Test chief complaint extraction."""
        narrative = "I have a severe headache. It started yesterday."
        chief = self.extractor._extract_chief_complaint(narrative)
        assert "headache" in chief.lower()

    def test_extract_symptoms_respiratory(self):
        """Test respiratory symptom extraction."""
        text = "i have a cough, sore throat, and shortness of breath"
        symptoms = self.extractor._extract_symptoms(text.lower())
        assert "cough" in symptoms
        assert "sore throat" in symptoms
        assert "shortness of breath" in symptoms

    def test_extract_symptoms_digestive(self):
        """Test digestive symptom extraction."""
        text = "nausea, vomiting, and diarrhea all day"
        symptoms = self.extractor._extract_symptoms(text.lower())
        assert "nausea" in symptoms
        assert "vomiting" in symptoms
        assert "diarrhea" in symptoms

    def test_extract_symptoms_general(self):
        """Test general/systemic symptom extraction."""
        text = "high fever, chills, body aches, and fatigue"
        symptoms = self.extractor._extract_symptoms(text.lower())
        assert "fever" in symptoms
        assert "chills" in symptoms
        assert "body aches" in symptoms
        assert "fatigue" in symptoms

    def test_extract_symptoms_neurological(self):
        """Test neurological symptom extraction."""
        text = "severe headache with blurred vision and dizziness"
        symptoms = self.extractor._extract_symptoms(text.lower())
        assert "headache" in symptoms
        assert "blurred vision" in symptoms
        assert "dizziness" in symptoms

    def test_extract_symptoms_skin(self):
        """Test skin symptom extraction."""
        text = "red rash all over with itching and swelling"
        symptoms = self.extractor._extract_symptoms(text.lower())
        assert "rash" in symptoms
        assert "itching" in symptoms
        assert "swelling" in symptoms

    def test_extract_symptoms_empty(self):
        """Test symptom extraction with no symptoms."""
        text = "feeling fine today"
        symptoms = self.extractor._extract_symptoms(text.lower())
        assert len(symptoms) == 0

    def test_extract_timeline_days(self):
        """Test timeline extraction in days."""
        text = "started 3 days ago"
        timeline = self.extractor._extract_timeline(text.lower())
        assert "3" in timeline or "days" in timeline

    def test_extract_timeline_weeks(self):
        """Test timeline extraction in weeks."""
        text = "symptoms for 2 weeks now"
        timeline = self.extractor._extract_timeline(text.lower())
        assert len(timeline) > 0

    def test_extract_timeline_empty(self):
        """Test timeline extraction with no timeline."""
        text = "i have a cough"
        timeline = self.extractor._extract_timeline(text.lower())
        assert timeline == ""

    def test_extract_factors_alleviating(self):
        """Test alleviating factor extraction."""
        text = "pain improves with rest and ice pack"
        factors = self.extractor._extract_factors(text.lower())
        assert any("rest" in f.lower() or "ice" in f.lower() for f in factors)

    def test_extract_factors_aggravating(self):
        """Test aggravating factor extraction."""
        text = "symptoms worsen when i exercise"
        factors = self.extractor._extract_factors(text.lower())
        assert any("exercise" in f.lower() for f in factors)

    def test_extract_factors_medication(self):
        """Test medication as alleviating factor."""
        text = "pain relieved by ibuprofen"
        factors = self.extractor._extract_factors(text.lower())
        assert any("medication" in f.lower() or "ibuprofen" in f.lower() for f in factors)

    def test_full_extraction(self):
        """Test full extraction pipeline."""
        narrative = """
        I'm a 35-year-old female with a severe headache for the past 3 days.
        Started after a stressful work day. The pain is worse when I look at screens
        and better when I rest. Also experiencing nausea and sensitivity to light.
        Ibuprofen helps a bit.
        """
        entity = self.extractor.extract(narrative)
        
        assert entity.age == 35
        assert entity.sex == "female"
        assert "headache" in entity.symptoms_found
        assert len(entity.timeline_onset) > 0
        assert len(entity.aggravating_or_alleviating_factors) > 0

    def test_entity_to_dict(self):
        """Test MedicalEntity conversion to dict."""
        entity = MedicalEntity(
            age=42,
            sex="male",
            chief_complaint="chest pain",
            symptoms_found=["chest pain", "shortness of breath"],
            timeline_onset="2 days",
            aggravating_or_alleviating_factors=["worsens with exertion"]
        )
        d = entity.to_dict()
        assert d["age"] == 42
        assert d["sex"] == "male"
        assert "chest pain" in d["symptoms_found"]

    def test_entity_to_json(self):
        """Test MedicalEntity conversion to JSON."""
        entity = MedicalEntity(
            age=42,
            sex="male",
            chief_complaint="chest pain",
            symptoms_found=["chest pain"],
            timeline_onset="2 days"
        )
        json_str = entity.to_json()
        parsed = json.loads(json_str)
        assert parsed["age"] == 42
        assert parsed["sex"] == "male"

    def test_convenience_function_dict(self):
        """Test convenience function returning dict."""
        narrative = "42 year old man with fever"
        result = extract_medical_entities(narrative)
        assert isinstance(result, dict)
        assert result["age"] == 42
        assert result["sex"] == "male"

    def test_convenience_function_json(self):
        """Test convenience function returning JSON."""
        narrative = "42 year old man with fever"
        result = extract_medical_entities_json(narrative)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["age"] == 42

    def test_no_personal_interpretation(self):
        """Test that extractor doesn't interpret/diagnose."""
        # This should NOT extract "flu" or "covid" or any diagnosis
        narrative = "I have fever, cough, and body aches"
        entity = self.extractor.extract(narrative)
        
        # Should only have the explicit symptoms, not interpreted diagnoses
        assert "fever" in entity.symptoms_found
        assert "cough" in entity.symptoms_found
        assert "body aches" in entity.symptoms_found
        # Should not contain diagnoses
        assert "flu" not in entity.symptoms_found
        assert "covid" not in entity.symptoms_found
        assert "infection" not in entity.chief_complaint.lower()

    def test_guardrail_no_severity_assignment(self):
        """Test that extractor doesn't assign severity."""
        narrative = "I have some discomfort"
        entity = self.extractor.extract(narrative)
        
        # Should not contain severity words in extraction
        # (only in the raw text)
        json_str = entity.to_json()
        assert "severe" not in json_str.lower() or "severe" in narrative.lower()

    def test_empty_narrative(self):
        """Test extraction from empty narrative."""
        entity = self.extractor.extract("")
        assert entity.age is None
        assert entity.sex is None
        assert entity.chief_complaint == ""
        assert entity.symptoms_found == []
        assert entity.timeline_onset == ""
        assert entity.aggravating_or_alleviating_factors == []

    def test_complex_narrative(self):
        """Test extraction from complex, messy narrative."""
        narrative = """
        Hi. Im 47yr old. Have been having this awful pain in my chest, 
        like pressure, for about a week now. Sometimes it gets worse when 
        i'm walking up stairs. It feels better when i sit down and rest. 
        Also been sweating a lot at night. Took some aspirin yesterday and 
        it helped for a while. Wife says i should see a dr. Male btw.
        """
        entity = self.extractor.extract(narrative)
        
        assert entity.age == 47
        assert entity.sex == "male"
        assert any("chest" in s.lower() for s in entity.symptoms_found)
        assert len(entity.timeline_onset) > 0
        assert len(entity.aggravating_or_alleviating_factors) > 0


class TestRobustness(unittest.TestCase):
    """Test robustness and edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = MedicalEntityExtractor()

    def test_case_insensitivity(self):
        """Test that extraction is case insensitive."""
        narrative_lower = "42 year old with COUGH and FEVER"
        narrative_upper = "42 YEAR OLD WITH cough AND fever"
        
        entity_lower = self.extractor.extract(narrative_lower)
        entity_upper = self.extractor.extract(narrative_upper)
        
        assert entity_lower.age == entity_upper.age
        assert set(entity_lower.symptoms_found) == set(entity_upper.symptoms_found)

    def test_duplicate_symptoms(self):
        """Test that duplicate symptoms are not duplicated in output."""
        narrative = "I have a cough and cough and I'm coughing"
        entity = self.extractor.extract(narrative)
        cough_count = sum(1 for s in entity.symptoms_found if "cough" in s.lower())
        assert cough_count == 1

    def test_special_characters(self):
        """Test extraction with special characters."""
        narrative = "42-year-old @ home w/ fever & cough..."
        entity = self.extractor.extract(narrative)
        assert entity.age == 42
        assert "fever" in entity.symptoms_found

    def test_long_narrative(self):
        """Test extraction from very long narrative."""
        narrative = " ".join(["I have a headache."] * 100)
        entity = self.extractor.extract(narrative)
        assert "headache" in entity.symptoms_found
        # Chief complaint should be truncated appropriately
        assert len(entity.chief_complaint) <= 200


if __name__ == "__main__":
    unittest.main()
