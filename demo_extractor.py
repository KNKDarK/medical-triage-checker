"""
Medical Entity Extractor - Demo & Usage Examples

This script demonstrates how to use the Medical Entity Extractor
to extract structured medical information from raw narratives.
"""

from medical_entity_extractor import (
    MedicalEntityExtractor,
    extract_medical_entities,
    extract_medical_entities_json,
)
import json


def demo_basic():
    """Basic usage example."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Usage")
    print("="*60)
    
    narrative = """
    I'm a 42-year-old man with chest pain and shortness of breath
    for the past 2 days. It started after I was shoveling snow.
    The pain gets worse when I walk up stairs and improves when
    I rest and take aspirin.
    """
    
    print("\nNarrative:")
    print(narrative)
    
    result = extract_medical_entities(narrative)
    
    print("\nExtracted Information:")
    print(json.dumps(result, indent=2))


def demo_complex_messy():
    """Complex, messy narrative example."""
    print("\n" + "="*60)
    print("DEMO 2: Complex, Messy Narrative")
    print("="*60)
    
    narrative = """
    Hi, im 35yr old female. Been having this awful headache 4 like
    3 days now... started aft a stressful day at work. When i look
    at my phone or computer, it gets MUCH worse. But when i lay down
    in the dark & rest, it feels way better. Also been feeling nausea
    and kinda dizzy. Light bothers me. Took ibuprofen yesterday and it
    helped some. My mom says i should see a dr.
    """
    
    print("\nNarrative:")
    print(narrative)
    
    result = extract_medical_entities(narrative)
    
    print("\nExtracted Information:")
    print(json.dumps(result, indent=2))


def demo_minimal():
    """Minimal information example."""
    print("\n" + "="*60)
    print("DEMO 3: Minimal Information")
    print("="*60)
    
    narrative = "I have a cough and sore throat."
    
    print("\nNarrative:")
    print(narrative)
    
    result = extract_medical_entities(narrative)
    
    print("\nExtracted Information:")
    print(json.dumps(result, indent=2))


def demo_multiple_symptoms():
    """Multiple symptoms example."""
    print("\n" + "="*60)
    print("DEMO 4: Multiple Symptoms")
    print("="*60)
    
    narrative = """
    48-year-old male presenting with fever (101.5°F), severe cough,
    body aches, fatigue, and chills for 5 days. Symptoms started
    after my coworker got sick. The cough is worse at night and
    when I exercise. Rest helps somewhat. Over-the-counter pain
    relievers help with the aches temporarily.
    """
    
    print("\nNarrative:")
    print(narrative)
    
    result = extract_medical_entities(narrative)
    
    print("\nExtracted Information:")
    print(json.dumps(result, indent=2))


def demo_guardrail():
    """Demonstrate the GUARDRAIL - no diagnosis/interpretation."""
    print("\n" + "="*60)
    print("DEMO 5: GUARDRAIL - No Diagnosis/Interpretation")
    print("="*60)
    
    narrative = """
    My son has been coughing and sneezing for a week. Fever is 100.2.
    We're worried it might be COVID or the flu. He's been feeling tired
    and has a runny nose.
    """
    
    print("\nNarrative:")
    print(narrative)
    print("\nNote: Although the narrative mentions 'COVID' and 'flu',")
    print("the extractor will NOT include these diagnoses. It will ONLY")
    print("extract the explicitly stated symptoms.")
    
    result = extract_medical_entities(narrative)
    
    print("\nExtracted Information:")
    print(json.dumps(result, indent=2))
    
    print("\nValidation:")
    if "covid" not in str(result).lower() and "flu" not in str(result).lower():
        print("✓ PASS: No diagnoses/interpretations extracted (guardrail working)")
    else:
        print("✗ FAIL: Diagnoses were extracted (guardrail broken)")


def demo_json_output():
    """Demonstrate JSON output options."""
    print("\n" + "="*60)
    print("DEMO 6: JSON Output Options")
    print("="*60)
    
    narrative = "35 year old female with 3-day headache, worse with screens, better with rest"
    
    print("\nOption 1: Dictionary output")
    dict_result = extract_medical_entities(narrative)
    print(f"Type: {type(dict_result)}")
    print(dict_result)
    
    print("\nOption 2: JSON string output")
    json_result = extract_medical_entities_json(narrative)
    print(f"Type: {type(json_result)}")
    print(json_result)


def demo_direct_class_usage():
    """Demonstrate direct class usage."""
    print("\n" + "="*60)
    print("DEMO 7: Direct Class Usage")
    print("="*60)
    
    extractor = MedicalEntityExtractor()
    
    narrative = """
    I'm a 52 year old man. Had a sudden onset of severe chest pain
    about 1 hour ago while watching TV. It radiates to my left arm.
    Pain is 8/10 in severity. Shortness of breath as well.
    """
    
    entity = extractor.extract(narrative)
    
    print(f"Age: {entity.age}")
    print(f"Sex: {entity.sex}")
    print(f"Chief Complaint: {entity.chief_complaint}")
    print(f"Symptoms: {entity.symptoms_found}")
    print(f"Timeline: {entity.timeline_onset}")
    print(f"Factors: {entity.aggravating_or_alleviating_factors}")
    
    print("\nConvert to JSON:")
    print(entity.to_json())


def demo_robustness():
    """Demonstrate extraction robustness."""
    print("\n" + "="*60)
    print("DEMO 8: Extraction Robustness")
    print("="*60)
    
    examples = [
        ("UPPERCASE narrative", "42 YEAR OLD WITH SEVERE HEADACHE AND FEVER FOR 2 DAYS"),
        ("Multiple variations", "He's 35yr-old w/ cough (dry), sore throat & nasal congestion x 5 days"),
        ("Informal language", "yo im 28 n got this rly bad backpain and cant walk cuz it hurts"),
        ("Missing spaces/punctuation", "38yearoldwithchestpainandshortneassofbreathlastninehours"),
    ]
    
    for label, narrative in examples:
        print(f"\n{label}:")
        print(f"  Input: {narrative}")
        result = extract_medical_entities(narrative)
        print(f"  Age: {result['age']}, Sex: {result['sex']}")
        print(f"  Symptoms: {result['symptoms_found'][:2] if result['symptoms_found'] else 'None'}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MEDICAL ENTITY EXTRACTOR - DEMONSTRATION")
    print("="*60)
    
    demo_basic()
    demo_complex_messy()
    demo_minimal()
    demo_multiple_symptoms()
    demo_guardrail()
    demo_json_output()
    demo_direct_class_usage()
    demo_robustness()
    
    print("\n" + "="*60)
    print("END OF DEMONSTRATIONS")
    print("="*60)
