"""
Clinical Risk Assessment Engine

Analyzes extracted clinical features and identifies:
1. Red flags indicating potential medical emergencies
2. Critical missing data points that would affect risk assessment
3. Worst-case scenarios to rule out or consider

IMPORTANT: This is a clinical decision support tool for EDUCATIONAL purposes.
It does NOT replace professional medical judgment or emergency response protocols.
Always defer to qualified healthcare professionals for actual clinical decisions.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class ClinicalRiskAssessment:
    """Structured output for clinical risk assessment."""
    red_flags_present: List[str] = field(default_factory=list)
    critical_missing_data_points: List[str] = field(default_factory=list)
    worst_case_scenarios_to_exclude: List[str] = field(default_factory=list)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self), indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ClinicalRiskAssessmentEngine:
    """Assesses clinical risk from extracted medical entities."""

    # CRITICAL RED FLAGS - Life-threatening symptoms requiring immediate attention
    CRITICAL_RED_FLAGS = {
        # Cardiovascular emergencies
        r'chest\s+(?:pain|pressure|tightness|discomfort)': 'Chest pain/pressure (ACS/MI risk)',
        r'acute\s+coronary': 'Acute coronary syndrome symptoms',
        r'\bheart\s+attack': 'Suspected myocardial infarction',
        
        # Respiratory emergencies
        r'(?:severe|critical|inability|unable\s+to)\s+(?:shortness\s+of\s+breath|breathe|breathing)': 'Severe respiratory distress',
        r'\bstridor\b': 'Stridor (airway compromise)',
        r'\basthma\s+(?:exacerbation|attack)': 'Acute asthma exacerbation',
        
         # Neurological emergencies
         r'(?:sudden|acute)\s+(?:weakness|numbness|paralysis)': 'Acute focal weakness/paralysis (stroke risk)',
         r'(?:sudden|acute)\s+(?:unilateral\s+)?(?:numbness|weakness)': 'Unilateral neuro deficit',
         r'weakness|paralysis': 'Stroke risk indicator',
         r'(?:sudden|severe|worst)\s+headache': 'Severe headache (SAH/meningitis risk)',
         r'worst\s+headache\s+of\s+(?:my\s+)?life': 'Thunderclap headache (SAH risk)',
         r'\bloss\s+of\s+consciousness\b': 'Loss of consciousness',
         r'\bseizure\b': 'Seizure activity',
        
        # Severe bleeding/trauma
        r'(?:severe|uncontrolled|active)\s+(?:bleeding|hemorrhage)': 'Severe bleeding/hemorrhage',
        r'\bsevere\s+head\s+(?:injury|trauma)(?:\s+with\s+(?:confusion|altered|LOC))?': 'Head injury with neuro changes',
        
        # Severe infection/shock
        r'(?:fever|temperature)\s+(?:very|extremely|critically)?\s*(?:high|≥|>|103|104|105)': 'Critical fever (sepsis risk)',
        r'\bsepsis': 'Sepsis/septic shock indicators',
        r'\bshock': 'Signs of shock',
        
        # Severe allergic reaction
        r'(?:severe|anaphylactic?)\s+(?:allergic\s+)?reaction': 'Severe allergic reaction/anaphylaxis',
        r'\banaphylaxis': 'Anaphylaxis',
        r'\bthroat\s+swelling|swollen\s+throat': 'Throat swelling (airway compromise)',
        
        # Severe abdominal emergencies
        r'(?:severe|acute|sudden)\s+(?:abdominal\s+)?pain': 'Severe abdominal pain (AAA/perforation risk)',
        r'\bperitonitis': 'Peritonitis indicators',
        
        # Other critical conditions
        r'(?:suicidal|homicidal)\s+(?:ideation|thoughts)': 'Suicidal/homicidal ideation',
        r'\bpoisoning|overdose|ingestion': 'Toxin exposure/overdose',
        r'\btraumatic\s+(?:injury|accident)': 'Traumatic injury',
    }

    # CONCERNING SYMPTOMS - Not immediately life-threatening but concerning
    CONCERNING_FLAGS = {
         r'(?:persistent|recurrent)\s+(?:chest|heart)\s+(?:pain|pressure)': 'Persistent chest pain (cardiac evaluation needed)',
         r'(?:sudden|acute)\s+(?:shortness\s+of\s+breath|dyspnea)': 'Acute dyspnea (PE/pneumonia risk)',
         r'(?:severe|intense)\s+headache': 'Severe headache (migraine vs structural lesion)',
         r'(?:severe|intense)\s+abdominal\s+pain': 'Severe abdominal pain (surgical abdomen?)',
         r'(?:high|elevated|≥|>)\s+(?:fever|temperature)(?:\s+\d+)?': 'Elevated fever (infection risk)',
         r'(?:altered|changed|decreased|confused|disoriented|confused)\s+(?:mental\s+)?status': 'Altered mental status',
         r'\bconfusion\b': 'Confusion/altered consciousness',
         r'\bpersistent\s+vomiting': 'Persistent vomiting (dehydration/obstruction)',
         r'(?:severe|profuse)\s+(?:bleeding|hemorrhage)': 'Significant bleeding',
         r'\bstroke\b': 'Possible stroke',
     }

    # CRITICAL DATA GAPS - Missing information that significantly impacts risk assessment
    # Format: (symptom_pattern, required_data_point)
    CRITICAL_GAPS = {
        # Chest pain without cardiac risk stratification
        'chest_pain': {
            'required': [
                'blood pressure reading',
                'heart rate/pulse',
                'EKG findings or description',
                'history of cardiac disease or risk factors',
                'troponin/cardiac markers (or note if not measured)',
            ],
            'trigger_symptoms': r'chest\s+(?:pain|pressure|tightness|discomfort)'
        },
        
        # Respiratory distress without oxygenation data
        'respiratory_distress': {
            'required': [
                'oxygen saturation (SpO2)',
                'respiratory rate',
                'breath sounds (clear/wheezing/crackles)',
                'ability to speak full sentences',
            ],
            'trigger_symptoms': r'(?:shortness\s+of\s+breath|dyspnea|respiratory\s+distress|breathe|breathing)'
        },
        
        # Focal neuro deficit without detailed exam
        'neuro_deficit': {
            'required': [
                'focal weakness location',
                'facial symmetry assessment',
                'speech clarity',
                'time of symptom onset (critical for stroke thrombolysis)',
                'mental status',
            ],
            'trigger_symptoms': r'(?:weakness|numbness|paralysis|stroke|weakness)'
        },
        
        # Severe headache without meningitis/SAH assessment
        'severe_headache': {
            'required': [
                'neck stiffness assessment',
                'fever presence/temperature',
                'photophobia assessment',
                'trauma history',
                'seizure activity',
            ],
            'trigger_symptoms': r'(?:severe|worst|worst\s+of\s+life)?\s*headache'
        },
        
        # High fever without infection source identification
        'high_fever': {
            'required': [
                'infection source (URI/UTI/wound/other)',
                'white blood cell count or infection markers',
                'mental status assessment',
                'hypotension presence/absence',
            ],
            'trigger_symptoms': r'(?:high|elevated|fever|temperature)'
        },
        
        # Severe allergic reaction without airway assessment
        'allergic_reaction': {
            'required': [
                'airway patency assessment',
                'presence/absence of stridor',
                'tongue/throat swelling',
                'epinephrine administration status',
            ],
            'trigger_symptoms': r'(?:allergic|reaction|anaphylaxis|hives|swelling)'
        },
        
        # Severe abdominal pain without surgical assessment
        'severe_abdominal_pain': {
            'required': [
                'location of pain (RLQ/LLQ/epigastric/periumbilical)',
                'abdominal rigidity/guarding',
                'vomiting presence',
                'blood pressure (AAA risk)',
                'imaging (ultrasound/CT) findings or status',
            ],
            'trigger_symptoms': r'(?:severe|acute|sudden).*abdominal\s+pain'
        },
        
        # Altered mental status without cause identification
        'altered_mental_status': {
            'required': [
                'baseline mental status/dementia history',
                'glucose level (hypoglycemia?)',
                'medication/substance use history',
                'recent trauma/head injury',
                'fever presence',
            ],
            'trigger_symptoms': r'(?:altered|confused|disoriented|delirious|decreased\s+consciousness)'
        },
    }

    # WORST-CASE SCENARIOS - Critical diagnoses to consider/rule out
    WORST_CASE_SCENARIOS = {
        'chest_pain': [
            'Acute Myocardial Infarction (AMI)',
            'Acute Coronary Syndrome (ACS)',
            'Aortic Dissection',
            'Pulmonary Embolism (PE)',
            'Tension Pneumothorax',
            'Acute Pericarditis with Tamponade',
            'Esophageal Rupture (Boerhaave Syndrome)',
        ],
        'respiratory_distress': [
            'Acute Asthma Exacerbation',
            'Anaphylaxis',
            'Tension Pneumothorax',
            'Massive Pulmonary Embolism',
            'Acute Epiglottitis',
            'Airway Obstruction',
            'Acute Decompensated Heart Failure (pulmonary edema)',
            'Acute Respiratory Distress Syndrome (ARDS)',
        ],
        'neuro_deficit': [
            'Acute Ischemic Stroke',
            'Hemorrhagic Stroke (Intracerebral or SAH)',
            'Todd\'s Paralysis (post-ictal)',
            'Spinal Cord Compression',
            'Guillain-Barré Syndrome',
            'Wernicke\'s Encephalopathy',
        ],
        'severe_headache': [
            'Subarachnoid Hemorrhage (SAH)',
            'Meningitis/Meningoencephalitis',
            'Subdural Hematoma',
            'Acute Angle-Closure Glaucoma',
            'Malignant Hypertension',
            'Thunderclap Headache',
        ],
        'high_fever': [
            'Sepsis/Septic Shock',
            'Meningitis',
            'Acute Bacterial Endocarditis',
            'Severe Community-Acquired Pneumonia',
            'Acute Hepatitis',
        ],
        'severe_bleeding': [
            'Uncontrolled Hemorrhage/Hypovolemic Shock',
            'Upper GI Bleed with Varices',
            'Intracranial Hemorrhage',
            'Ruptured Abdominal Aortic Aneurysm (AAA)',
            'Disseminated Intravascular Coagulation (DIC)',
        ],
        'allergic_reaction': [
            'Anaphylaxis',
            'Airway Obstruction',
            'Angioedema',
        ],
        'altered_mental_status': [
            'Hypoglycemia/Hyperglycemia',
            'Sepsis/Infection',
            'Intracranial Hemorrhage',
            'Acute Stroke',
            'Hypoxia',
            'Medication Toxicity/Overdose',
        ],
    }

    def __init__(self):
        """Initialize the risk assessment engine."""
        pass

    def assess(self, extracted_entities: Dict[str, Any], 
               additional_vitals: Optional[Dict[str, Any]] = None) -> ClinicalRiskAssessment:
        """
        Assess clinical risk from extracted medical entities.
        
        Args:
            extracted_entities: Output from MedicalEntityExtractor
            additional_vitals: Optional dict with vital signs (BP, HR, SpO2, temp, etc.)
            
        Returns:
            ClinicalRiskAssessment object with findings
        """
        assessment = ClinicalRiskAssessment()
        
        # Combine extracted entities and vitals into searchable text
        searchable_text = self._prepare_searchable_text(extracted_entities, additional_vitals)
        
        # 1. Detect critical red flags
        assessment.red_flags_present = self._detect_red_flags(searchable_text)
        
        # 2. Identify critical missing data points
        assessment.critical_missing_data_points = self._identify_gaps(
            extracted_entities, 
            additional_vitals,
            searchable_text
        )
        
        # 3. Determine worst-case scenarios to consider
        assessment.worst_case_scenarios_to_exclude = self._determine_scenarios(
            assessment.red_flags_present,
            extracted_entities,
            searchable_text
        )
        
        return assessment

    def _prepare_searchable_text(self, extracted_entities: Dict[str, Any], 
                                  additional_vitals: Optional[Dict[str, Any]] = None) -> str:
        """Prepare combined text for pattern matching."""
        text_parts = []
        
        # Add extracted entities
        if extracted_entities.get('chief_complaint'):
            text_parts.append(extracted_entities['chief_complaint'])
        
        if extracted_entities.get('symptoms_found'):
            text_parts.append(' '.join(extracted_entities['symptoms_found']))
        
        if extracted_entities.get('timeline_onset'):
            text_parts.append(extracted_entities['timeline_onset'])
        
        if extracted_entities.get('aggravating_or_alleviating_factors'):
            text_parts.append(' '.join(extracted_entities['aggravating_or_alleviating_factors']))
        
        # Add vital signs
        if additional_vitals:
            if additional_vitals.get('temperature'):
                text_parts.append(f"temperature {additional_vitals['temperature']}")
            if additional_vitals.get('blood_pressure'):
                text_parts.append(f"blood pressure {additional_vitals['blood_pressure']}")
            if additional_vitals.get('heart_rate'):
                text_parts.append(f"heart rate {additional_vitals['heart_rate']}")
            if additional_vitals.get('spo2'):
                text_parts.append(f"SpO2 {additional_vitals['spo2']}")
        
        return ' '.join(text_parts).lower()

    def _detect_red_flags(self, searchable_text: str) -> List[str]:
        """Detect critical red flags from text."""
        import re
        
        red_flags = []
        seen = set()
        
        # Check critical flags first (highest priority)
        for pattern, description in self.CRITICAL_RED_FLAGS.items():
            if re.search(pattern, searchable_text, re.IGNORECASE):
                if description not in seen:
                    red_flags.append(description)
                    seen.add(description)
        
        # Then check concerning flags
        for pattern, description in self.CONCERNING_FLAGS.items():
            if re.search(pattern, searchable_text, re.IGNORECASE):
                if description not in seen:
                    red_flags.append(description)
                    seen.add(description)
        
        return red_flags

    def _identify_gaps(self, extracted_entities: Dict[str, Any],
                       additional_vitals: Optional[Dict[str, Any]],
                       searchable_text: str) -> List[str]:
        """Identify critical missing data points."""
        import re
        
        gaps = []
        seen = set()
        
        for gap_category, gap_info in self.CRITICAL_GAPS.items():
            trigger_pattern = gap_info['trigger_symptoms']
            
            # Check if this gap category applies
            if re.search(trigger_pattern, searchable_text, re.IGNORECASE):
                # Check which required data points are missing
                for required_point in gap_info['required']:
                    if not self._is_data_present(required_point, extracted_entities, additional_vitals, searchable_text):
                        if required_point not in seen:
                            gaps.append(f"MISSING: {required_point}")
                            seen.add(required_point)
        
        return gaps

    def _is_data_present(self, data_point: str, extracted_entities: Dict[str, Any],
                        additional_vitals: Optional[Dict[str, Any]],
                        searchable_text: str) -> bool:
        """Check if a specific data point is present or mentioned."""
        import re
        
        data_point_lower = data_point.lower()
        
        # Check in searchable text
        if re.search(re.escape(data_point), searchable_text, re.IGNORECASE):
            return True
        
        # Check for common patterns
        if 'blood pressure' in data_point_lower and additional_vitals and additional_vitals.get('blood_pressure'):
            return True
        if 'heart rate' in data_point_lower and additional_vitals and additional_vitals.get('heart_rate'):
            return True
        if 'spo2' in data_point_lower and additional_vitals and additional_vitals.get('spo2'):
            return True
        if 'temperature' in data_point_lower and additional_vitals and additional_vitals.get('temperature'):
            return True
        
        # Check patterns in searchable text
        patterns = [
            r'spo2|oxygen\s+saturation',
            r'blood\s+pressure|bp|mmhg',
            r'heart\s+rate|pulse|bpm',
            r'fever|temperature|temp|°f|°c',
            r'ekg|ecg|electrocardiogram',
            r'troponin|cardiac\s+marker',
            r'mental\s+status|consciousness|alert',
        ]
        
        for pattern in patterns:
            if pattern in data_point_lower and re.search(pattern, searchable_text, re.IGNORECASE):
                return True
        
        return False

    def _determine_scenarios(self, red_flags: List[str], 
                            extracted_entities: Dict[str, Any],
                            searchable_text: str) -> List[str]:
        """Determine worst-case scenarios based on symptoms."""
        import re
        
        scenarios = []
        seen = set()
        
        # Determine which scenario category applies
        if re.search(r'chest\s+(?:pain|pressure)', searchable_text, re.IGNORECASE):
            scenarios.extend(self.WORST_CASE_SCENARIOS.get('chest_pain', []))
        
        if re.search(r'(?:shortness\s+of\s+breath|respiratory\s+distress|dyspnea)', 
                    searchable_text, re.IGNORECASE):
            scenarios.extend(self.WORST_CASE_SCENARIOS.get('respiratory_distress', []))
        
        if re.search(r'(?:weakness|numbness|paralysis|stroke)', searchable_text, re.IGNORECASE):
            scenarios.extend(self.WORST_CASE_SCENARIOS.get('neuro_deficit', []))
        
        if re.search(r'(?:severe|worst|worst\s+of\s+life)?\s*headache', 
                    searchable_text, re.IGNORECASE):
            scenarios.extend(self.WORST_CASE_SCENARIOS.get('severe_headache', []))
        
        if re.search(r'(?:high|elevated).*(?:fever|temperature)', searchable_text, re.IGNORECASE):
            scenarios.extend(self.WORST_CASE_SCENARIOS.get('high_fever', []))
        
        if re.search(r'(?:severe|active|uncontrolled).*(?:bleeding|hemorrhage)', 
                    searchable_text, re.IGNORECASE):
            scenarios.extend(self.WORST_CASE_SCENARIOS.get('severe_bleeding', []))
        
        if re.search(r'(?:allergic|anaphylaxis|reaction)', searchable_text, re.IGNORECASE):
            scenarios.extend(self.WORST_CASE_SCENARIOS.get('allergic_reaction', []))
        
        if re.search(r'(?:altered|confused|disoriented)', searchable_text, re.IGNORECASE):
            scenarios.extend(self.WORST_CASE_SCENARIOS.get('altered_mental_status', []))
        
        # Deduplicate and limit
        seen = set()
        unique_scenarios = []
        for scenario in scenarios:
            if scenario not in seen:
                seen.add(scenario)
                unique_scenarios.append(scenario)
        
        return unique_scenarios[:15]  # Limit to top 15


def assess_clinical_risk(extracted_entities: Dict[str, Any],
                        additional_vitals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to assess clinical risk.
    
    Args:
        extracted_entities: Output from MedicalEntityExtractor
        additional_vitals: Optional dict with vital signs
        
    Returns:
        Dictionary with risk assessment results
    """
    engine = ClinicalRiskAssessmentEngine()
    assessment = engine.assess(extracted_entities, additional_vitals)
    return assessment.to_dict()


def assess_clinical_risk_json(extracted_entities: Dict[str, Any],
                             additional_vitals: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience function to assess clinical risk and return as JSON string.
    
    Args:
        extracted_entities: Output from MedicalEntityExtractor
        additional_vitals: Optional dict with vital signs
        
    Returns:
        JSON string with risk assessment results
    """
    engine = ClinicalRiskAssessmentEngine()
    assessment = engine.assess(extracted_entities, additional_vitals)
    return assessment.to_json()


if __name__ == "__main__":
    # Example usage
    sample_entities = {
        "age": 55,
        "sex": "male",
        "chief_complaint": "Acute chest pain for 30 minutes",
        "symptoms_found": ["chest pain", "shortness of breath", "diaphoresis"],
        "timeline_onset": "30 minutes ago",
        "aggravating_or_alleviating_factors": []
    }
    
    sample_vitals = {
        "blood_pressure": "145/90",
        "heart_rate": 105,
        "spo2": 94,
        "temperature": 98.6
    }
    
    result = assess_clinical_risk(sample_entities, sample_vitals)
    print(json.dumps(result, indent=2))
