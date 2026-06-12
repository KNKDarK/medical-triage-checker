"""
Conservative Clinical Triage Router

Routes patients to appropriate care tiers based on extracted clinical features
and identified risk factors. Uses conservative decision-making to ensure patient safety.

CARE TIERS:
- EMERGENCY: Imminent threat to life or organ system (911/ER NOW)
- URGENT: Clinical evaluation needed within 4-24 hours
- NON-URGENT: Stable, can schedule outpatient care
- HOME-CARE: Minor, self-limiting issue, can manage at home

PHILOSOPHY: "When in doubt, route up" - Conservative approach prioritizes safety.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class TriageDecision:
    """Structured output for triage routing decision."""
    care_tier: str  # "EMERGENCY" | "URGENT" | "NON-URGENT" | "HOME-CARE"
    clinical_justification: str
    immediate_actions: List[str] = field(default_factory=list)
    patient_facing_message: str = ""

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self), indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ClinicalTriageRouter:
    """Routes patients to appropriate care tiers."""

    # EMERGENCY ROUTING CRITERIA
    # Any of these red flags warrant immediate emergency routing
    EMERGENCY_CRITERIA = {
        # Cardiovascular emergencies
        'chest_pain': {
            'keywords': ['chest pain', 'chest pressure', 'crushing', 'aortic'],
            'justification': 'Acute chest pain requires immediate cardiac evaluation',
            'actions': ['Call 911 or go to emergency room immediately', 
                       'Do not drive yourself if possible',
                       'Have someone drive you or call ambulance'],
            'patient_message': 'Chest pain needs emergency care right now. Call 911 or have someone drive you to the nearest emergency room immediately. Do not drive yourself.'
        },
        
        # Respiratory emergencies
        'severe_respiratory': {
            'keywords': ['severe respiratory distress', 'unable to breathe', 'critical respiratory', 'stridor'],
            'justification': 'Severe respiratory compromise requires immediate airway management',
            'actions': ['Call 911 immediately',
                       'Sit upright to ease breathing',
                       'Do not wait for transport approval'],
            'patient_message': 'You\'re having severe trouble breathing and need emergency help right now. Call 911 immediately and sit upright. Do not try to drive yourself.'
        },
        
        # Neurological emergencies
        'stroke_symptoms': {
            'keywords': ['sudden weakness', 'acute focal weakness', 'sudden numbness', 'speech difficulty', 'facial droop'],
            'justification': 'Acute neurological deficit is a stroke emergency (time-critical for intervention)',
            'actions': ['Call 911 immediately - note the time symptoms started',
                       'Do not give anything to eat or drink',
                       'Keep patient lying flat or in recovery position',
                       'Note exact time of symptom onset - this is critical for treatment'],
            'patient_message': 'You\'re showing signs of stroke, which is a medical emergency that needs immediate treatment. Call 911 RIGHT NOW and remember what time your symptoms started. This timing is very important for treatment options.'
        },
        
        # Severe bleeding/trauma
        'severe_bleeding': {
            'keywords': ['severe bleeding', 'active bleeding', 'uncontrolled', 'hemorrhage', 'severe trauma', 'head injury with'],
            'justification': 'Uncontrolled bleeding or traumatic injury requires immediate intervention',
            'actions': ['Call 911',
                       'Apply firm pressure with clean cloth if bleeding',
                       'Elevate injured limb if possible',
                       'Do not remove objects impaled in wounds'],
            'patient_message': 'You have severe bleeding or a serious injury that needs emergency care. Call 911 immediately. If you can, apply firm pressure to stop the bleeding with a clean cloth.'
        },
        
        # Loss of consciousness/severe altered mental status
        'altered_consciousness': {
            'keywords': ['loss of consciousness', 'unconscious', 'unresponsive', 'severely altered mental status'],
            'justification': 'Loss of consciousness requires immediate emergency evaluation',
            'actions': ['Call 911',
                       'Place in recovery position (on side)',
                       'Monitor breathing',
                       'Do not give anything to eat/drink'],
            'patient_message': 'Loss of consciousness or extreme confusion is a medical emergency. Call 911 immediately. If the person is unresponsive, place them on their side and watch their breathing.'
        },
        
        # Severe allergic reaction/anaphylaxis
        'anaphylaxis': {
            'keywords': ['anaphylaxis', 'throat swelling', 'severe allergic', 'airway obstruction'],
            'justification': 'Anaphylaxis can rapidly progress to airway obstruction (life-threatening)',
            'actions': ['Call 911 immediately',
                       'Administer epinephrine if available',
                       'Have person lie flat with legs elevated',
                       'Have second dose of epinephrine ready'],
            'patient_message': 'Severe allergic reaction is a medical emergency requiring immediate care. Call 911 right away. If you have an EpiPen, use it now.'
        },
        
        # Severe infection with shock
        'septic_shock': {
            'keywords': ['septic shock', 'hypotension', 'critical fever', 'fever with hypotension', 'sepsis with'],
            'justification': 'Septic shock requires immediate IV intervention and antibiotics',
            'actions': ['Call 911',
                       'Lie flat with legs elevated',
                       'Keep warm with blankets',
                       'Try to drink small sips of water if able'],
            'patient_message': 'Signs of severe infection with shock require emergency care. Call 911 immediately. Lie flat and keep warm while waiting.'
        },
        
        # Suicidal/homicidal crisis
        'psychiatric_crisis': {
            'keywords': ['suicidal', 'homicidal', 'suicidal ideation', 'homicidal thoughts'],
            'justification': 'Suicidal or homicidal ideation requires immediate crisis intervention',
            'actions': ['Call 911 or crisis hotline',
                       'If person is in immediate danger, call police emergency',
                       'Do not leave person alone',
                       'Remove access to means of self-harm'],
            'patient_message': 'If you\'re thinking about hurting yourself or others, this is a crisis that needs immediate help. Call 911 or the National Suicide Prevention Lifeline at 988 RIGHT NOW. Help is available.'
        },
        
        # Poisoning/overdose
        'toxin_exposure': {
            'keywords': ['poisoning', 'overdose', 'ingestion', 'toxin'],
            'justification': 'Toxin exposure requires immediate poison control and medical intervention',
            'actions': ['Call Poison Control: 1-800-222-1222',
                       'Call 911 if patient is unconscious or severely symptomatic',
                       'Have bottle/container of substance ready for provider',
                       'Do not induce vomiting unless instructed'],
            'patient_message': 'Poisoning or overdose needs emergency help. Call Poison Control immediately at 1-800-222-1222. They will tell you exactly what to do. If you\'re having trouble breathing or are unconscious, call 911.'
        },
    }

    # URGENT ROUTING CRITERIA
    # These presentations need medical evaluation within hours
    URGENT_CRITERIA = {
        'moderate_chest_pain': {
            'keywords': ['chest pain', 'moderate breathing difficulty', 'abnormal vitals'],
            'require_exclusion': ['chest_pain', 'severe_respiratory'],  # Don't double-count emergencies
            'justification': 'Moderate chest pain or respiratory symptoms require urgent evaluation',
            'actions': ['Go to urgent care or ER within 1-2 hours',
                       'Call your doctor for guidance',
                       'Monitor symptoms closely',
                       'Have someone available in case symptoms worsen'],
            'patient_message': 'Your symptoms need to be evaluated by a healthcare provider today. Go to an urgent care center or emergency room within the next 1-2 hours, or call your doctor for guidance on where to go.'
        },
        
        'high_fever': {
            'keywords': ['high fever', 'fever with altered mental', 'fever with weakness'],
            'require_exclusion': ['septic_shock'],
            'justification': 'High fever with systemic symptoms suggests serious infection',
            'actions': ['See doctor or go to urgent care today',
                       'Do not wait for regular appointment',
                       'Stay hydrated',
                       'Seek immediate care if symptoms worsen'],
            'patient_message': 'Your fever and other symptoms need to be checked by a doctor today. Go to an urgent care center or call your doctor right away for an urgent appointment. Don\'t wait for a regular appointment.'
        },
        
        'severe_headache': {
            'keywords': ['severe headache', 'worst headache', 'headache with fever', 'headache with neck stiffness'],
            'require_exclusion': ['stroke_symptoms'],
            'justification': 'Severe headache may indicate serious condition (SAH/meningitis)',
            'actions': ['Go to ER or urgent care today',
                       'Do not delay evaluation',
                       'Note any neck stiffness, photophobia, or fever',
                       'Call 911 if symptoms worsen dramatically'],
            'patient_message': 'Severe headaches need urgent medical evaluation. Go to an emergency room or urgent care center today. This is not something to wait on.'
        },
        
        'severe_pain': {
            'keywords': ['severe pain', 'acute pain', 'sudden severe'],
            'require_exclusion': ['chest_pain', 'severe_bleeding'],
            'justification': 'Severe acute pain requires urgent evaluation to rule out serious causes',
            'actions': ['Go to urgent care or ER today',
                       'Avoid food and fluids until evaluated',
                       'Take pain medication if appropriate',
                       'Have imaging or lab work ready'],
            'patient_message': 'Your severe pain needs prompt medical attention. Go to an urgent care center or emergency room today. Don\'t wait - this needs to be checked out quickly.'
        },
        
        'altered_mental_status': {
            'keywords': ['confused', 'disoriented', 'altered mental', 'confusion'],
            'require_exclusion': ['loss_of_consciousness'],
            'justification': 'Altered mental status requires urgent evaluation to identify cause',
            'actions': ['Go to urgent care or ER today',
                       'Have someone stay with patient',
                       'Bring list of medications',
                       'Check blood sugar if diabetic'],
            'patient_message': 'Confusion or unusual behavior needs urgent medical evaluation. Go to an urgent care center or emergency room today. Have someone go with you if possible.'
        },
        
        'severe_vomiting_diarrhea': {
            'keywords': ['persistent vomiting', 'severe diarrhea', 'unable to keep down', 'bloody vomit'],
            'require_exclusion': ['severe_bleeding'],
            'justification': 'Severe GI symptoms lead to dehydration and require urgent evaluation',
            'actions': ['Go to urgent care or ER today',
                       'Sip small amounts of clear fluids',
                       'Do not eat solid food yet',
                       'Monitor for signs of dehydration'],
            'patient_message': 'Severe vomiting or diarrhea can quickly lead to dehydration. Go to an urgent care center or emergency room today for IV fluids and evaluation.'
        },
    }

    # NON-URGENT ROUTING CRITERIA
    # These can be scheduled for routine outpatient care
    NON_URGENT_CRITERIA = {
        'mild_respiratory': {
            'keywords': ['cough', 'sore throat', 'mild respiratory', 'runny nose', 'congestion'],
            'require_exclusion': ['severe_respiratory', 'high_fever'],
            'justification': 'Mild respiratory symptoms are typically viral and self-limited',
            'actions': ['Schedule routine doctor visit',
                       'Use home remedies (steam, rest, fluids)',
                       'Over-the-counter medications as needed',
                       'Seek care if symptoms worsen'],
            'patient_message': 'Your cold or mild cough is probably viral and will likely get better on its own. Drink plenty of fluids, get rest, and use over-the-counter medications if needed. Schedule a regular doctor visit if symptoms don\'t improve in a week or get worse.'
        },
        
        'mild_gi': {
            'keywords': ['mild nausea', 'mild stomach ache', 'mild diarrhea', 'indigestion'],
            'require_exclusion': ['severe_pain', 'severe_vomiting'],
            'justification': 'Mild GI symptoms are often self-limiting',
            'actions': ['Try dietary modifications',
                       'Rest and hydration',
                       'Over-the-counter antacids if appropriate',
                       'Schedule routine visit if persistent'],
            'patient_message': 'Your mild stomach symptoms often improve with rest and fluids. Eat bland foods, stay hydrated, and avoid things that irritate your stomach. If symptoms persist beyond a week, schedule a doctor visit.'
        },
        
        'minor_ache_pain': {
            'keywords': ['mild pain', 'ache', 'soreness', 'minor'],
            'require_exclusion': ['severe_pain', 'chest_pain'],
            'justification': 'Minor aches and pains are typically musculoskeletal',
            'actions': ['Rest the affected area',
                       'Ice for first 48 hours, then heat',
                       'Over-the-counter pain relief',
                       'Gentle stretching as tolerated'],
            'patient_message': 'Minor aches and pains often improve with rest and time. Use ice, over-the-counter pain relief, and rest the area. You can usually manage this at home.'
        },
        
        'skin_issues': {
            'keywords': ['rash', 'itching', 'mild skin', 'wound care'],
            'require_exclusion': ['severe_bleeding', 'anaphylaxis'],
            'justification': 'Minor skin issues can typically be managed outpatient',
            'actions': ['Keep area clean and dry',
                       'Use over-the-counter creams if appropriate',
                       'Monitor for signs of infection',
                       'Schedule routine visit if persists'],
            'patient_message': 'Minor skin issues usually clear up with good hygiene and time. Keep the area clean and dry. Use over-the-counter creams if you need them. Schedule a routine doctor visit if it doesn\'t improve or gets worse.'
        },
    }

    # HOME-CARE ROUTING CRITERIA
    # Minor, self-limiting issues manageable at home
    HOME_CARE_CRITERIA = {
        'minor_symptoms': {
            'keywords': ['mild', 'minor', 'minimal'],
            'require_exclusion': ['severe', 'acute', 'emergency'],
            'justification': 'Minor symptoms typically resolve with supportive care',
            'actions': ['Rest and hydration',
                       'Monitor symptoms',
                       'Use over-the-counter remedies as needed',
                       'Contact doctor only if symptoms worsen or persist'],
            'patient_message': 'Your symptoms are mild and should improve with rest, fluids, and time. Most viral illnesses resolve on their own. Keep an eye on how you\'re feeling, and call your doctor if things get worse or don\'t improve in a week.'
        },
    }

    def __init__(self):
        """Initialize the triage router."""
        pass

    def route(self, extracted_entities: Dict[str, Any],
              risk_assessment: Dict[str, Any],
              additional_vitals: Optional[Dict[str, Any]] = None) -> TriageDecision:
        """
        Route patient to appropriate care tier.
        
        Args:
            extracted_entities: Output from MedicalEntityExtractor
            risk_assessment: Output from ClinicalRiskAssessmentEngine
            additional_vitals: Optional vital signs dict
            
        Returns:
            TriageDecision with care tier assignment
        """
        # CONSERVATIVE ROUTING: Check emergency first, then urgent, etc.
        # "When in doubt, route up"
        
        # Step 1: Check for RED FLAGS from risk assessment (strongest signal)
        if risk_assessment.get('red_flags_present') and len(risk_assessment['red_flags_present']) > 0:
            red_flags = risk_assessment['red_flags_present']
            # Most red flags go to EMERGENCY
            emergency_keywords = [
                'chest pain', 'breathing', 'respiratory', 'stroke', 'weakness', 'altered mental',
                'unconscious', 'unresponsive', 'severe bleeding', 'anaphylaxis',
                'shock', 'septic', 'suicidal', 'homicidal', 'poisoning', 'overdose'
            ]
            for flag in red_flags:
                flag_lower = flag.lower()
                for emerg_keyword in emergency_keywords:
                    if emerg_keyword in flag_lower:
                        # This is a critical red flag
                        return self._create_decision_from_red_flag(
                            'EMERGENCY', flag, extracted_entities, risk_assessment
                        )
            
            # If we have red flags but they're not EMERGENCY-level
            # They should go to URGENT at minimum
            return self._create_decision_from_red_flag(
                'URGENT', red_flags[0], extracted_entities, risk_assessment
            )
        
        # Step 2: Prepare searchable text for pattern matching
        searchable_text = self._prepare_searchable_text(extracted_entities, risk_assessment, additional_vitals)
        
        # Step 3: Check EMERGENCY criteria by pattern
        emergency_match = self._check_criteria_match(searchable_text, self.EMERGENCY_CRITERIA)
        if emergency_match:
            return self._create_decision(
                'EMERGENCY',
                emergency_match,
                extracted_entities,
                risk_assessment
            )
        
        # Step 4: Check URGENT criteria
        urgent_match = self._check_criteria_match(searchable_text, self.URGENT_CRITERIA)
        if urgent_match:
            return self._create_decision(
                'URGENT',
                urgent_match,
                extracted_entities,
                risk_assessment
            )
        
        # Step 5: Check NON-URGENT criteria
        non_urgent_match = self._check_criteria_match(searchable_text, self.NON_URGENT_CRITERIA)
        if non_urgent_match:
            return self._create_decision(
                'NON-URGENT',
                non_urgent_match,
                extracted_entities,
                risk_assessment
            )
        
        # Step 6: Default to HOME-CARE if minimal symptoms
        return self._create_decision(
            'HOME-CARE',
            self.HOME_CARE_CRITERIA['minor_symptoms'],
            extracted_entities,
            risk_assessment
        )

    def _prepare_searchable_text(self, extracted_entities: Dict[str, Any],
                                 risk_assessment: Dict[str, Any],
                                 additional_vitals: Optional[Dict[str, Any]] = None) -> str:
        """Prepare combined searchable text from all inputs."""
        text_parts = []
        
        # Add extracted entities
        if extracted_entities.get('chief_complaint'):
            text_parts.append(extracted_entities['chief_complaint'])
        
        if extracted_entities.get('symptoms_found'):
            text_parts.append(' '.join(extracted_entities['symptoms_found']))
        
        # Add red flags from risk assessment
        if risk_assessment.get('red_flags_present'):
            text_parts.append(' '.join(risk_assessment['red_flags_present']))
        
        # Add vital signs
        if additional_vitals:
            if additional_vitals.get('blood_pressure'):
                text_parts.append(f"blood pressure {additional_vitals['blood_pressure']}")
            if additional_vitals.get('temperature'):
                text_parts.append(f"temperature {additional_vitals['temperature']}")
            if additional_vitals.get('heart_rate'):
                text_parts.append(f"heart rate {additional_vitals['heart_rate']}")
            if additional_vitals.get('spo2'):
                text_parts.append(f"SpO2 {additional_vitals['spo2']}")
        
        return ' '.join(text_parts).lower()

    def _check_criteria_match(self, searchable_text: str, criteria_dict: Dict) -> Optional[Dict]:
        """Check if any criteria in dictionary matches the text."""
        import re
        
        for category, criteria in criteria_dict.items():
            keywords = criteria.get('keywords', [])
            
            for keyword in keywords:
                # Use word boundaries for better matching to avoid partial matches
                # e.g., "pain" should not match "chronic stable pain"
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, searchable_text):
                    # Check if we should exclude based on other criteria
                    if 'require_exclusion' in criteria:
                        should_exclude = False
                        for exclusion_key in criteria['require_exclusion']:
                            # For now, simple check - could be enhanced
                            pass
                    
                    return criteria
        
        return None

    def _create_decision(self, care_tier: str, criteria: Dict,
                        extracted_entities: Dict[str, Any],
                        risk_assessment: Dict[str, Any]) -> TriageDecision:
        """Create a triage decision."""
        return TriageDecision(
            care_tier=care_tier,
            clinical_justification=criteria.get('justification', 'Clinical evaluation required'),
            immediate_actions=criteria.get('actions', []),
            patient_facing_message=criteria.get('patient_message', '')
        )

    def _create_decision_from_red_flag(self, care_tier: str, red_flag: str,
                                      extracted_entities: Dict[str, Any],
                                      risk_assessment: Dict[str, Any]) -> TriageDecision:
        """Create a triage decision based on a red flag."""
        # Map red flag to appropriate template
        templates = {
            'EMERGENCY': {
                'justification': f'Critical red flag detected: {red_flag}',
                'actions': [
                    'Call 911 immediately',
                    'Do not delay seeking emergency care',
                    'Inform provider of this concern'
                ],
                'patient_message': 'This is a medical emergency. Call 911 immediately. Do not wait or drive yourself to the hospital.'
            },
            'URGENT': {
                'justification': f'Red flag identified requiring urgent evaluation: {red_flag}',
                'actions': [
                    'Go to emergency room or urgent care immediately',
                    'Do not delay',
                    'Bring list of current medications'
                ],
                'patient_message': 'Your symptoms need urgent medical evaluation. Go to an emergency room or urgent care center right away.'
            }
        }
        
        template = templates.get(care_tier, templates['URGENT'])
        return TriageDecision(
            care_tier=care_tier,
            clinical_justification=template['justification'],
            immediate_actions=template['actions'],
            patient_facing_message=template['patient_message']
        )


def route_patient(extracted_entities: Dict[str, Any],
                 risk_assessment: Dict[str, Any],
                 additional_vitals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to route patient to care tier.
    
    Args:
        extracted_entities: Output from MedicalEntityExtractor
        risk_assessment: Output from ClinicalRiskAssessmentEngine
        additional_vitals: Optional vital signs dict
        
    Returns:
        Dictionary with triage decision
    """
    router = ClinicalTriageRouter()
    decision = router.route(extracted_entities, risk_assessment, additional_vitals)
    return decision.to_dict()


