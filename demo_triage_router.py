"""
Demonstration of Clinical Triage Router

Shows all 4 care tiers with realistic clinical scenarios:
1. EMERGENCY - Acute Myocardial Infarction (55M)
2. URGENT - High Fever with Systemic Symptoms (68M)
3. NON-URGENT - Mild Upper Respiratory Infection (32F)
4. HOME-CARE - Stable Chronic Arthritis (72M)
"""

from medical_entity_extractor import extract_medical_entities
from clinical_risk_assessment import assess_clinical_risk
from clinical_triage_router import route_patient


def demo_emergency():
    """EMERGENCY Scenario: 55-year-old male with acute MI symptoms"""
    print("\n" + "=" * 90)
    print("SCENARIO 1: EMERGENCY - Acute Myocardial Infarction")
    print("=" * 90)
    
    narrative = """
I'm a 55-year-old man and I've got crushing chest pain that started about 30 minutes ago.
The pain radiates to my left arm and jaw. I'm sweating profusely and feel nauseous.
I'm also having shortness of breath. My father had a heart attack at 60. This feels serious.
"""
    
    print(f"\nNarrative: {narrative.strip()}")
    
    # Step 1: Extract entities
    entities = extract_medical_entities(narrative)
    print(f"\n✓ Extracted age: {entities['age']}, sex: {entities['sex']}")
    print(f"✓ Chief complaint: {entities['chief_complaint'][:50]}...")
    print(f"✓ Symptoms: {', '.join(entities['symptoms_found'])}")
    
    # Step 2: Assess risk
    vitals = {"blood_pressure": "155/95", "heart_rate": 108, "spo2": 92}
    risk = assess_clinical_risk(entities, vitals)
    print(f"\n✓ Red flags identified: {len(risk['red_flags_present'])}")
    for flag in risk['red_flags_present'][:2]:
        print(f"  - {flag}")
    
    # Step 3: Route patient
    triage = route_patient(entities, risk, vitals)
    print(f"\n🚨 CARE TIER: {triage['care_tier']}")
    print(f"Justification: {triage['clinical_justification']}")
    print(f"\nImmediate Actions:")
    for i, action in enumerate(triage['immediate_actions'], 1):
        print(f"  {i}. {action}")
    print(f"\nPatient Message: '{triage['patient_facing_message']}'")


def demo_urgent():
    """URGENT Scenario: 68-year-old male with high fever"""
    print("\n" + "=" * 90)
    print("SCENARIO 2: URGENT - High Fever with Systemic Symptoms")
    print("=" * 90)
    
    narrative = """
I'm 68 years old and woke up this morning with a high fever, severe chills, and body aches.
I've been feeling weak and have a headache. I'm also confused about what day it is.
I live alone and am worried because I'm not getting better with over-the-counter medications.
"""
    
    print(f"\nNarrative: {narrative.strip()}")
    
    # Step 1: Extract entities
    entities = extract_medical_entities(narrative)
    print(f"\n✓ Extracted age: {entities['age']}, sex: {entities['sex']}")
    print(f"✓ Chief complaint: {entities['chief_complaint'][:50]}...")
    print(f"✓ Symptoms: {', '.join(entities['symptoms_found'])}")
    
    # Step 2: Assess risk
    vitals = {"temperature": 39.5, "heart_rate": 105}
    risk = assess_clinical_risk(entities, vitals)
    print(f"\n✓ Red flags identified: {len(risk['red_flags_present'])}")
    for flag in risk['red_flags_present'][:2]:
        print(f"  - {flag}")
    
    # Step 3: Route patient
    triage = route_patient(entities, risk, vitals)
    print(f"\n⚠️  CARE TIER: {triage['care_tier']}")
    print(f"Justification: {triage['clinical_justification']}")
    print(f"\nImmediate Actions:")
    for i, action in enumerate(triage['immediate_actions'], 1):
        print(f"  {i}. {action}")
    print(f"\nPatient Message: '{triage['patient_facing_message']}'")


