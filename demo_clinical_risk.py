"""
Clinical Risk Assessment Engine - Demo & Usage Examples

Demonstrates end-to-end flow from narrative extraction to risk assessment.
"""

import json
from medical_entity_extractor import extract_medical_entities
from clinical_risk_assessment import assess_clinical_risk


def demo_ami_scenario():
    """Demo: Acute Myocardial Infarction"""
    print("\n" + "="*70)
    print("DEMO 1: Acute Chest Pain (MI Risk)")
    print("="*70)
    
    narrative = """
    I'm a 58-year-old man experiencing severe crushing chest pain
    that started 20 minutes ago. The pain radiates to my left arm and jaw.
    I'm also sweating heavily and feel nauseous. I have a history of
    high blood pressure and my father had a heart attack at 60.
    """
    
    print("\nNarrative:")
    print(narrative)
    
    entities = extract_medical_entities(narrative)
    print("\n1. EXTRACTED ENTITIES:")
    print(json.dumps(entities, indent=2))
    
    vitals = {
        "blood_pressure": "155/95",
        "heart_rate": 108,
        "spo2": 94,
        "temperature": 98.8
    }
    
    assessment = assess_clinical_risk(entities, vitals)
    print("\n2. CLINICAL RISK ASSESSMENT:")
    print(f"RED FLAGS: {len(assessment['red_flags_present'])} identified")
    for flag in assessment['red_flags_present']:
        print(f"  ⚠️ {flag}")
    
    print(f"\nCRITICAL DATA GAPS: {len(assessment['critical_missing_data_points'])} identified")
    for gap in assessment['critical_missing_data_points'][:3]:
        print(f"  ❌ {gap}")
    if len(assessment['critical_missing_data_points']) > 3:
        print(f"  ... and {len(assessment['critical_missing_data_points']) - 3} more")
    
    print(f"\nWORST-CASE SCENARIOS TO CONSIDER:")
    for scenario in assessment['worst_case_scenarios_to_exclude'][:5]:
        print(f"  🔴 {scenario}")
    if len(assessment['worst_case_scenarios_to_exclude']) > 5:
        print(f"  ... and {len(assessment['worst_case_scenarios_to_exclude']) - 5} more")


def demo_stroke_scenario():
    """Demo: Acute Stroke"""
    print("\n" + "="*70)
    print("DEMO 2: Acute Stroke (Time-Sensitive)")
    print("="*70)
    
    narrative = """
    My 70-year-old mother suddenly lost the ability to speak clearly.
    Her face appears droopy on the right side. She has sudden weakness
    in her right arm. This all started about 15 minutes ago while she
    was watching TV. She's alert but seems confused. No recent trauma.
    """
    
    print("\nNarrative:")
    print(narrative)
    
    entities = extract_medical_entities(narrative)
    print("\n1. EXTRACTED ENTITIES:")
    print(json.dumps(entities, indent=2))
    
    assessment = assess_clinical_risk(entities)
    print("\n2. CLINICAL RISK ASSESSMENT:")
    print(f"RED FLAGS: {len(assessment['red_flags_present'])} identified")
    for flag in assessment['red_flags_present']:
        print(f"  ⚠️ {flag}")
    
    print(f"\nCRITICAL DATA GAPS:")
    for gap in assessment['critical_missing_data_points']:
        print(f"  ❌ {gap}")
    
    print(f"\nWORST-CASE SCENARIOS:")
    for scenario in assessment['worst_case_scenarios_to_exclude']:
        print(f"  🔴 {scenario}")
    
    print("\n⏱️ NOTE: Time of symptom onset is CRITICAL for stroke treatment!")
    print("   If within 3-4.5 hours, patient may qualify for thrombolysis")


