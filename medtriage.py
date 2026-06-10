import streamlit as st
from datetime import datetime

st.set_page_config(page_title="MedTriage Pro+", page_icon="🏥", layout="centered")

if "report_generated" not in st.session_state:
    st.session_state.report_generated = False

# ---------- HEADER ----------
col_title, col_reset = st.columns([5, 1])
with col_title:
    st.title("🏥 Enhanced Symptom Checker & Triage")
    st.caption("⚕️ Informational triage guidance only — does **not** replace professional medical advice.")
with col_reset:
    if st.button("🔄 Clear All", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.session_state.report_generated = False
        st.rerun()

# ---------- SIDEBAR: PATIENT PROFILE ----------
with st.sidebar:
    st.header("👤 Patient Profile")
    age = st.number_input("Age (years)", 0, 120, 30, help="Patient's age")
    gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])

    st.subheader("🩺 Vitals")
    c1, c2 = st.columns(2)
    with c1:
        temp = st.number_input("Temp (°F)", 90.0, 110.0, 98.6, 0.1)
        hr = st.number_input("Heart Rate (bpm)", 20, 250, 75, 1)
    with c2:
        spo2 = st.number_input("SpO₂ (%)", 50, 100, 98, 1)
        sbp = st.number_input("Systolic BP (mmHg)", 60, 260, 120, 1)

    st.subheader("📋 History")
    preexisting = st.multiselect("Pre-existing Conditions", [
        "Diabetes", "Hypertension", "Asthma", "Heart Disease", "COPD",
        "Immunocompromised", "Pregnancy", "None"
    ], default=["None"])
    meds = st.text_input("Current Medications", placeholder="e.g. metformin, lisinopril")
    allergies = st.text_input("Allergies", placeholder="e.g. penicillin, latex")

# ---------- TABS ----------
tab_sym, tab_pain, tab_report = st.tabs(["🤒 Symptoms", "📍 Pain", "📄 Report"])

# ---------- TAB 1: SYMPTOMS ----------
with tab_sym:
    st.subheader("Select all that apply")
    c_left, c_right = st.columns(2)

    with c_left:
        emergency = st.multiselect("🚨 **Severe / Emergency**", [
            "Chest pain or pressure", "Severe shortness of breath", "Sudden weakness/numbness (one side)",
            "Difficulty speaking", "Loss of consciousness", "Severe bleeding",
            "Head injury with confusion", "Severe allergic reaction", "Suicidal thoughts"
        ])
        respiratory = st.multiselect("🫁 **Respiratory**", [
            "Cough (dry)", "Cough (productive)", "Sore throat", "Runny nose",
            "Congestion", "Mild shortness of breath", "Wheezing", "Sneezing"
        ])
        digestive = st.multiselect("🍽️ **Digestive**", [
            "Nausea", "Vomiting", "Diarrhea", "Constipation", "Mild stomach ache",
            "Severe abdominal pain", "Heartburn", "Loss of appetite"
        ])

    with c_right:
        general = st.multiselect("🌡️ **General / Systemic**", [
            "Fever (feeling hot)", "Chills", "Fatigue", "Body aches",
            "Night sweats", "Dizziness", "Fainting", "Unexplained weight loss"
        ])
        neuro = st.multiselect("🧠 **Neurological**", [
            "Headache (mild)", "Headache (severe)", "Blurred vision",
            "Numbness/tingling", "Tremors", "Confusion", "Seizure"
        ])
        skin = st.multiselect("🧴 **Skin / Wounds**", [
            "Rash", "Itching", "Swelling", "Bruising", "Cut / wound",
            "Burn", "Signs of infection (redness, warmth)", "Skin discoloration"
        ])

    duration = st.slider("📅 Days with these symptoms", 1, 30, 1)

