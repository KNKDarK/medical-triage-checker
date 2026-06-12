version: "1.0"

system:
  name: "Medical Conversational AI"
  description: "Handles patient complaints, extracts clinical concepts, and manages dynamic dialogue."

llm_engineering:
  model: "gpt-4-medical"
  techniques:
    - name: "Few-Shot Prompting"
      enabled: true
      examples:
        - "Patient: I feel dizzy\nAI: Possible causes include vertigo, dehydration..."
    - name: "Chain-of-Thought Reasoning"
      enabled: true
      strategy: "Step-by-step logical reasoning before final response"

medical_nlp:
  entity_recognition:
    framework: "spaCy + scispaCy"
    mappings:
      - phrase: "my chest feels heavy"
        clinical_concept: "Angina / Chest Pressure"
      - phrase: "I can't catch my breath"
        clinical_concept: "Dyspnea / Shortness of Breath"
  normalization:
    standard: "SNOMED-CT"
    fallback: "UMLS"

conversation_state:
  dialogue_manager:
    type: "dynamic_tree"
    risk_calculation: "real-time"
    loop_prevention: true
    escalation_rules:
      - condition: "high_risk_symptom"
        action: "escalate_to_human"
      - condition: "low_confidence_response"
        action: "ask_clarifying_question"

logging:
  enabled: true
  format: "json"
  fields: ["timestamp", "user_input", "extracted_entities", "risk_score", "ai_response"]

deployment:
  runtime: "OpenCode"
  environment: "production"
  scaling:
    max_instances: 10
    auto_restart: true

