version: "1.1"

system:
  name: "Clinical Symptom Checker AI"
  description: "Safe, validated conversational AI for patient complaints."

llm_engineering:
  model: "gpt-4-medical"
  techniques:
    - name: "Few-Shot Prompting"
      enabled: true
    - name: "Chain-of-Thought Reasoning"
      enabled: true
    - name: "Retrieval-Augmented Generation (RAG)"
      enabled: true
      sources:
        - "SNOMED-CT"
        - "ICD-11"
        - "NICE Clinical Guidelines"
      fallback: "UMLS"

medical_nlp:
  entity_recognition:
    framework: "scispaCy + MedCAT"
    normalization: "SNOMED-CT"
    error_handling: "flag_low_confidence_entities"

clinical_modeling:
  probabilistic_reasoning:
    type: "Bayesian Network"
    inputs: ["age", "sex", "symptoms", "risk_factors"]
    outputs: "condition_probability_distribution"
    threshold:
      high_risk: 0.75
      medium_risk: 0.40
      low_risk: 0.20

conversation_state:
  dialogue_manager:
    type: "dynamic_tree"
    risk_calculation: "probabilistic + rule-based"
    escalation_rules:
      - condition: "probability > 0.75"
        action: "escalate_to_human"
      - condition: "uncertain_diagnosis"
        action: "ask_clarifying_question"
    loop_prevention: true

validation:
  clinical_red_teaming:
    participants:
      - "Medical Doctors (MD/DO)"
      - "Clinical QA Engineers"
    test_cases: "5000+ vignettes"
    focus: ["under-triage errors", "hallucination detection", "edge-case stress tests"]

logging:
  enabled: true
  format: "json"
  fields: ["timestamp", "user_input", "entities", "probabilities", "risk_score", "ai_response", "escalation_flag"]

deployment:
  runtime: "OpenCode"
  environment: "production"
  scaling:
    max_instances: 20
    auto_restart: true