def route_patient_json(extracted_entities: Dict[str, Any],
                      risk_assessment: Dict[str, Any],
                      additional_vitals: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience function to route patient and return JSON.
    
    Args:
        extracted_entities: Output from MedicalEntityExtractor
        risk_assessment: Output from ClinicalRiskAssessmentEngine
        additional_vitals: Optional vital signs dict
        
    Returns:
        JSON string with triage decision
    """
    router = ClinicalTriageRouter()
    decision = router.route(extracted_entities, risk_assessment, additional_vitals)
    return decision.to_json()


if __name__ == "__main__":
    # Example usage
    sample_entities = {
        "age": 55,
        "sex": "male",
        "chief_complaint": "Acute chest pain",
        "symptoms_found": ["chest pain", "shortness of breath"],
        "timeline_onset": "30 minutes ago",
        "aggravating_or_alleviating_factors": []
    }
    
    sample_risk = {
        "red_flags_present": ["Chest pain/pressure (ACS/MI risk)"],
        "critical_missing_data_points": [],
        "worst_case_scenarios_to_exclude": ["Acute Myocardial Infarction"]
    }
    
    sample_vitals = {
        "blood_pressure": "145/90",
        "heart_rate": 105,
        "spo2": 94
    }
    
    result = route_patient(sample_entities, sample_risk, sample_vitals)
    print(json.dumps(result, indent=2))
