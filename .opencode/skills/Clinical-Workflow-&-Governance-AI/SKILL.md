version: "1.3"

system:
  name: "Clinical Workflow & Governance AI"
  description: "Securely integrates triage data into hospital EHR systems with compliance guardrails."

ehr_integration:
  standards:
    - name: "HL7 v2"
      enabled: true
      description: "Legacy hospital interoperability standard."
    - name: "FHIR R4"
      enabled: true
      description: "Fast Healthcare Interoperability Resources for modern EHRs."
  target_systems:
    - "Epic"
    - "Cerner"
    - "Allscripts"
  transport:
    protocol: "REST + JSON"
    security: "TLS 1.3"

clinical_coding:
  automation:
    ontologies:
      - "ICD-10"
      - "ICD-11"
      - "RxNorm"
    mapping_rules:
      - symptom: "chest pain"
        code: "R07.9"
      - symptom: "shortness of breath"
        code: "R06.02"
    billing_integration: true

workflow_integration:
  webhooks:
    enabled: true
    endpoints:
      - "hospital_portal"
      - "Zocdoc"
      - "Amwell"
    retry_policy: "exponential_backoff"
  scheduling_api:
    enabled: true
    supported_systems:
      - "Epic Scheduling"
      - "Zocdoc"
      - "Amwell"

privacy_governance:
  compliance:
    frameworks:
      - "HIPAA (US)"
      - "GDPR (EU)"
      - "Local Privacy Laws"
    audit_logging: true
  pii_phi_protection:
    detectors:
      - "names"
      - "birthdates"
      - "social_security_numbers"
    masking_pipeline: "real-time scrubbing before cloud transmission"
    fallback: "local-only processing if scrubbing fails"

mlops_monitoring:
  drift_detection:
    enabled: true
    methods:
      - "Population Stability Index (PSI)"
      - "Kolmogorov-Smirnov Test"
    alert_threshold: 0.15
  model_monitoring:
    metrics:
      - "accuracy"
      - "precision"
      - "recall"
      - "false_negative_rate"
    dashboard: "Grafana + Prometheus"

logging:
  enabled: true
  format: "json"
  fields: ["timestamp", "user_input", "entities", "ehr_payload", "compliance_flags", "ai_response"]

deployment:
  runtime: "OpenCode"
  environment: "production"
  scaling:
    max_instances: 25
    auto_restart: true

