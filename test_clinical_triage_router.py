"""
Unit tests for clinical_triage_router.py

Tests cover:
- All 4 care tiers (EMERGENCY, URGENT, NON-URGENT, HOME-CARE)
- Red flag detection logic
- Conservative routing (when in doubt, route up)
- Immediate actions generation
- Patient messaging
- Edge cases and boundary conditions
"""

import unittest
from clinical_triage_router import route_patient


class TestEmergencyTriage(unittest.TestCase):
    """Test cases for EMERGENCY care tier routing"""
    
    def test_chest_pain_emergency(self):
        """Chest pain with red flag should route to EMERGENCY"""
        entities = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "Acute chest pain",
            "symptoms_found": ["chest pain", "shortness of breath"],
            "timeline_onset": "30 minutes",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Chest pain/pressure (ACS/MI risk)"],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": ["Acute Myocardial Infarction (AMI)"]
        }
        result = route_patient(entities, risk)
        self.assertEqual(result['care_tier'], 'EMERGENCY')
        self.assertIn('911', result['patient_facing_message'])
    
    def test_stroke_symptoms_emergency(self):
        """Stroke symptoms should route to EMERGENCY"""
        entities = {
            "age": 72,
            "sex": "female",
            "chief_complaint": "Sudden weakness on left side",
            "symptoms_found": ["weakness", "speech difficulty", "facial drooping"],
            "timeline_onset": "15 minutes",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Acute focal neurological deficit (stroke risk)"],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": ["Ischemic Stroke", "Hemorrhagic Stroke"]
        }
        result = route_patient(entities, risk)
        self.assertEqual(result['care_tier'], 'EMERGENCY')
    
    def test_severe_respiratory_distress_emergency(self):
        """Severe respiratory distress should route to EMERGENCY"""
        entities = {
            "age": 68,
            "sex": "male",
            "chief_complaint": "Severe shortness of breath",
            "symptoms_found": ["shortness of breath", "wheezing", "stridor"],
            "timeline_onset": "acute",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Severe respiratory distress"],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": ["Anaphylaxis", "Tension Pneumothorax"]
        }
        result = route_patient(entities, risk)
        self.assertEqual(result['care_tier'], 'EMERGENCY')
    
    def test_altered_mental_status_emergency(self):
        """Altered mental status should route to EMERGENCY"""
        entities = {
            "age": 64,
            "sex": "male",
            "chief_complaint": "Confused and disoriented",
            "symptoms_found": ["confusion", "disorientation"],
            "timeline_onset": "acute",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Acute altered mental status"],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": ["Stroke", "Intracranial hemorrhage", "Sepsis"]
        }
        result = route_patient(entities, risk)
        self.assertEqual(result['care_tier'], 'EMERGENCY')
    
    def test_severe_allergic_reaction_emergency(self):
        """Severe allergic reaction should route to EMERGENCY"""
        entities = {
            "age": 35,
            "sex": "female",
            "chief_complaint": "Difficulty breathing after nut exposure",
            "symptoms_found": ["shortness of breath", "throat tightness", "swelling"],
            "timeline_onset": "5 minutes",
            "aggravating_or_alleviating_factors": ["started after eating peanuts"]
        }
        risk = {
            "red_flags_present": ["Anaphylaxis suspected"],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": ["Anaphylaxis"]
        }
        result = route_patient(entities, risk)
        self.assertEqual(result['care_tier'], 'EMERGENCY')
    
    def test_multiple_red_flags_emergency(self):
        """Multiple red flags should guarantee EMERGENCY routing"""
        entities = {
            "age": 78,
            "sex": "male",
            "chief_complaint": "Chest pain with shortness of breath",
            "symptoms_found": ["chest pain", "shortness of breath", "nausea"],
            "timeline_onset": "1 hour",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": [
                "Chest pain/pressure (ACS/MI risk)",
                "Severe respiratory distress",
                "Hypoxia"
            ],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": ["AMI", "Pulmonary Embolism"]
        }
        result = route_patient(entities, risk)
        self.assertEqual(result['care_tier'], 'EMERGENCY')