def demo_non_urgent():
    """NON-URGENT Scenario: 32-year-old female with mild cold"""
    print("\n" + "=" * 90)
    print("SCENARIO 3: NON-URGENT - Mild Upper Respiratory Infection")
    print("=" * 90)
    
    narrative = """
I'm 32 and I've had a runny nose, sneezing, and mild cough for 2 days.
My throat is a bit sore but nothing severe. I feel mostly fine otherwise.
No fever. I think I just caught a cold from my coworker.
"""
    
    print(f"\nNarrative: {narrative.strip()}")
    
    # Step 1: Extract entities
    entities = extract_medical_entities(narrative)
    print(f"\n✓ Extracted age: {entities['age']}, sex: {entities['sex']}")
    print(f"✓ Chief complaint: {entities['chief_complaint'][:50]}...")
    print(f"✓ Symptoms: {', '.join(entities['symptoms_found'])}")
    
    # Step 2: Assess risk
    risk = assess_clinical_risk(entities)
    print(f"\n✓ Red flags identified: {len(risk['red_flags_present'])}")
    if not risk['red_flags_present']:
        print(f"  - None (routine viral illness)")
    
    # Step 3: Route patient
    triage = route_patient(entities, risk)
    print(f"\nℹ️  CARE TIER: {triage['care_tier']}")
    print(f"Justification: {triage['clinical_justification']}")
    print(f"\nImmediate Actions:")
    for i, action in enumerate(triage['immediate_actions'], 1):
        print(f"  {i}. {action}")
    print(f"\nPatient Message: '{triage['patient_facing_message']}'")


def demo_home_care():
    """HOME-CARE Scenario: 72-year-old male with stable chronic arthritis"""
    print("\n" + "=" * 90)
    print("SCENARIO 4: HOME-CARE - Stable Chronic Arthritis")
    print("=" * 90)
    
    narrative = """
I'm 72 years old and calling for my regular arthritis followup.
My knee pain is stable on my current medications. No new symptoms.
I've been managing well with my exercise routine and pain is controlled.
Just need to schedule a routine appointment.
"""
    
    print(f"\nNarrative: {narrative.strip()}")
    
    # Step 1: Extract entities
    entities = extract_medical_entities(narrative)
    print(f"\n✓ Extracted age: {entities['age']}, sex: {entities['sex']}")
    print(f"✓ Chief complaint: {entities['chief_complaint'][:50]}...")
    print(f"✓ Symptoms: {', '.join(entities['symptoms_found'])}")
    
    # Step 2: Assess risk
    risk = assess_clinical_risk(entities)
    print(f"\n✓ Red flags identified: {len(risk['red_flags_present'])}")
    if not risk['red_flags_present']:
        print(f"  - None (chronic stable condition)")
    
    # Step 3: Route patient
    triage = route_patient(entities, risk)
    print(f"\n✅ CARE TIER: {triage['care_tier']}")
    print(f"Justification: {triage['clinical_justification']}")
    print(f"\nImmediate Actions:")
    for i, action in enumerate(triage['immediate_actions'], 1):
        print(f"  {i}. {action}")
    print(f"\nPatient Message: '{triage['patient_facing_message']}'")


def main():
    """Run all triage router demonstrations"""
    print("\n" + "=" * 90)
    print(" " * 20 + "CLINICAL TRIAGE ROUTER - DEMONSTRATION")
    print(" " * 15 + "All 4 Care Tiers with Realistic Scenarios")
    print("=" * 90)
    
    demo_emergency()
    demo_urgent()
    demo_non_urgent()
    demo_home_care()
    
    print("\n" + "=" * 90)
    print("DEMONSTRATION COMPLETE")
    print("=" * 90)
    print("\nKey Takeaways:")
    print("• EMERGENCY: Life-threatening symptoms → 911/ER NOW")
    print("• URGENT: Serious symptoms → ER/Urgent care TODAY")
    print("• NON-URGENT: Minor issues → Schedule routine visit")
    print("• HOME-CARE: Stable chronic → Manage at home, schedule routine")
    print("\nConservative Philosophy: When in doubt, route UP (higher acuity)")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()
