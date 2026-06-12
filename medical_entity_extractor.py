"""
Expert Medical Entity Extractor

Analyzes raw, messy narrative from patients/caregivers and extracts:
- Demographics (age, sex)
- Chief complaint
- Symptoms
- Timeline/onset
- Aggravating/alleviating factors

GUARDRAIL: Extracts ONLY what is explicitly stated. 
Does NOT interpret, diagnose, or assign severity.
"""

import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class MedicalEntity:
    """Structured output for extracted medical entities."""
    age: Optional[int] = None
    sex: Optional[str] = None
    chief_complaint: str = ""
    symptoms_found: List[str] = None
    timeline_onset: str = ""
    aggravating_or_alleviating_factors: List[str] = None

    def __post_init__(self):
        if self.symptoms_found is None:
            self.symptoms_found = []
        if self.aggravating_or_alleviating_factors is None:
            self.aggravating_or_alleviating_factors = []

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self), indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class MedicalEntityExtractor:
    """Extracts medical entities from raw narrative text."""

    # Common symptom keywords (mapped to normalized forms)
    SYMPTOMS_KEYWORDS = {
        # Respiratory
        r'\bcough(?:ing)?\b': 'cough',
        r'\bsore\s+throat\b': 'sore throat',
        r'\bshortn?ess\s+of\s+breath\b': 'shortness of breath',
        r'\bwheezing?\b': 'wheezing',
        r'\bsneezing?\b': 'sneezing',
        r'\bstuffed?\s+up\b': 'congestion',
        r'\bcongestion\b': 'congestion',
        r'\brunny?\s+nose\b': 'runny nose',
        r'\bnasal\s+congestion\b': 'nasal congestion',
        
        # Digestive
        r'\bnausea\b': 'nausea',
        r'\bvomiting?\b': 'vomiting',
        r'\bdiarrhea\b': 'diarrhea',
        r'\bconstipation\b': 'constipation',
        r'\bstomach\s+ache\b': 'stomach ache',
        r'\babdominal\s+pain\b': 'abdominal pain',
        r'\bheartburn\b': 'heartburn',
        r'\blose\s+appetite\b': 'loss of appetite',
        r'\bloss\s+of\s+appetite\b': 'loss of appetite',
        
        # General/Systemic
        r'\bfever\b': 'fever',
        r'\bfeeling\s+hot\b': 'fever',
        r'\bchills\b': 'chills',
        r'\bfatigue\b': 'fatigue',
        r'\btired(?:ness)?\b': 'fatigue',
        r'\bweak(?:ness)?\b': 'weakness',
        r'\bbody\s+aches?\b': 'body aches',
        r'\bache(?:s)?\b': 'aches',
        r'\bnight\s+sweats\b': 'night sweats',
        r'\bsweating\b': 'sweating',
        r'\bweight\s+loss\b': 'weight loss',
        
        # Neurological
        r'\bheadache\b': 'headache',
        r'\bmigraine\b': 'migraine',
        r'\b(?:blurred?|blurry)\s+vision\b': 'blurred vision',
        r'\bnumb(?:ness)?\b': 'numbness',
        r'\btingling\b': 'tingling',
        r'\bdizziness?\b': 'dizziness',
        r'\bvertig[oe]\b': 'vertigo',
        r'\bconfusion\b': 'confusion',
        r'\bconfused\b': 'confusion',
        r'\bseizure\b': 'seizure',
        r'\bfainting\b': 'fainting',
        r'\b(?:lose|loss\s+of)\s+consciousness\b': 'loss of consciousness',
        r'\btremor(?:s)?\b': 'tremors',
        
        # Pain/Chest
        r'\b(?:chest|thoracic)\s+(?:pain|pressure|tightness|discomfort|ache)\b': 'chest pain',
        r'\bpain\s+(?:\w+\s+)*(?:in\s+)?(?:the\s+)?chest\b': 'chest pain',
        r'\bpressure\s+(?:\w+\s+)*(?:in\s+)?(?:the\s+)?chest\b': 'chest pressure',
        
        # Skin
        r'\brash\b': 'rash',
        r'\bitching?\b': 'itching',
        r'\bswelling\b': 'swelling',
        r'\bswollen\b': 'swelling',
        r'\brunis(?:h)?\b': 'bruising',
        r'\bbruise(?:s|d)?\b': 'bruising',
        r'\bcut\b': 'cut',
        r'\bwound\b': 'wound',
        r'\bburn(?:ing)?\b': 'burn',
        r'\bredness?\b': 'redness',
        r'\bwarmth\b': 'warmth',
        r'\binfection\b': 'infection',
        r'\binfected\b': 'infection',
        r'\bskin\s+discoloration\b': 'skin discoloration',
        
        # Other
        r'\ball(?:ergy|ergic)?\b': 'allergic reaction',
        r'\bhives\b': 'hives',
    }

    # Timeline keywords
    TIMELINE_KEYWORDS = {
        r'\b(\d+)\s*(?:days?|d)\b': '{} days',
        r'\b(\d+)\s*(?:weeks?|w)\b': '{} weeks',
        r'\b(\d+)\s*(?:months?|m)\b': '{} months',
        r'\byesterday\b': 'yesterday',
        r'\btoday\b': 'today',
        r'\bthis\s+morning\b': 'this morning',
        r'\blast\s+night\b': 'last night',
        r'\bsince\s+yesterday\b': 'since yesterday',
        r'\bsince\s+([a-zA-Z]+\s+\d+)\b': 'since {}',
        r'\b(2\d{3})\b': '{}',  # Year
        r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b': '{}',
        r'\baround\s+(\d+)\s*(?:days?|d|weeks?|w|months?|m)\b': 'around {}',
        r'\babout\s+(\d+)\s*(?:days?|d|weeks?|w|months?|m)\b': 'about {}',
    }

    # Aggravating/Alleviating factor keywords
    FACTOR_KEYWORDS = {
        # Alleviating first (more specific)
        r'\b(?:pain|symptoms?|feeling|ache)\s+(?:improves?|better|eases?|relieved?|helps?|reduced?)\s+(?:with|when|after|by)\s+([^,.\n;]+)': 'improves with {}',
        r'\b(?:improves?|better|eases?|helps?|relieved?)\s+(?:with|when|after|by)\s+([^,.\n;]+)': 'improves with {}',
        r'\brelieves?\s+(?:the\s+)?(?:pain|symptoms?|ache)\b': 'provides relief',
        r'\b(rest|sleep|ice|heat|massage|medication)\s+(?:helps?|improves?|eases?)': 'improves with {}',
        r'\b(?:when\s+)?(?:i|taking|took|uses?)\s+(rest|sleep|medication|ibuprofen|aspirin|tylenol)': 'improves with {}',
        r'\b(rest|sleep|lying\s+down|sitting|elevation)\s+(?:makes?|its?)\s+(?:better|improves?)': 'improves with {}',
        
        # Aggravating
        r'\b(?:symptoms?|pain|ache)\s+(?:worsens?|worse|aggravates?|flares?)\s+(?:when|after|with|during)\s+([^,.\n;]+)': 'worsens when {}',
        r'\b(?:worsens?|worse|aggravates?|flares?)\s+(?:when|after|with|during)\s+([^,.\n;]+)': 'worsens when {}',
        r'\b(?:when|if|after)\s+([^,.\n;]{5,30}?)\s+(?:it\s+)?(?:worsens?|gets?\s+worse|hurts?\s+more)': 'worsens when {}',
        r'\b(?:walking|climbing|stairs|exercise|movement|activity|touching|pressure)\s+(?:makes?|worsens?|aggravates?)': 'worsens with {}',
    }

    # Demographics keywords
    AGE_PATTERN = r'(?:age\s+)?(\d{1,3})\s*(?:years?|yo|y\.o\.|yrs?|old)'
    SEX_PATTERN = r'\b(male|female|man|woman|boy|girl|he|she|son|daughter)\b'

    def __init__(self):
        """Initialize the extractor with compiled regex patterns."""
        self.symptom_patterns = {
            re.compile(pattern, re.IGNORECASE): normalized
            for pattern, normalized in self.SYMPTOMS_KEYWORDS.items()
        }

    def extract(self, narrative: str) -> MedicalEntity:
        """
        Extract medical entities from raw narrative text.
        
        Args:
            narrative: Raw text from patient/caregiver
            
        Returns:
            MedicalEntity object with extracted information
        """
        narrative_lower = narrative.lower()
        
        entity = MedicalEntity()
        
        # Extract age
        entity.age = self._extract_age(narrative_lower)
        
        # Extract sex/gender
        entity.sex = self._extract_sex(narrative_lower)
        
        # Extract chief complaint (first sentence or opening clause)
        entity.chief_complaint = self._extract_chief_complaint(narrative)
        
        # Extract symptoms
        entity.symptoms_found = self._extract_symptoms(narrative_lower)
        
        # Extract timeline/onset
        entity.timeline_onset = self._extract_timeline(narrative_lower)
        
        # Extract aggravating/alleviating factors
        entity.aggravating_or_alleviating_factors = self._extract_factors(narrative_lower)
        
        return entity

    def _extract_age(self, text: str) -> Optional[int]:
        """Extract age from text. Returns first valid age found."""
        # Try different age patterns (with negative lookbehind to avoid leading dash)
        patterns = [
            r'(?<![-\d])(?:age\s+)?(\d{1,3})\s*(?:-\s*)?(?:years?|yo|y\.o\.|yrs?|old)',  # no leading dash or digit
            r'(?:is|am|are|was|were)\s+(\d{1,3})(?:\s+years?)?(?:\s+old)?',  # "is 68" or "is 68 years old"
            r'(?:^|\s)age\s+(\d{1,3})',
            r'(?:^|\s)(\d{1,3})\s+(?:years?\s+)?old\b',  # "68 years old"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    age_str = match.group(1).strip()
                    age = int(age_str)
                    # Validate reasonable age range
                    if 0 <= age <= 150:
                        return age
                except (ValueError, IndexError):
                    pass
        return None

    def _extract_sex(self, text: str) -> Optional[str]:
        """Extract sex/gender from text."""
        # Look for explicit sex mentions
        female_patterns = [
            r'\bfemale\b', 
            r'\bwoman\b', 
            r'\bgirl\b', 
            r'\bdaughter\b',
            r'\b(?:she|her)\b'
        ]
        male_patterns = [
            r'\bmale\b', 
            r'\bman\b', 
            r'\bboy\b', 
            r'\bson\b',
            r'\b(?:he|him)\b'
        ]
        
        for pattern in female_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "female"
        
        for pattern in male_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "male"
        
        return None

    def _extract_chief_complaint(self, text: str) -> str:
        """
        Extract chief complaint - typically the first statement.
        Returns the first 1-2 sentences.
        """
        sentences = re.split(r'[.!?]\s+', text)
        if sentences:
            # Clean and return first sentence, max 200 chars
            chief = sentences[0].strip()
            return chief[:200] if len(chief) > 200 else chief
        return ""

    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract all mentioned symptoms."""
        symptoms = set()
        
        for pattern, normalized in self.symptom_patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                symptoms.add(normalized)
        
        return sorted(list(symptoms))

    def _extract_timeline(self, text: str) -> str:
        """Extract timeline/onset information."""
        timelines = []
        
        # Check for explicit onset patterns
        onset_patterns = [
            r'\b(?:started?|began?|onset)\s+([^,.\n]+?)\s+(?:ago|when)\b',
            r'\b(?:for|since)\s+([^,.\n]+?)\s+(?:now|ago)?\b',
            r'\b(\d+)\s+(?:days?|weeks?|months?)\s+ago\b',
        ]
        
        for pattern in onset_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group(1):
                    timelines.append(match.group(1).strip())
        
        if timelines:
            return timelines[0][:100]
        
        return ""

    def _extract_factors(self, text: str) -> List[str]:
        """Extract aggravating and alleviating factors."""
        factors = []
        
        for pattern, template in self.FACTOR_KEYWORDS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if match.lastindex and match.lastindex > 0:
                        # Has captured group
                        factor_text = match.group(1).strip()
                        # Clean up - remove trailing punctuation/conjunctions
                        factor_text = re.sub(r'[,.\n;]+$', '', factor_text)
                        factor_text = re.sub(r'\s+(?:and|or)\s+.*$', '', factor_text)
                        if len(factor_text) > 2:  # Only add if meaningful
                            factors.append(factor_text[:80])
                    else:
                        # No captured group, use template as-is
                        if template not in factors and len(template) > 2:
                            factors.append(template[:80])
                except (IndexError, AttributeError):
                    pass
        
        # Remove duplicates while preserving order
        seen = set()
        unique_factors = []
        for f in factors:
            normalized = f.lower().strip()
            if normalized not in seen and len(f) > 0:
                seen.add(normalized)
                unique_factors.append(f)
        
        return unique_factors[:10]  # Limit to 10 factors


def extract_medical_entities(narrative: str) -> Dict[str, Any]:
    """
    Convenience function to extract medical entities from narrative.
    
    Args:
        narrative: Raw text from patient/caregiver
        
    Returns:
        Dictionary with extracted entities
    """
    extractor = MedicalEntityExtractor()
    entity = extractor.extract(narrative)
    return entity.to_dict()


def extract_medical_entities_json(narrative: str) -> str:
    """
    Convenience function to extract medical entities and return as JSON string.
    
    Args:
        narrative: Raw text from patient/caregiver
        
    Returns:
        JSON string with extracted entities
    """
    extractor = MedicalEntityExtractor()
    entity = extractor.extract(narrative)
    return entity.to_json()


if __name__ == "__main__":
    # Example usage
    sample_narrative = """
    I'm a 42-year-old woman experiencing severe headaches for the past 3 days.
    It started after a stressful day at work. The pain is worse when I look at screens
    and better when I rest in a dark room. I also have some nausea and sensitivity to light.
    I've been taking ibuprofen which helps a bit.
    """
    
    result = extract_medical_entities(sample_narrative)
    print(json.dumps(result, indent=2))