class TestUrgentTriage(unittest.TestCase):
    """Test cases for URGENT care tier routing"""
    
    def test_high_fever_urgent(self):
        """High fever (38.5°C+) should route to URGENT"""
        entities = {
            "age": 68,
            "sex": "male",
            "chief_complaint": "High fever and chills",
            "symptoms_found": ["fever", "chills", "body aches"],
            "timeline_onset": "overnight",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["High fever (38.5°C or higher)"],
            "critical_missing_data_points": ["Location of infection unclear"],
            "worst_case_scenarios_to_exclude": ["Meningitis", "Sepsis"]
        }
        vitals = {"temperature": 39.2}
        result = route_patient(entities, risk, vitals)
        self.assertEqual(result['care_tier'], 'URGENT')
    
    def test_moderate_dehydration_urgent(self):
        """Moderate dehydration should route to URGENT"""
        entities = {
            "age": 42,
            "sex": "female",
            "chief_complaint": "Severe vomiting for 2 days",
            "symptoms_found": ["vomiting", "dizziness", "weakness"],
            "timeline_onset": "2 days",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Moderate dehydration risk"],
            "critical_missing_data_points": ["Urine output", "Fluid intake"],
            "worst_case_scenarios_to_exclude": ["Severe dehydration", "Acute kidney injury"]
        }
        result = route_patient(entities, risk)
        self.assertEqual(result['care_tier'], 'URGENT')
    
    def test_diabetic_hyperglycemia_urgent(self):
        """Diabetic hyperglycemia symptoms should route to URGENT"""
        entities = {
            "age": 52,
            "sex": "male",
            "chief_complaint": "Extreme thirst and frequent urination",
            "symptoms_found": ["thirst", "frequent urination", "fatigue"],
            "timeline_onset": "3 days",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Possible hyperglycemia crisis"],
            "critical_missing_data_points": ["Blood glucose level", "Medication compliance"],
            "worst_case_scenarios_to_exclude": ["DKA", "HHS"]
        }
        result = route_patient(entities, risk)
        self.assertEqual(result['care_tier'], 'URGENT')
    
    def test_severe_abdominal_pain_urgent(self):
        """Severe acute abdominal pain should route to URGENT"""
        entities = {
            "age": 45,
            "sex": "female",
            "chief_complaint": "Severe abdominal pain",
            "symptoms_found": ["abdominal pain", "nausea", "vomiting"],
            "timeline_onset": "2 hours",
            "aggravating_or_alleviating_factors": ["pain is worsening"]
        }
        risk = {
            "red_flags_present": ["Severe acute abdominal pain"],
            "critical_missing_data_points": ["Imaging", "Surgical consult"],
            "worst_case_scenarios_to_exclude": ["Appendicitis", "Bowel obstruction", "AAA"]
        }
        result = route_patient(entities, risk)
        self.assertEqual(result['care_tier'], 'URGENT')
    
    def test_head_trauma_urgent(self):
        """Head trauma with symptoms should route to URGENT"""
        entities = {
            "age": 38,
            "sex": "male",
            "chief_complaint": "Hit head in fall",
            "symptoms_found": ["head injury", "dizziness", "confusion"],
            "timeline_onset": "30 minutes",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Head trauma with neuro symptoms"],
            "critical_missing_data_points": ["CT imaging", "Loss of consciousness timeline"],
            "worst_case_scenarios_to_exclude": ["Intracranial hemorrhage", "Epidural hematoma"]
        }
        result = route_patient(entities, risk)
        self.assertEqual(result['care_tier'], 'URGENT')


class TestNonUrgentTriage(unittest.TestCase):
    """Test cases for NON-URGENT care tier routing"""
    
    def test_mild_upper_respiratory_non_urgent(self):
        """Mild cold symptoms should route to NON-URGENT"""
        entities = {
            "age": 32,
            "sex": "female",
            "chief_complaint": "Runny nose and sneezing",
            "symptoms_found": ["runny nose", "sneezing", "mild cough"],
            "timeline_onset": "2 days",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": [],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": []
        }
        result = route_patient(entities, risk)
        self.assertIn(result['care_tier'], ['NON-URGENT', 'HOME-CARE'])
    
    def test_mild_headache_non_urgent(self):
        """Mild headache without red flags should route to NON-URGENT"""
        entities = {
            "age": 28,
            "sex": "male",
            "chief_complaint": "Mild headache",
            "symptoms_found": ["headache"],
            "timeline_onset": "this morning",
            "aggravating_or_alleviating_factors": ["responds to rest"]
        }
        risk = {
            "red_flags_present": [],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": []
        }
        result = route_patient(entities, risk)
        self.assertIn(result['care_tier'], ['NON-URGENT', 'HOME-CARE'])
    
    def test_minor_laceration_non_urgent(self):
        """Minor laceration should route to NON-URGENT"""
        entities = {
            "age": 45,
            "sex": "female",
            "chief_complaint": "Small cut on finger",
            "symptoms_found": ["laceration"],
            "timeline_onset": "10 minutes",
            "aggravating_or_alleviating_factors": ["bleeding controlled with pressure"]
        }
        risk = {
            "red_flags_present": [],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": []
        }
        result = route_patient(entities, risk)
        self.assertIn(result['care_tier'], ['NON-URGENT', 'HOME-CARE'])
    
    def test_mild_joint_pain_non_urgent(self):
        """Mild joint pain without red flags should route to NON-URGENT"""
        entities = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "Knee pain from overexertion",
            "symptoms_found": ["joint pain", "stiffness"],
            "timeline_onset": "1 day",
            "aggravating_or_alleviating_factors": ["pain with activity"]
        }
        risk = {
            "red_flags_present": [],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": []
        }
        result = route_patient(entities, risk)
        self.assertIn(result['care_tier'], ['NON-URGENT', 'HOME-CARE'])