# ---------- TAB 2: PAIN ----------
with tab_pain:
    st.subheader("Pain Assessment")
    pain_level = st.select_slider("Worst pain level (0 = none, 10 = worst imaginable)",
                                   options=list(range(0, 11)), value=2)
    if pain_level > 0:
        severity = "🟢 Mild" if pain_level <= 3 else "🟡 Moderate" if pain_level <= 6 else "🔴 Severe"
        st.markdown(f"**Severity:** {severity}")

    pain_loc = st.multiselect("Pain location(s)", [
        "Head", "Neck", "Chest", "Upper Back", "Lower Back", "Abdomen",
        "Pelvis", "Shoulder", "Arm / Hand", "Leg / Foot", "Joints"
    ])
    pain_nature = st.selectbox("Nature of pain", [
        "Aching", "Sharp / Stabbing", "Burning", "Throbbing", "Cramping", "Dull", "Radiating"
    ])

# ---------- TAB 3: REPORT ----------
with tab_report:
    all_symptoms = emergency + general + respiratory + digestive + neuro + skin
    has_any_symptom = bool(all_symptoms or pain_level > 0 or pain_loc)

    if not has_any_symptom:
        st.info("👈 Select symptoms or rate your pain to generate a report.")
    else:
        # ---- BUILD FLAGS ----
        red_flags, yellow_flags = [], []

        # Vital-sign red flags
        if temp >= 103:    red_flags.append(f"Very high fever ({temp}°F)")
        elif temp >= 100.4: yellow_flags.append(f"Elevated temperature ({temp}°F)")
        if hr > 120 or hr < 50: red_flags.append(f"Critical heart rate ({hr} bpm)")
        elif hr > 100 or hr < 60: yellow_flags.append(f"Abnormal heart rate ({hr} bpm)")
        if spo2 < 90: red_flags.append(f"Critical oxygen level ({spo2}%)")
        elif spo2 < 95: yellow_flags.append(f"Low oxygen saturation ({spo2}%)")
        if sbp > 180 or sbp < 80: red_flags.append(f"Critical blood pressure ({sbp} mmHg)")
        elif sbp > 140 or sbp < 90: yellow_flags.append(f"Elevated blood pressure ({sbp} mmHg)")

        # Pain flags
        if pain_level >= 8: red_flags.append(f"Severe pain ({pain_level}/10)")
        elif pain_level >= 5: yellow_flags.append(f"Significant pain ({pain_level}/10)")

        # Symptom flags
        if "Fever (feeling hot)" in general and temp >= 102:
            yellow_flags.append("Fever with elevated temperature")
        if duration >= 7: yellow_flags.append(f"Symptoms persisting {duration} days")
        if "None" not in preexisting:
            conds = [c for c in preexisting if c != "None"]
            yellow_flags.append(f"Pre-existing: {', '.join(conds)}")
        if "Pregnancy" in preexisting and any(s in emergency for s in ["Chest pain or pressure", "Severe shortness of breath", "Severe bleeding"]):
            red_flags.append("Pregnancy with critical symptoms")

        # ---- TRIAGE DECISION ----
        crit_symptoms = {"Chest pain or pressure", "Severe shortness of breath",
                         "Sudden weakness/numbness (one side)", "Difficulty speaking",
                         "Loss of consciousness", "Severe bleeding",
                         "Head injury with confusion", "Severe allergic reaction",
                         "Suicidal thoughts", "Severe abdominal pain", "Seizure"}
        is_emergency = bool(set(emergency) & crit_symptoms) or bool(red_flags) or pain_level >= 9
        is_emergency = is_emergency or {"Vomiting", "Diarrhea"}.issubset(set(digestive))
        is_emergency = is_emergency or ("Fainting" in general and age >= 60)

        needs_doctor = (temp >= 102) or len(yellow_flags) >= 2 or duration >= 7
        needs_doctor = needs_doctor or pain_level >= 5 or spo2 < 95
        needs_doctor = needs_doctor or "Headache (severe)" in neuro
        needs_doctor = needs_doctor or ("Fever (feeling hot)" in general and "None" not in preexisting)
        needs_doctor = needs_doctor or ("Signs of infection (redness, warmth)" in skin)
        needs_doctor = needs_doctor or ("Chest" in pain_loc and pain_level >= 4)

        # ---- DISPLAY ----
        if is_emergency:
            st.error("🔴 **URGENT — EMERGENCY CARE REQUIRED**")
            st.markdown("---")
            st.markdown("### 🚨 Immediate Actions")
            st.markdown("- Call **911** (or local emergency services) **now**")
            st.markdown("- Do **not** wait for symptoms to improve")
            st.markdown("- Have someone drive you — do **not** drive yourself if possible")
            for f in red_flags:
                st.markdown(f"- ⚠️ **{f}**")
            for s in emergency:
                if s in crit_symptoms:
                    st.markdown(f"- 🚩 {s}")
        elif needs_doctor:
            st.warning("🟡 **SCHEDULE A DOCTOR VISIT**")
            st.markdown("---")
            st.markdown("### 📅 Recommended Next Steps")
            st.markdown("- Contact your **primary care physician** or visit an **Urgent Care** today")
            st.markdown("- Monitor closely — seek emergency care if symptoms worsen")
            for f in yellow_flags:
                st.markdown(f"- ⚡ {f}")
            if "None" not in preexisting:
                conds = [c for c in preexisting if c != "None"]
                st.markdown(f"- 🩺 This may be impacted by: {', '.join(conds)}")
        else:
            st.success("🟢 **HOME CARE & MONITORING**")
            st.markdown("---")
            st.markdown("### 🏡 Self-Care")
            st.markdown("- **Rest**, hydrate, and monitor symptoms")
            st.markdown("- OTC medication as appropriate for fever / pain")
            st.markdown("- Consult a doctor if symptoms persist **> 7 days** or worsen")

        # ---- PRINTABLE SUMMARY ----
        st.divider()
        st.subheader("📋 Summary for Your Provider")

        triage_label = "🔴 Emergency" if is_emergency else "🟡 Needs Doctor" if needs_doctor else "🟢 Home Care"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        symptom_str = ", ".join(all_symptoms) if all_symptoms else "None reported"
        pain_loc_str = ", ".join(pain_loc) if pain_loc else "Not specified"
        pre_str = ", ".join(c for c in preexisting if c != "None") if "None" not in preexisting else "None reported"
        med_str = meds if meds.strip() else "None reported"
        allergy_str = allergies if allergies.strip() else "None reported"

        summary = f"""
╔══════════════════════════════════════════════╗
║          MEDICAL TRIAGE SUMMARY              ║
║     Generated: {now_str}          ║
╚══════════════════════════════════════════════╝

PATIENT
  Age: {age} yr  |  Gender: {gender}
  Triage: {triage_label}
  Duration: {duration} day(s)

VITALS
  Temp: {temp}°F  |  HR: {hr} bpm  |  SpO₂: {spo2}%  |  BP: {sbp} mmHg

SYMPTOMS
  {symptom_str}

PAIN
  Level: {pain_level}/10  |  Location: {pain_loc_str}  |  Nature: {pain_nature}

HISTORY
  Conditions: {pre_str}
  Medications: {med_str}
  Allergies: {allergy_str}

RECOMMENDATION
  {triage_label}"""
        if is_emergency:
            summary += "\n  Seek immediate emergency care — call 911 or go to ER."
        elif needs_doctor:
            summary += "\n  See a doctor or visit urgent care within 24 hours."
        else:
            summary += "\n  Home care with monitoring."

        summary += "\n\n" + "═" * 50
        summary += "\nDisclaimer: Informational assessment only. Not a substitute\n"
        summary += "for professional medical advice. Consult a qualified\n"
        summary += "healthcare provider for any health concerns."
        summary += "\n" + "═" * 50

        st.code(summary, language="")

        st.download_button(
            "📥 Download Summary (.txt)",
            data=summary,
            file_name=f"triage_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ---------- FOOTER DISCLAIMER ----------
st.divider()
st.caption(
    "⚠️ **Medical Disclaimer:** This tool provides **informational triage guidance only** and "
    "does **not** diagnose, treat, or replace professional medical advice. "
    "If you are experiencing a medical emergency, call emergency services immediately."
)
