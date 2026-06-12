"""
Unit tests for Clinical Risk Assessment Engine
"""

import unittest
import json
from clinical_risk_assessment import (
    ClinicalRiskAssessmentEngine,
    ClinicalRiskAssessment,
    assess_clinical_risk,
    assess_clinical_risk_json,
)


class TestClinicalRiskAssessmentEngine(unittest.TestCase):
    """Test cases for ClinicalRiskAssessmentEngine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = ClinicalRiskAssessmentEngine()

    def test_assess_chest_pain_critical(self):
        """Test assessment of acute chest pain (critical scenario)."""
        entities = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "Acute chest pain for 30 minutes",
            "symptoms_found": ["chest pain", "shortness of breath"],
            "timeline_onset": "30 minutes ago",
            "aggravating_or_alleviating_factors": []
        }
        vitals = {
            "blood_pressure": "145/90",
            "heart_rate": 105,
            "spo2": 94,
            "temperature": 98.6
        }
        
        assessment = self.engine.assess(entities, vitals)
        
        # Should have red flags
        assert len(assessment.red_flags_present) > 0
        assert any("chest" in f.lower() for f in assessment.red_flags_present)
        
        # Should identify missing data
        assert len(assessment.critical_missing_data_points) > 0
        
        # Should have worst-case scenarios
        assert len(assessment.worst_case_scenarios_to_exclude) > 0

    def test_red_flags_detection_acute_stroke(self):
        """Test detection of acute stroke indicators."""
        entities = {
            "age": 72,
            "sex": "female",
            "chief_complaint": "Sudden weakness on left side",
            "symptoms_found": ["weakness", "numbness"],
            "timeline_onset": "15 minutes ago",
            "aggravating_or_alleviating_factors": []
        }
        
        assessment = self.engine.assess(entities)
        
        assert len(assessment.red_flags_present) > 0
        assert any("stroke" in f.lower() or "weakness" in f.lower() 
                  for f in assessment.red_flags_present)

    def test_red_flags_detection_respiratory_distress(self):
        """Test detection of severe respiratory distress."""
        entities = {
            "age": 42,
            "sex": "male",
            "chief_complaint": "Severe shortness of breath",
            "symptoms_found": ["shortness of breath", "wheezing"],
            "timeline_onset": "10 minutes ago",
            "aggravating_or_alleviating_factors": []
        }
        vitals = {
            "spo2": 88,
            "heart_rate": 120
        }
        
        assessment = self.engine.assess(entities, vitals)
        
        assert len(assessment.red_flags_present) > 0
        assert any("respiratory" in f.lower() or "breath" in f.lower() 
                  for f in assessment.red_flags_present)

    def test_red_flags_detection_severe_headache(self):
        """Test detection of severe headache (SAH/meningitis risk)."""
        entities = {
            "age": 38,
            "sex": "female",
            "chief_complaint": "Worst headache of my life",
            "symptoms_found": ["headache"],
            "timeline_onset": "sudden onset",
            "aggravating_or_alleviating_factors": []
        }
        
        assessment = self.engine.assess(entities)
        
        assert len(assessment.red_flags_present) > 0
        assert any("headache" in f.lower() for f in assessment.red_flags_present)

    def test_red_flags_detection_altered_mental_status(self):
        """Test detection of altered mental status."""
        entities = {
            "age": 68,
            "sex": "male",
            "chief_complaint": "Patient is confused and disoriented",
            "symptoms_found": ["confusion"],
            "timeline_onset": "this morning",
            "aggravating_or_alleviating_factors": []
        }
        
        assessment = self.engine.assess(entities)
        
        assert len(assessment.red_flags_present) > 0

    def test_red_flags_detection_high_fever(self):
        """Test detection of high fever with sepsis risk."""
        entities = {
            "age": 45,
            "sex": "female",
            "chief_complaint": "High fever and chills",
            "symptoms_found": ["fever", "chills"],
            "timeline_onset": "2 days",
            "aggravating_or_alleviating_factors": []
        }
        vitals = {
            "temperature": 104.5
        }
        
        assessment = self.engine.assess(entities, vitals)
        
        assert len(assessment.red_flags_present) > 0

    def test_red_flags_detection_severe_abdominal_pain(self):
        """Test detection of severe abdominal pain."""
        entities = {
            "age": 62,
            "sex": "male",
            "chief_complaint": "Acute severe abdominal pain",
            "symptoms_found": ["abdominal pain"],
            "timeline_onset": "1 hour ago",
            "aggravating_or_alleviating_factors": []
        }
        vitals = {
            "blood_pressure": "110/68"
        }
        
        assessment = self.engine.assess(entities, vitals)
        
        assert len(assessment.red_flags_present) > 0

    def test_gaps_identification_chest_pain(self):
        """Test identification of gaps for chest pain assessment."""
        entities = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "Chest pain",
            "symptoms_found": ["chest pain"],
            "timeline_onset": "30 minutes",
            "aggravating_or_alleviating_factors": []
        }
        
        assessment = self.engine.assess(entities)
        
        # Should identify missing vital signs
        gaps = assessment.critical_missing_data_points
        assert len(gaps) > 0
        gap_text = ' '.join(gaps).lower()
        assert any(term in gap_text for term in [
            'blood pressure', 'heart rate', 'spo2'
        ])

    def test_gaps_identification_respiratory_distress(self):
        """Test identification of gaps for respiratory distress."""
        entities = {
            "age": 42,
            "sex": "male",
            "chief_complaint": "Shortness of breath",
            "symptoms_found": ["shortness of breath"],
            "timeline_onset": "today",
            "aggravating_or_alleviating_factors": []
        }
        
        assessment = self.engine.assess(entities)
        
        gaps = assessment.critical_missing_data_points
        assert len(gaps) > 0
        gap_text = ' '.join(gaps).lower()
        assert 'spo2' in gap_text or 'oxygen' in gap_text

    def test_gaps_identification_neuro_deficit(self):
        """Test identification of gaps for neurological deficit."""
        entities = {
            "age": 68,
            "sex": "female",
            "chief_complaint": "Sudden weakness",
            "symptoms_found": ["weakness"],
            "timeline_onset": "15 minutes ago",
            "aggravating_or_alleviating_factors": []
        }
        
        assessment = self.engine.assess(entities)
        
        gaps = assessment.critical_missing_data_points
        assert len(gaps) > 0
        gap_text = ' '.join(gaps).lower()
        assert any(term in gap_text for term in ['time', 'mental', 'speech'])

    def test_worst_case_scenarios_chest_pain(self):
        """Test worst-case scenario generation for chest pain."""
        entities = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "Acute chest pain",
            "symptoms_found": ["chest pain"],
            "timeline_onset": "30 minutes",
            "aggravating_or_alleviating_factors": []
        }
        
        assessment = self.engine.assess(entities)
        
        scenarios = assessment.worst_case_scenarios_to_exclude
        assert len(scenarios) > 0
        scenario_text = ' '.join(scenarios).lower()
        assert any(term in scenario_text for term in [
            'ami', 'myocardial', 'aortic', 'embolism'
        ])

    def test_worst_case_scenarios_stroke(self):
        """Test worst-case scenario generation for stroke."""
        entities = {
            "age": 72,
            "sex": "male",
            "chief_complaint": "Sudden weakness one side",
            "symptoms_found": ["weakness"],
            "timeline_onset": "10 minutes",
            "aggravating_or_alleviating_factors": []
        }
        
        assessment = self.engine.assess(entities)
        
        scenarios = assessment.worst_case_scenarios_to_exclude
        assert len(scenarios) > 0
        scenario_text = ' '.join(scenarios).lower()
        assert 'stroke' in scenario_text

    def test_assessment_to_dict(self):
        """Test conversion to dictionary."""
        assessment = ClinicalRiskAssessment(
            red_flags_present=["Red flag 1"],
            critical_missing_data_points=["Missing data 1"],
            worst_case_scenarios_to_exclude=["Scenario 1"]
        )
        
        d = assessment.to_dict()
        assert d["red_flags_present"] == ["Red flag 1"]
        assert d["critical_missing_data_points"] == ["Missing data 1"]
        assert d["worst_case_scenarios_to_exclude"] == ["Scenario 1"]

    def test_assessment_to_json(self):
        """Test conversion to JSON."""
        assessment = ClinicalRiskAssessment(
            red_flags_present=["Red flag 1"]
        )
        
        json_str = assessment.to_json()
        parsed = json.loads(json_str)
        assert "red_flags_present" in parsed
        assert parsed["red_flags_present"] == ["Red flag 1"]

    def test_convenience_function_dict(self):
        """Test convenience function returning dict."""
        entities = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "Chest pain",
            "symptoms_found": ["chest pain"],
            "timeline_onset": "30 minutes",
            "aggravating_or_alleviating_factors": []
        }
        
        result = assess_clinical_risk(entities)
        assert isinstance(result, dict)
        assert "red_flags_present" in result
        assert "critical_missing_data_points" in result
        assert "worst_case_scenarios_to_exclude" in result

    def test_convenience_function_json(self):
        """Test convenience function returning JSON."""
        entities = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "Chest pain",
            "symptoms_found": ["chest pain"],
            "timeline_onset": "30 minutes",
            "aggravating_or_alleviating_factors": []
        }
        
        result = assess_clinical_risk_json(entities)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "red_flags_present" in parsed

    def test_empty_entities(self):
        """Test assessment with empty entities."""
        entities = {
            "age": None,
            "sex": None,
            "chief_complaint": "",
            "symptoms_found": [],
            "timeline_onset": "",
            "aggravating_or_alleviating_factors": []
        }
        
        assessment = self.engine.assess(entities)
        
        # Should not crash
        assert isinstance(assessment.red_flags_present, list)
        assert isinstance(assessment.critical_missing_data_points, list)

    def test_multiple_red_flags(self):
        """Test detection of multiple red flags."""
        entities = {
            "age": 58,
            "sex": "male",
            "chief_complaint": "Chest pain, shortness of breath, and severe headache",
            "symptoms_found": ["chest pain", "shortness of breath", "headache"],
            "timeline_onset": "1 hour",
            "aggravating_or_alleviating_factors": []
        }
        vitals = {
            "temperature": 103.5,
            "spo2": 90
        }
        
        assessment = self.engine.assess(entities, vitals)
        
        # Should detect multiple red flags
        assert len(assessment.red_flags_present) >= 2

    def test_no_red_flags_mild_symptoms(self):
        """Test assessment with mild, non-urgent symptoms."""
        entities = {
            "age": 35,
            "sex": "female",
            "chief_complaint": "Mild runny nose",
            "symptoms_found": ["runny nose", "sneezing"],
            "timeline_onset": "2 days",
            "aggravating_or_alleviating_factors": ["better with rest"]
        }
        
        assessment = self.engine.assess(entities)
        
        # Should have few or no red flags
        red_flag_text = ' '.join(assessment.red_flags_present).lower()
        # Basic cold symptoms should not trigger emergency flags
        assert "emergency" not in red_flag_text or len(assessment.red_flags_present) == 0


class TestRobustness(unittest.TestCase):
    """Test robustness and edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = ClinicalRiskAssessmentEngine()

    def test_case_insensitivity(self):
        """Test that assessment is case insensitive."""
        entities_lower = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "chest pain",
            "symptoms_found": ["chest pain"],
            "timeline_onset": "30 minutes",
            "aggravating_or_alleviating_factors": []
        }
        
        entities_upper = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "CHEST PAIN",
            "symptoms_found": ["CHEST PAIN"],
            "timeline_onset": "30 minutes",
            "aggravating_or_alleviating_factors": []
        }
        
        assessment_lower = self.engine.assess(entities_lower)
        assessment_upper = self.engine.assess(entities_upper)
        
        # Should detect same red flags regardless of case
        assert len(assessment_lower.red_flags_present) > 0
        assert len(assessment_upper.red_flags_present) > 0

    def test_vitals_integration(self):
        """Test integration of vital signs into risk assessment."""
        entities = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "Chest pain",
            "symptoms_found": ["chest pain"],
            "timeline_onset": "30 minutes",
            "aggravating_or_alleviating_factors": []
        }
        
        # Without vitals
        assessment_no_vitals = self.engine.assess(entities)
        
        # With critical vitals
        critical_vitals = {
            "blood_pressure": "180/100",
            "heart_rate": 125,
            "spo2": 88,
            "temperature": 99
        }
        assessment_with_vitals = self.engine.assess(entities, critical_vitals)
        
        # Both should detect chest pain
        assert len(assessment_no_vitals.red_flags_present) > 0
        assert len(assessment_with_vitals.red_flags_present) > 0

    def test_gap_identification_with_partial_vitals(self):
        """Test gap identification when only some vitals are provided."""
        entities = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "Chest pain",
            "symptoms_found": ["chest pain"],
            "timeline_onset": "30 minutes",
            "aggravating_or_alleviating_factors": []
        }
        
        partial_vitals = {
            "blood_pressure": "145/90"
            # Missing HR, SpO2, temp
        }
        
        assessment = self.engine.assess(entities, partial_vitals)
        
        # Should still identify missing data
        gaps = assessment.critical_missing_data_points
        assert len(gaps) > 0