class TestHomeCareRoutability(unittest.TestCase):
    """Test cases for HOME-CARE tier (lowest acuity)"""
    
    def test_stable_chronic_condition_home_care(self):
        """Stable chronic condition should route to HOME-CARE or NON-URGENT"""
        entities = {
            "age": 72,
            "sex": "male",
            "chief_complaint": "Routine followup for arthritis",
            "symptoms_found": ["joint pain"],
            "timeline_onset": "chronic",
            "aggravating_or_alleviating_factors": ["stable on current medication"]
        }
        risk = {
            "red_flags_present": [],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": []
        }
        result = route_patient(entities, risk)
        self.assertIn(result['care_tier'], ['HOME-CARE', 'NON-URGENT'])
    
    def test_medication_refill_home_care(self):
        """Medication refill request should route to HOME-CARE or NON-URGENT"""
        entities = {
            "age": 48,
            "sex": "female",
            "chief_complaint": "Need blood pressure medication refill",
            "symptoms_found": [],
            "timeline_onset": "non-acute",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": [],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": []
        }
        result = route_patient(entities, risk)
        self.assertIn(result['care_tier'], ['HOME-CARE', 'NON-URGENT'])


class TestConservativeRoutingLogic(unittest.TestCase):
    """Test conservative routing: when in doubt, route up"""
    
    def test_uncertain_with_red_flag_escalates(self):
        """Any red flag should escalate to higher acuity"""
        entities = {
            "age": 58,
            "sex": "male",
            "chief_complaint": "Chest discomfort",
            "symptoms_found": ["chest discomfort"],
            "timeline_onset": "intermittent",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Possible cardiac chest pain"],
            "critical_missing_data_points": ["EKG", "Cardiac markers"],
            "worst_case_scenarios_to_exclude": ["ACS"]
        }
        result = route_patient(entities, risk)
        # Should not be HOME-CARE due to red flag
        self.assertNotEqual(result['care_tier'], 'HOME-CARE')
    
    def test_multiple_missing_data_points_escalates(self):
        """Multiple missing critical data points should escalate"""
        entities = {
            "age": 62,
            "sex": "female",
            "chief_complaint": "Chest pain",
            "symptoms_found": ["chest pain"],
            "timeline_onset": "2 hours",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Chest pain"],
            "critical_missing_data_points": [
                "EKG findings",
                "Cardiac markers",
                "Blood pressure",
                "Oxygen saturation",
                "Risk factors"
            ],
            "worst_case_scenarios_to_exclude": ["AMI", "ACS", "PE"]
        }
        result = route_patient(entities, risk)
        # Should be EMERGENCY due to red flag + missing data
        self.assertEqual(result['care_tier'], 'EMERGENCY')


class TestImmediateActionsGeneration(unittest.TestCase):
    """Test immediate actions are appropriate for each tier"""
    
    def test_emergency_includes_911(self):
        """EMERGENCY tier should include 911 in immediate actions"""
        entities = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "Chest pain",
            "symptoms_found": ["chest pain"],
            "timeline_onset": "acute",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Chest pain/pressure (ACS/MI risk)"],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": []
        }
        result = route_patient(entities, risk)
        self.assertTrue(any('911' in action.lower() for action in result['immediate_actions']))
    
    def test_urgent_includes_er_recommendation(self):
        """URGENT tier should include ER visit recommendation"""
        entities = {
            "age": 68,
            "sex": "male",
            "chief_complaint": "High fever",
            "symptoms_found": ["fever"],
            "timeline_onset": "overnight",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["High fever"],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": []
        }
        result = route_patient(entities, risk)
        actions_text = ' '.join(result['immediate_actions']).lower()
        self.assertIn('emergency', actions_text)
    
    def test_non_urgent_suggests_urgent_care(self):
        """NON-URGENT tier should suggest urgent care or PCP"""
        entities = {
            "age": 35,
            "sex": "female",
            "chief_complaint": "Mild rash",
            "symptoms_found": ["rash"],
            "timeline_onset": "3 days",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": [],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": []
        }
        result = route_patient(entities, risk)
        actions_text = ' '.join(result['immediate_actions']).lower()
        # Should suggest urgent care or PCP, not ER
        self.assertNotIn('911', actions_text)