def demo_sepsis_scenario():
    """Demo: Sepsis"""
    print("\n" + "="*70)
    print("DEMO 3: Sepsis (System-Wide Infection)")
    print("="*70)
    
    narrative = """
    72-year-old male with high fever (105.2°F), confusion, and rapid breathing.
    Symptoms started 8 hours ago. Patient recently had urinary catheter placed.
    Also complaining of severe fatigue and chills. Wife reports he's been
    more confused than usual. Blood pressure is lower than his baseline.
    """
    
    print("\nNarrative:")
    print(narrative)
    
    entities = extract_medical_entities(narrative)
    print("\n1. EXTRACTED ENTITIES:")
    print(json.dumps(entities, indent=2))
    
    vitals = {
        "temperature": 105.2,
        "heart_rate": 132,
        "spo2": 87,
        "blood_pressure": "92/58"
    }
    
    assessment = assess_clinical_risk(entities, vitals)
    print("\n2. CLINICAL RISK ASSESSMENT:")
    print(f"RED FLAGS: {len(assessment['red_flags_present'])} identified")
    for flag in assessment['red_flags_present']:
        print(f"  ⚠️ {flag}")
    
    print(f"\nCRITICAL DATA GAPS (first 3):")
    for gap in assessment['critical_missing_data_points'][:3]:
        print(f"  ❌ {gap}")
    
    print(f"\nWORST-CASE SCENARIOS (first 5):")
    for scenario in assessment['worst_case_scenarios_to_exclude'][:5]:
        print(f"  🔴 {scenario}")
    
    print("\n⚠️ URGENT: Patient shows signs of septic shock")
    print("   - Fever + Confusion + Hypotension + Tachycardia")
    print("   - Requires immediate intervention and blood cultures")


def demo_mild_scenario():
    """Demo: Mild Symptoms (Low Risk)"""
    print("\n" + "="*70)
    print("DEMO 4: Common Cold (Low Risk)")
    print("="*70)
    
    narrative = """
    I'm a 32-year-old with a runny nose and slight cough for 3 days.
    Symptoms started after my coworker got sick. No fever. Feeling
    okay otherwise, just annoying congestion. Works as IT specialist.
    """
    
    print("\nNarrative:")
    print(narrative)
    
    entities = extract_medical_entities(narrative)
    print("\n1. EXTRACTED ENTITIES:")
    print(json.dumps(entities, indent=2))
    
    assessment = assess_clinical_risk(entities)
    print("\n2. CLINICAL RISK ASSESSMENT:")
    
    if not assessment['red_flags_present']:
        print("✅ NO RED FLAGS DETECTED")
    else:
        print(f"⚠️ {len(assessment['red_flags_present'])} flags found")
        for flag in assessment['red_flags_present']:
            print(f"   {flag}")
    
    if not assessment['worst_case_scenarios_to_exclude']:
        print("✅ NO CRITICAL SCENARIOS IDENTIFIED")
    else:
        print(f"Scenarios to consider:")
        for scenario in assessment['worst_case_scenarios_to_exclude']:
            print(f"   {scenario}")
    
    print("\n✅ ASSESSMENT: Likely self-limited viral URI")
    print("   Supportive care, hydration, rest")


def demo_data_completeness():
    """Demo: Impact of Data Completeness"""
    print("\n" + "="*70)
    print("DEMO 5: Data Completeness Impact")
    print("="*70)
    
    narrative = "58-year-old with chest pain"
    
    print("\nScenario: Minimal Information")
    print(f"Narrative: '{narrative}'")
    
    entities = extract_medical_entities(narrative)
    
    print("\nA) WITHOUT VITAL SIGNS:")
    assessment_no_vitals = assess_clinical_risk(entities)
    print(f"   Red flags found: {len(assessment_no_vitals['red_flags_present'])}")
    print(f"   Data gaps: {len(assessment_no_vitals['critical_missing_data_points'])}")
    
    vitals = {
        "blood_pressure": "155/95",
        "heart_rate": 115,
        "spo2": 90,
        "temperature": 99.2
    }
    
    print("\nB) WITH COMPLETE VITAL SIGNS:")
    assessment_with_vitals = assess_clinical_risk(entities, vitals)
    print(f"   Red flags found: {len(assessment_with_vitals['red_flags_present'])}")
    print(f"   Data gaps: {len(assessment_with_vitals['critical_missing_data_points'])}")
    
    print("\n💡 INSIGHT: Complete vital signs help risk stratification")
    print("   but don't replace clinical assessment")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("CLINICAL RISK ASSESSMENT ENGINE - COMPLETE DEMO")
    print("="*70)
    
    demo_ami_scenario()
    demo_stroke_scenario()
    demo_sepsis_scenario()
    demo_mild_scenario()
    demo_data_completeness()
    
    print("\n" + "="*70)
    print("END OF DEMONSTRATIONS")
    print("="*70)