class TestClinicalScenarios(unittest.TestCase):
    """Test realistic clinical scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = ClinicalRiskAssessmentEngine()

    def test_scenario_ami(self):
        """Test acute myocardial infarction scenario."""
        entities = {
            "age": 62,
            "sex": "male",
            "chief_complaint": "Crushing chest pain with shortness of breath",
            "symptoms_found": ["chest pain", "shortness of breath", "diaphoresis"],
            "timeline_onset": "20 minutes ago",
            "aggravating_or_alleviating_factors": ["worse with exertion"]
        }
        vitals = {
            "blood_pressure": "150/95",
            "heart_rate": 110,
            "spo2": 92
        }
        
        assessment = self.engine.assess(entities, vitals)
        
        assert len(assessment.red_flags_present) > 0
        scenarios = ' '.join(assessment.worst_case_scenarios_to_exclude).lower()
        assert 'infarction' in scenarios or 'ami' in scenarios

    def test_scenario_stroke(self):
        """Test acute stroke scenario."""
        entities = {
            "age": 75,
            "sex": "female",
            "chief_complaint": "Sudden onset left-sided weakness and speech difficulty",
            "symptoms_found": ["weakness", "speech difficulty"],
            "timeline_onset": "25 minutes ago",
            "aggravating_or_alleviating_factors": []
        }
        
        assessment = self.engine.assess(entities)
        
        red_flags = ' '.join(assessment.red_flags_present).lower()
        scenarios = ' '.join(assessment.worst_case_scenarios_to_exclude).lower()
        
        assert 'stroke' in red_flags or 'weakness' in red_flags
        assert 'stroke' in scenarios

    def test_scenario_sepsis(self):
        """Test sepsis scenario."""
        entities = {
            "age": 72,
            "sex": "male",
            "chief_complaint": "High fever, confusion, and rapid breathing",
            "symptoms_found": ["fever", "confusion", "shortness of breath"],
            "timeline_onset": "6 hours",
            "aggravating_or_alleviating_factors": []
        }
        vitals = {
            "temperature": 105.2,
            "heart_rate": 125,
            "spo2": 89,
            "blood_pressure": "98/60"
        }
        
        assessment = self.engine.assess(entities, vitals)
        
        assert len(assessment.red_flags_present) > 0
        scenarios = ' '.join(assessment.worst_case_scenarios_to_exclude).lower()
        assert 'sepsis' in scenarios


if __name__ == "__main__":
    unittest.main()