class TestPatientMessaging(unittest.TestCase):
    """Test patient-facing messages are clear and actionable"""
    
    def test_emergency_message_clear_and_actionable(self):
        """Emergency message should be clear about immediate action"""
        entities = {
            "age": 55,
            "sex": "male",
            "chief_complaint": "Chest pain",
            "symptoms_found": ["chest pain"],
            "timeline_onset": "acute",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Chest pain/pressure (ACS/MI risk)"],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": []
        }
        result = route_patient(entities, risk)
        msg = result['patient_facing_message'].lower()
        self.assertIn('emergency', msg)
        self.assertIn('911', msg)
    
    def test_no_medical_jargon_in_patient_message(self):
        """Patient messages should avoid medical jargon"""
        entities = {
            "age": 45,
            "sex": "female",
            "chief_complaint": "Chest pain",
            "symptoms_found": ["chest pain"],
            "timeline_onset": "1 hour",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Chest pain/pressure (ACS/MI risk)"],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": ["AMI", "ACS"]
        }
        result = route_patient(entities, risk)
        msg = result['patient_facing_message'].lower()
        # Should not contain medical abbreviations
        self.assertNotIn('ami', msg)
        self.assertNotIn('acs', msg)
    
    def test_patient_message_empathetic(self):
        """Patient messages should be empathetic and reassuring where appropriate"""
        entities = {
            "age": 35,
            "sex": "female",
            "chief_complaint": "Mild cold",
            "symptoms_found": ["runny nose"],
            "timeline_onset": "2 days",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": [],
            "critical_missing_data_points": [],
            "worst_case_scenarios_to_exclude": []
        }
        result = route_patient(entities, risk)
        msg = result['patient_facing_message']
        # Should not be alarmist for mild conditions
        self.assertNotIn('emergency', msg.lower())


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_elderly_patient_with_multiple_symptoms(self):
        """Elderly patient should be treated conservatively"""
        entities = {
            "age": 85,
            "sex": "male",
            "chief_complaint": "Feeling unwell",
            "symptoms_found": ["weakness", "dizziness"],
            "timeline_onset": "acute",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Acute weakness in elderly"],
            "critical_missing_data_points": ["Vital signs", "Mental status baseline"],
            "worst_case_scenarios_to_exclude": ["Stroke", "MI", "Sepsis"]
        }
        result = route_patient(entities, risk)
        # Should not be HOME-CARE for elderly with acute symptoms
        self.assertNotEqual(result['care_tier'], 'HOME-CARE')
    
    def test_pediatric_patient_high_fever(self):
        """Pediatric patient with high fever should be urgent"""
        entities = {
            "age": 3,
            "sex": "male",
            "chief_complaint": "High fever",
            "symptoms_found": ["fever", "lethargy"],
            "timeline_onset": "overnight",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["High fever in pediatric patient"],
            "critical_missing_data_points": ["Temperature reading", "Recent exposures"],
            "worst_case_scenarios_to_exclude": ["Meningitis", "Sepsis"]
        }
        result = route_patient(entities, risk)
        # Should be at least URGENT
        self.assertIn(result['care_tier'], ['URGENT', 'EMERGENCY'])
    
    def test_pregnant_patient_with_vaginal_bleeding(self):
        """Pregnant patient with vaginal bleeding should be URGENT/EMERGENCY"""
        entities = {
            "age": 28,
            "sex": "female",
            "chief_complaint": "Vaginal bleeding",
            "symptoms_found": ["vaginal bleeding", "abdominal pain"],
            "timeline_onset": "this morning",
            "aggravating_or_alleviating_factors": []
        }
        risk = {
            "red_flags_present": ["Vaginal bleeding in pregnancy"],
            "critical_missing_data_points": ["Gestational age", "Fetal heart rate"],
            "worst_case_scenarios_to_exclude": ["Miscarriage", "Placental abruption", "Ectopic rupture"]
        }
        result = route_patient(entities, risk)
        self.assertIn(result['care_tier'], ['URGENT', 'EMERGENCY'])


def run_tests():
    """Run all tests with verbose output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEmergencyTriage))
    suite.addTests(loader.loadTestsFromTestCase(TestUrgentTriage))
    suite.addTests(loader.loadTestsFromTestCase(TestNonUrgentTriage))
    suite.addTests(loader.loadTestsFromTestCase(TestHomeCareRoutability))
    suite.addTests(loader.loadTestsFromTestCase(TestConservativeRoutingLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestImmediateActionsGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestPatientMessaging))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
