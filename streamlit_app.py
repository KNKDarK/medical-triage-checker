import streamlit as st
from datetime import datetime
import re
import urllib.parse
import json
from medtriage import get_db, signup_user, login_user, validate_email
from medical_entity_extractor import extract_medical_entities
from clinical_risk_assessment import assess_clinical_risk
from clinical_triage_router import route_patient

GUEST_LIMIT = 2

st.set_page_config(page_title="MedTriage Pro+", page_icon="🏥", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Color+Emoji&amp;display=swap');
html, body, .stApp, .stApp * {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.emoji {
    font-family: 'Noto Color Emoji', 'Apple Color Emoji', 'Segoe UI Emoji', sans-serif;
}

@keyframes pulse { 0%,100% { transform:scale(1); } 50% { transform:scale(1.03); } }
@keyframes pulseGlow { 0%,100% { box-shadow:0 0 0 0 rgba(211,47,47,0.4); } 50% { box-shadow:0 0 0 12px rgba(211,47,47,0); } }
@keyframes slideInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
@keyframes shimmer { 0% { background-position:-200px 0; } 100% { background-position:200px 0; } }
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
@keyframes gradientShift { 0% { background-position:0% 50%; } 50% { background-position:100% 50%; } 100% { background-position:0% 50%; } }
@keyframes bounceIn { 0% { opacity:0; transform:scale(0.3); } 50% { transform:scale(1.05); } 70% { transform:scale(0.9); } 100% { opacity:1; transform:scale(1); } }

[data-testid="stMetricValue"] { animation: slideInUp 0.4s ease-out; }
.stAlert { animation: slideInUp 0.5s ease-out; }
.st-emotion-cache-1v0mbdj { animation: fadeIn 0.3s ease-in; }

.pulse-emergency { animation: pulse 1.5s ease-in-out infinite; }
.pulse-glow { animation: pulseGlow 2s ease-in-out infinite; }
.slide-in { animation: slideInUp 0.5s ease-out; }
.bounce-in { animation: bounceIn 0.6s ease-out; }
.shimmer { background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); background-size: 200px 100%; animation: shimmer 1.5s infinite; }

.animate-gradient {
    background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
    background-size: 400% 400%;
    animation: gradientShift 3s ease infinite;
    color: white; border-radius: 8px; padding: 1rem; text-align: center;
}

.emoji { font-family: 'Noto Color Emoji', 'Apple Color Emoji', 'Segoe UI Emoji', sans-serif; }
.circle-red { display:inline-block; width:12px; height:12px; border-radius:50%; background:#d32f2f; margin-right:4px; }
.circle-yellow { display:inline-block; width:12px; height:12px; border-radius:50%; background:#fbc02d; margin-right:4px; }
.circle-green { display:inline-block; width:12px; height:12px; border-radius:50%; background:#388e3c; margin-right:4px; }
.badge-emergency { background:#d32f2f; color:#fff; padding:2px 10px; border-radius:4px; font-weight:700; font-size:0.85rem; }
.badge-doctor { background:#fbc02d; color:#333; padding:2px 10px; border-radius:4px; font-weight:700; font-size:0.85rem; }
.badge-home { background:#388e3c; color:#fff; padding:2px 10px; border-radius:4px; font-weight:700; font-size:0.85rem; }
.action-card { padding:1rem; border-radius:8px; margin:0.5rem 0; border:1px solid #e0e0e0; background:#fafafa; transition: transform 0.2s, box-shadow 0.2s; }
.action-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.clinic-item { padding:0.75rem; border-radius:8px; margin:0.5rem 0; border-left:4px solid; background:#ffffff; }
.locked-section { padding:2rem; border-radius:12px; margin:1rem 0; background:#f3f0ff; border:2px dashed #7c4dff; text-align:center; animation: bounceIn 0.6s ease-out; }
.emergency-alert { animation: pulse 1.5s ease-in-out infinite; border-radius:8px; }
.severity-bar { height:12px; border-radius:6px; transition: width 0.8s ease-in-out; }
.tip-card { padding:0.75rem; border-radius:8px; margin:0.25rem 0; border-left:3px solid; animation: slideInUp 0.4s ease-out; }
.body-part { display:inline-block; padding:2px 6px; margin:2px; border-radius:4px; font-size:0.85rem; }
.body-part.active { background:#ffcdd2; color:#c62828; font-weight:600; }
.body-part.inactive { background:#f5f5f5; color:#9e9e9e; }
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"
if "is_guest" not in st.session_state:
    st.session_state.is_guest = False
if "guest_uses" not in st.session_state:
    st.session_state.guest_uses = 0
if "reports" not in st.session_state:
    st.session_state.reports = []

if not st.session_state.authenticated and not st.session_state.is_guest:

    st.title("🏥 MedTriage Pro+")
    st.markdown("**Medical Symptom Checker & Triage Assistant**")
    st.caption("Sign in for full access or continue as a guest.")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔑 Sign In", use_container_width=True):
            st.session_state.auth_page = "login"
    with col2:
        if st.button("📝 Sign Up", use_container_width=True):
            st.session_state.auth_page = "signup"
    with col3:
        if st.button("👤 Guest Access", use_container_width=True, type="secondary"):
            st.session_state.is_guest = True
            st.session_state.guest_uses = 0
            st.rerun()

    st.divider()

    if st.session_state.auth_page == "login":
        st.subheader("🔑 Sign In")
        with st.form("login_form"):
            l_user = st.text_input("Username")
            l_pass = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In", type="primary", use_container_width=True):
                if not l_user.strip():
                    st.error("Please enter your username.")
                elif not l_pass:
                    st.error("Please enter your password.")
                else:
                    ok, email = login_user(l_user, l_pass)
                    if ok:
                        st.session_state.authenticated = True
                        st.session_state.username = l_user.strip()
                        st.session_state.user_email = email
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

    else:
        st.subheader("📝 Sign Up")
        with st.form("signup_form"):
            s_user = st.text_input("Username", help="3–20 characters, letters and numbers only")
            s_email = st.text_input("Email")
            s_pass = st.text_input("Password", type="password", help="At least 6 characters")
            s_confirm = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Create Account", type="primary", use_container_width=True):
                errors = []
                if not s_user.strip():
                    errors.append("Username is required.")
                elif len(s_user.strip()) < 3:
                    errors.append("Username must be at least 3 characters.")
                elif not re.match(r"^[a-zA-Z0-9_]+$", s_user.strip()):
                    errors.append("Username can only contain letters, numbers, and underscores.")
                if not s_email.strip():
                    errors.append("Email is required.")
                elif not validate_email(s_email.strip()):
                    errors.append("Invalid email format.")
                if not s_pass:
                    errors.append("Password is required.")
                elif len(s_pass) < 6:
                    errors.append("Password must be at least 6 characters.")
                if s_pass != s_confirm:
                    errors.append("Passwords do not match.")
                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    ok, msg = signup_user(s_user, s_email, s_pass)
                    if ok:
                        st.success(msg)
                        st.session_state.auth_page = "login"
                        st.rerun()
                    else:
                        st.error(msg)

    st.caption("---")
    st.caption("👤 **Guest:** Try the triage checker with limited uses. Sign up to save reports and unlock unlimited access.")
    st.caption("⚠️ **Disclaimer:** This tool provides informational triage guidance only. It does not diagnose or replace professional medical advice.")
    st.stop()


def clear_session():
    for k in ["authenticated", "username", "user_email", "auth_page", "is_guest", "guest_uses", "reports"]:
        if k in st.session_state:
            del st.session_state[k]


remaining = max(0, GUEST_LIMIT - st.session_state.guest_uses) if st.session_state.is_guest else None

col_title, col_user, col_reset = st.columns([4, 2, 1])
with col_title:
    st.title("🏥 Enhanced Symptom Checker & Triage")
    st.caption("⚕️ Informational triage guidance only — does **not** replace professional medical advice.")
with col_user:
    if st.session_state.is_guest:
        st.markdown(f"👤 **Guest**  \n{remaining}/{GUEST_LIMIT} free uses left")
    else:
        st.markdown(f"👤 **{st.session_state.username}**  \n{st.session_state.user_email}")
with col_reset:
    label = "🚪 Logout" if not st.session_state.is_guest else "🚪 Exit Guest"
    if st.button(label, use_container_width=True):
        clear_session()
        st.rerun()

if st.session_state.is_guest:
    st.markdown(
        f"<div class='animate-gradient'><strong>🔒 Guest Mode</strong> — "
        f"{remaining}/{GUEST_LIMIT} free triage checks remaining. "
        f"<a href='#' onclick='alert(\"Sign up to unlock unlimited access, download reports, and more!\")' "
        f"style='color:#fff;text-decoration:underline;font-weight:700;'>Sign up →</a></div>",
        unsafe_allow_html=True,
    )

with st.sidebar:
    st.header("👤 Patient Profile")
    age = st.number_input("Age (years)", 0, 120, 30)
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

    st.divider()
    st.subheader("📍 Your Location")
    location = st.text_input("City / ZIP code", placeholder="e.g. New York, NY or 10001")
    if st.button("📍 Detect My Location", use_container_width=True):
        st.info("Allow browser location access when prompted, then refresh.")
        st.markdown("""
            <script>
            navigator.geolocation.getCurrentPosition(function(pos) {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                const input = window.parent.document.querySelector('input[aria-label="City / ZIP code"]');
                if (input) input.value = lat + ',' + lon;
            });
            </script>
        """, unsafe_allow_html=True)

    if st.session_state.is_guest:
        st.divider()
        st.markdown("""
        <div class='animate-gradient'>
        <strong>🚀 Upgrade for:</strong><br>
        ✓ Unlimited triage checks<br>
        ✓ Download summaries<br>
        ✓ All clinic locations<br>
        ✓ Save report history
        </div>
        """, unsafe_allow_html=True)

tab_sym, tab_pain, tab_report, tab_extract, tab_risk, tab_triage, tab_nearby = st.tabs(["🤒 Symptoms", "📍 Pain", "📄 Report", "🔍 Extract", "⚠️ Risk", "🏥 Triage", "📍 Nearby Clinics"])

with tab_sym:
    st.subheader("Select all that apply")
    c_left, c_right = st.columns(2)

    with c_left:
        emergency_sym = st.multiselect("🚨 **Severe / Emergency**", [
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

with tab_pain:
    st.subheader("Pain Assessment")
    pain_level = st.select_slider("Worst pain level (0 = none, 10 = worst imaginable)",
                                   options=list(range(0, 11)), value=0)
    if pain_level > 0:
        severity = "<span class='circle-green'></span> Mild" if pain_level <= 3 else "<span class='circle-yellow'></span> Moderate" if pain_level <= 6 else "<span class='circle-red'></span> Severe"
        st.markdown(f"**Severity:** {severity}", unsafe_allow_html=True)

    pain_loc = st.multiselect("Pain location(s)", [
        "Head", "Neck", "Chest", "Upper Back", "Lower Back", "Abdomen",
        "Pelvis", "Shoulder", "Arm / Hand", "Leg / Foot", "Joints"
    ])
    pain_nature = st.selectbox("Nature of pain", [
        "Aching", "Sharp / Stabbing", "Burning", "Throbbing", "Cramping", "Dull", "Radiating"
    ])

all_symptoms = emergency_sym + general + respiratory + digestive + neuro + skin
has_any_symptom = bool(all_symptoms or pain_level > 0 or pain_loc)

red_flags, yellow_flags = [], []
is_emergency = False
needs_doctor = False
triage_label = "NONE"
severity_score = 0

if has_any_symptom:
    if temp >= 103:    red_flags.append(f"Very high fever ({temp}°F)")
    elif temp >= 100.4: yellow_flags.append(f"Elevated temperature ({temp}°F)")
    if hr > 120 or hr < 50: red_flags.append(f"Critical heart rate ({hr} bpm)")
    elif hr > 100 or hr < 60: yellow_flags.append(f"Abnormal heart rate ({hr} bpm)")
    if spo2 < 90: red_flags.append(f"Critical oxygen level ({spo2}%)")
    elif spo2 < 95: yellow_flags.append(f"Low oxygen saturation ({spo2}%)")
    if sbp > 180 or sbp < 80: red_flags.append(f"Critical blood pressure ({sbp} mmHg)")
    elif sbp > 140 or sbp < 90: yellow_flags.append(f"Elevated blood pressure ({sbp} mmHg)")

    if pain_level >= 8: red_flags.append(f"Severe pain ({pain_level}/10)")
    elif pain_level >= 5: yellow_flags.append(f"Significant pain ({pain_level}/10)")

    if "Fever (feeling hot)" in general and temp >= 102:
        yellow_flags.append("Fever with elevated temperature")
    if duration >= 7: yellow_flags.append(f"Symptoms persisting {duration} days")
    if "None" not in preexisting:
        conds = [c for c in preexisting if c != "None"]
        yellow_flags.append(f"Pre-existing: {', '.join(conds)}")
    if "Pregnancy" in preexisting and any(s in emergency_sym for s in ["Chest pain or pressure", "Severe shortness of breath", "Severe bleeding"]):
        red_flags.append("Pregnancy with critical symptoms")

    crit_symptoms = {"Chest pain or pressure", "Severe shortness of breath",
                     "Sudden weakness/numbness (one side)", "Difficulty speaking",
                     "Loss of consciousness", "Severe bleeding",
                     "Head injury with confusion", "Severe allergic reaction",
                     "Suicidal thoughts", "Severe abdominal pain", "Seizure"}
    is_emergency = bool(set(emergency_sym) & crit_symptoms) or bool(red_flags) or pain_level >= 9
    is_emergency = is_emergency or ("Fainting" in general and age >= 60)

    needs_doctor = (temp >= 102) or len(yellow_flags) >= 3 or duration >= 7
    needs_doctor = needs_doctor or pain_level >= 5
    needs_doctor = needs_doctor or "Headache (severe)" in neuro
    needs_doctor = needs_doctor or ("Signs of infection (redness, warmth)" in skin)
    needs_doctor = needs_doctor or ("Chest" in pain_loc and pain_level >= 4)
    needs_doctor = needs_doctor or {"Vomiting", "Diarrhea"}.issubset(set(digestive))

    triage_label = "EMERGENCY" if is_emergency else "NEEDS DOCTOR" if needs_doctor else "HOME CARE"

    score = 0
    score += min(temp - 97, 15) if temp > 99 else 0
    score += min((160 - sbp) / 3, 10) if sbp > 140 or sbp < 90 else 0
    score += min((hr - 70) / 3, 10) if hr > 100 or hr < 60 else 0
    score += min((100 - spo2) * 2, 10) if spo2 < 95 else 0
    score += pain_level * 3
    score += len(red_flags) * 8
    score += len(yellow_flags) * 4
    score += len(emergency_sym) * 5
    score += min(duration, 14)
    severity_score = min(int(score), 100)

HEALTH_TIPS = {
    "EMERGENCY": [
        "🆘 Call 911 or your local emergency number immediately.",
        "🚑 Do NOT drive yourself — ask someone or call an ambulance.",
        "🧑‍⚕️ If possible, unlock your front door for responders.",
        "📋 Have your medication list and ID ready for the hospital.",
        "🧊 If bleeding, apply firm pressure with a clean cloth.",
    ],
    "NEEDS DOCTOR": [
        "📞 Call your doctor's office first — they may have same-day openings.",
        "🏥 Urgent care centers are usually faster than ER for non-life-threatening issues.",
        "💧 Stay hydrated and rest while waiting for your appointment.",
        "📝 Write down your symptoms and questions before the visit.",
        "💊 Keep taking prescribed medications unless told otherwise.",
    ],
    "HOME CARE": [
        "😴 Rest is the best medicine — give your body time to recover.",
        "💧 Drink plenty of water and avoid caffeine/alcohol.",
        "🌡️ Monitor your temperature twice daily.",
        "🍵 Soup, herbal tea, and light foods are easier on digestion.",
        "📅 If symptoms persist beyond 7 days, see a doctor.",
    ],
}

BODY_MAP = [
    ("🧠", "Head"), ("🦴", "Neck"), ("❤️", "Chest"),
    ("🔙", "Upper Back"), ("⬇️", "Lower Back"),
    ("🍽️", "Abdomen"), ("🦴", "Pelvis"),
    ("💪", "Shoulder"), ("🤚", "Arm / Hand"),
    ("🦵", "Leg / Foot"), ("🦴", "Joints"),
]

with tab_report:
    if not has_any_symptom:
        st.info("👈 Select symptoms or rate your pain to generate a report.")
    elif st.session_state.is_guest and st.session_state.guest_uses >= GUEST_LIMIT:
        st.markdown(f"""
        <div class='locked-section'>
            <h2>🔒 Trial Limit Reached</h2>
            <p style='font-size:1.1rem;'>You've used all {GUEST_LIMIT} free triage checks.</p>
            <p>Sign up for <strong>unlimited</strong> access:</p>
            <ul style='display:inline-block;text-align:left;'>
                <li>✓ Unlimited triage assessments</li>
                <li>✓ Download full summary reports</li>
                <li>✓ Nearby clinic finder</li>
                <li>✓ Save your history</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📝 Sign Up Now — It's Free", type="primary", use_container_width=True):
            clear_session()
            st.rerun()
    else:
        if st.session_state.is_guest and has_any_symptom:
            if not st.session_state.get("_report_counted", False):
                st.session_state.guest_uses += 1
                st.session_state._report_counted = True

        if not has_any_symptom:
            st.session_state._report_counted = False

        triage_color = "#d32f2f" if is_emergency else "#fbc02d" if needs_doctor else "#388e3c"

        st.subheader("📋 Triage Assessment")
        col_alert, col_score = st.columns([2, 1])
        with col_alert:
            if is_emergency:
                st.error("### 🚨 URGENT — EMERGENCY CARE REQUIRED")
                st.markdown("Call **911** immediately. Do not wait.", unsafe_allow_html=True)
            elif needs_doctor:
                st.warning("### 📅 SCHEDULE A DOCTOR VISIT")
                st.markdown("Contact your PCP or visit Urgent Care today.", unsafe_allow_html=True)
            else:
                st.success("### 🏡 HOME CARE & MONITORING")
                st.markdown("Rest, hydrate, and monitor symptoms.", unsafe_allow_html=True)
        with col_score:
            st.metric("Triage Level", triage_label, delta_color="off")
            st.metric("Pain Level", f"{pain_level}/10" if pain_level > 0 else "None")
            st.metric("Duration", f"{duration} day(s)")

        bar_color = "#d32f2f" if severity_score >= 60 else "#fbc02d" if severity_score >= 30 else "#388e3c"
        st.markdown(f"""
        <div class='slide-in' style='margin:0.5rem 0;'>
            <strong>📊 Severity Score: {severity_score}/100</strong>
            <div style='background:#e0e0e0;border-radius:8px;height:14px;overflow:hidden;margin-top:4px;'>
                <div class='severity-bar' style='width:{severity_score}%;background:{bar_color};height:100%;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🚩 Red Flags & Warnings", expanded=bool(red_flags or yellow_flags)):
            col_r, col_y = st.columns(2)
            with col_r:
                if red_flags:
                    for f in red_flags:
                        st.markdown(f"- <span class='circle-red'></span> **{f}**", unsafe_allow_html=True)
                else:
                    st.caption("No red flags detected.")
            with col_y:
                if yellow_flags:
                    for f in yellow_flags:
                        st.markdown(f"- <span class='circle-yellow'></span> {f}", unsafe_allow_html=True)
                else:
                    st.caption("No yellow flags detected.")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🩺 Vitals Overview")
            vc1, vc2, vc3, vc4 = st.columns(4)
            vc1.metric("Temp", f"{temp}°F")
            vc2.metric("HR", f"{hr} bpm")
            vc3.metric("SpO₂", f"{spo2}%")
            vc4.metric("BP", f"{sbp} mmHg")

            with st.expander("🧾 Symptoms Detail"):
                cats = [
                    ("🚨 Emergency", emergency_sym), ("🫁 Respiratory", respiratory),
                    ("🍽️ Digestive", digestive), ("🌡️ General", general),
                    ("🧠 Neurological", neuro), ("🧴 Skin", skin),
                ]
                for label, items in cats:
                    if items:
                        st.markdown(f"**{label}:** {', '.join(items)}")

        with col2:
            st.subheader("📋 Patient History")
            pre_str = ", ".join(c for c in preexisting if c != "None") if "None" not in preexisting else "None"
            st.markdown(f"**Conditions:** {pre_str}")
            st.markdown(f"**Medications:** {meds if meds.strip() else 'None'}")
            st.markdown(f"**Allergies:** {allergies if allergies.strip() else 'None'}")

            if pain_level > 0:
                st.markdown(f"**Pain:** {pain_level}/10 ({pain_nature}) at {', '.join(pain_loc)}")

            if pain_loc:
                st.markdown("**📍 Body Map:**")
                parts_html = "".join(
                    f"<span class='body-part {'active' if label in pain_loc else 'inactive'}'>"
                    f"{emoji} {label}</span>"
                    for emoji, label in BODY_MAP
                )
                st.markdown(f"<div>{parts_html}</div>", unsafe_allow_html=True)

        st.divider()

        col_tips, col_contacts = st.columns(2)
        with col_tips:
            st.subheader("💡 Health Tips")
            tips = HEALTH_TIPS.get(triage_label, HEALTH_TIPS["HOME CARE"])
            for tip in tips:
                color = "#d32f2f" if is_emergency else "#fbc02d" if needs_doctor else "#388e3c"
                st.markdown(
                    f"<div class='tip-card' style='border-left-color:{color};background:" +
                    ("#ffebee" if is_emergency else "#fff8e1" if needs_doctor else "#e8f5e9") +
                    f"'>{tip}</div>",
                    unsafe_allow_html=True,
                )

        with col_contacts:
            st.subheader("📞 Emergency Contacts")
            st.markdown("""
            <div class='action-card' style='text-align:center;'>
                <a href='tel:911' style='display:block;padding:0.5rem;background:#d32f2f;color:white;
                border-radius:8px;text-decoration:none;font-weight:700;font-size:1.2rem;margin-bottom:0.5rem;'>
                📞 911 — Emergency</a>
                <a href='tel:1-800-222-1222' style='display:block;padding:0.5rem;background:#f57c00;
                color:white;border-radius:8px;text-decoration:none;font-weight:700;margin-bottom:0.5rem;'>
                ☠️ Poison Control</a>
                <a href='tel:988' style='display:block;padding:0.5rem;background:#7b1fa2;
                color:white;border-radius:8px;text-decoration:none;font-weight:700;margin-bottom:0.5rem;'>
                🫂 Crisis Helpline (988)</a>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        if st.session_state.is_guest:
            st.info(f"🔒 Guest — {remaining}/{GUEST_LIMIT} checks left. Sign up to download summaries and unlock all features.")
            st.markdown(
                "<div class='locked-section' style='padding:1rem;'>"
                "<strong>🔒 Full summary & download</strong> — available after sign up</div>",
                unsafe_allow_html=True,
            )
        else:
            with st.expander("📄 Full Summary for Your Provider", expanded=False):
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                symptom_str = ", ".join(all_symptoms) if all_symptoms else "None reported"
                pain_loc_str = ", ".join(pain_loc) if pain_loc else "Not specified"
                pre_str_full = ", ".join(c for c in preexisting if c != "None") if "None" not in preexisting else "None reported"
                med_str = meds if meds.strip() else "None reported"
                allergy_str = allergies if allergies.strip() else "None reported"

                summary = f"""
    ╔══════════════════════════════════════════════╗
    ║          MEDICAL TRIAGE SUMMARY              ║
    ║     Generated: {now_str}          ║
    ╚══════════════════════════════════════════════╝

    PATIENT
      Age: {age} yr  |  Gender: {gender}
      Triage: {triage_label}  |  Severity: {severity_score}/100
      Duration: {duration} day(s)

    VITALS
      Temp: {temp}°F  |  HR: {hr} bpm  |  SpO₂: {spo2}%  |  BP: {sbp} mmHg

    SYMPTOMS
      {symptom_str}

    PAIN
      Level: {pain_level}/10  |  Location: {pain_loc_str}  |  Nature: {pain_nature}

    HISTORY
      Conditions: {pre_str_full}
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

            report_entry = {
                "time": now_str, "triage": triage_label, "severity": severity_score,
                "pain": pain_level, "symptoms": len(all_symptoms),
            }
            st.session_state.reports.insert(0, report_entry)
            if len(st.session_state.reports) > 20:
                st.session_state.reports = st.session_state.reports[:20]

            if st.session_state.reports:
                with st.expander("📜 Session History", expanded=False):
                    for i, r in enumerate(st.session_state.reports[:10]):
                        c = "#d32f2f" if r["triage"] == "EMERGENCY" else "#fbc02d" if r["triage"] == "NEEDS DOCTOR" else "#388e3c"
                        st.markdown(
                            f"<div style='padding:0.5rem;margin:0.25rem 0;border-left:3px solid {c};"
                            f"background:#fafafa;border-radius:4px;'>"
                            f"<strong>#{i+1}</strong> {r['time']} — "
                            f"<span style='color:{c};font-weight:700;'>{r['triage']}</span> | "
                            f"Score: {r['severity']}/100 | Pain: {r['pain']}/10 | {r['symptoms']} symptoms"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

        st.divider()

        st.subheader("⚡ Quick Actions")
        qc1, qc2, qc3 = st.columns(3)
        with qc1:
            if is_emergency:
                st.markdown(
                    "<a href='tel:911' target='_blank' class='pulse-glow' style='display:block;text-align:center;"
                    "padding:0.75rem;background:#d32f2f;color:white;border-radius:8px;"
                    "text-decoration:none;font-weight:700;font-size:1.1rem;'>📞 Call 911 Now</a>",
                    unsafe_allow_html=True,
                )
            else:
                st.info("🚑 Emergency\nnot needed")
        with qc2:
            if location:
                query = urllib.parse.quote(
                    "Emergency Room near " + location if is_emergency else
                    "Urgent Care near " + location if needs_doctor else
                    "Pharmacy near " + location
                )
                maps_url = f"https://www.google.com/maps/search/{query}"
                st.markdown(
                    f"<a href='{maps_url}' target='_blank' style='display:block;text-align:center;"
                    f"padding:0.75rem;background:{triage_color};color:white;border-radius:8px;"
                    f"text-decoration:none;font-weight:700;transition:transform 0.2s;'>"
                    f"🗺️ Find Near {location.split(',')[0]}</a>",
                    unsafe_allow_html=True,
                )
            else:
                st.info("📍 Enter location\nin sidebar")
        with qc3:
            if needs_doctor or is_emergency:
                st.markdown(
                    "<div style='text-align:center;padding:0.75rem;background:#fff3e0;"
                    "border-radius:8px;'><strong>🩺 Have someone drive you</strong></div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div style='text-align:center;padding:0.75rem;background:#e8f5e9;"
                    "border-radius:8px;'><strong>💊 OTC if needed</strong></div>",
                    unsafe_allow_html=True,
                )

with tab_extract:
    st.subheader("🔍 Extract Medical Entities from Text")
    st.caption("Analyze raw narrative text and extract structured medical information. Extracts ONLY explicitly stated information—no interpretation or diagnosis.")
    
    st.divider()
    
    narrative_input = st.text_area(
        "Paste patient narrative here:",
        placeholder="Example: I'm a 35-year-old woman with a severe headache for 3 days. Started after a stressful work day. Pain is worse when looking at screens, better with rest. Also have nausea.",
        height=150,
        label_visibility="collapsed"
    )
    
    if st.button("Extract Entities", type="primary", use_container_width=True):
        if not narrative_input.strip():
            st.error("Please enter a narrative to extract entities from.")
        else:
            with st.spinner("Extracting medical entities..."):
                extracted = extract_medical_entities(narrative_input)
            
            st.success("Extraction complete!")
            
            # Display in structured format
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Demographics")
                st.markdown(f"**Age:** {extracted['age'] if extracted['age'] else 'Not stated'}")
                st.markdown(f"**Sex:** {extracted['sex'].capitalize() if extracted['sex'] else 'Not stated'}")
            
            with col2:
                st.subheader("Chief Complaint")
                st.markdown(f"_{extracted['chief_complaint']}_" if extracted['chief_complaint'] else "_No complaint extracted_")
            
            st.divider()
            
            col_sym, col_timeline = st.columns(2)
            
            with col_sym:
                st.subheader("Symptoms Found")
                if extracted['symptoms_found']:
                    for symptom in extracted['symptoms_found']:
                        st.markdown(f"- {symptom}")
                else:
                    st.caption("No symptoms extracted")
            
            with col_timeline:
                st.subheader("Timeline/Onset")
                if extracted['timeline_onset']:
                    st.markdown(f"_{extracted['timeline_onset']}_")
                else:
                    st.caption("No timeline information extracted")
            
            st.divider()
            
            st.subheader("Aggravating / Alleviating Factors")
            if extracted['aggravating_or_alleviating_factors']:
                for factor in extracted['aggravating_or_alleviating_factors']:
                    st.markdown(f"- {factor}")
            else:
                st.caption("No aggravating or alleviating factors extracted")
            
            st.divider()
            
            # Display raw JSON
            with st.expander("📋 Raw JSON Output"):
                st.code(json.dumps(extracted, indent=2), language="json")
            
            # Download option
            json_str = json.dumps(extracted, indent=2)
            st.download_button(
                "📥 Download as JSON",
                data=json_str,
                file_name=f"medical_entities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )
    
    st.divider()
    st.info(
        "**How it works:** This tool extracts entities like age, sex, symptoms, timeline, and factors directly from "
        "the narrative text. It does NOT interpret, diagnose, or assign severity. It only extracts what is explicitly stated."
    )

with tab_risk:
    st.subheader("⚠️ Clinical Risk Assessment")
    st.caption("Analyzes extracted medical information to identify red flags, data gaps, and worst-case scenarios that need to be excluded.")
    
    st.divider()
    
    # Option 1: Use narrative input
    st.markdown("**Option 1: From Narrative Text**")
    narrative_for_risk = st.text_area(
        "Paste patient narrative here:",
        placeholder="Example: I'm a 55-year-old man with crushing chest pain for 30 minutes, radiating to my left arm. Also shortness of breath.",
        height=120,
        label_visibility="collapsed",
        key="risk_narrative"
    )
    
    # Option 2: Input extracted entities directly
    st.markdown("**Option 2: From Extracted Entities (JSON)**")
    entities_json_input = st.text_area(
        "Or paste extracted entities as JSON:",
        placeholder='{"age": 55, "sex": "male", "chief_complaint": "Chest pain", "symptoms_found": ["chest pain", "shortness of breath"], "timeline_onset": "30 minutes", "aggravating_or_alleviating_factors": []}',
        height=100,
        label_visibility="collapsed",
        key="entities_json"
    )
    
    st.markdown("**Optional: Vital Signs**")
    col_v1, col_v2, col_v3, col_v4 = st.columns(4)
    with col_v1:
        temp_risk = st.number_input("Temperature (°F)", 90.0, 110.0, 98.6, 0.1, key="temp_risk")
    with col_v2:
        hr_risk = st.number_input("Heart Rate (bpm)", 20, 250, 75, 1, key="hr_risk")
    with col_v3:
        spo2_risk = st.number_input("SpO₂ (%)", 50, 100, 98, 1, key="spo2_risk")
    with col_v4:
        sbp_risk = st.number_input("Systolic BP (mmHg)", 60, 260, 120, 1, key="sbp_risk")
    
    if st.button("Assess Clinical Risk", type="primary", use_container_width=True):
        try:
            # Get entities
            if entities_json_input.strip():
                try:
                    extracted_ents = json.loads(entities_json_input)
                except json.JSONDecodeError:
                    st.error("Invalid JSON format for entities.")
                    st.stop()
            elif narrative_for_risk.strip():
                with st.spinner("Extracting entities from narrative..."):
                    extracted_ents = extract_medical_entities(narrative_for_risk)
            else:
                st.error("Please provide either a narrative or extracted entities.")
                st.stop()
            
            # Prepare vitals
            vitals_dict = {
                "temperature": temp_risk,
                "heart_rate": hr_risk,
                "spo2": spo2_risk,
                "blood_pressure": f"{sbp_risk}/{int(sbp_risk * 0.6)}"  # Simple diastolic estimate
            }
            
            # Assess risk
            with st.spinner("Assessing clinical risk..."):
                risk_assessment = assess_clinical_risk(extracted_ents, vitals_dict)
            
            st.success("Risk assessment complete!")
            
            # Display results
            col_flags, col_gaps = st.columns(2)
            
            with col_flags:
                st.subheader("🚩 Red Flags Identified")
                if risk_assessment['red_flags_present']:
                    for i, flag in enumerate(risk_assessment['red_flags_present'], 1):
                        st.markdown(f"**{i}.** {flag}")
                else:
                    st.info("No red flags identified.")
            
            with col_gaps:
                st.subheader("📋 Critical Data Gaps")
                if risk_assessment['critical_missing_data_points']:
                    for i, gap in enumerate(risk_assessment['critical_missing_data_points'][:5], 1):
                        st.markdown(f"**{i}.** {gap}")
                    if len(risk_assessment['critical_missing_data_points']) > 5:
                        st.caption(f"... and {len(risk_assessment['critical_missing_data_points']) - 5} more")
                else:
                    st.info("No critical data gaps identified.")
            
            st.divider()
            
            st.subheader("⚠️ Worst-Case Scenarios to Exclude")
            if risk_assessment['worst_case_scenarios_to_exclude']:
                cols = st.columns(2)
                for i, scenario in enumerate(risk_assessment['worst_case_scenarios_to_exclude']):
                    with cols[i % 2]:
                        st.markdown(f"- {scenario}")
            else:
                st.info("No critical scenarios identified for this presentation.")
            
            st.divider()
            
            # Display raw JSON
            with st.expander("📋 Raw JSON Output"):
                st.code(json.dumps(risk_assessment, indent=2), language="json")
            
            # Download option
            json_str = json.dumps(risk_assessment, indent=2)
            st.download_button(
                "📥 Download as JSON",
                data=json_str,
                file_name=f"clinical_risk_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )
        
        except Exception as e:
            st.error(f"Error during assessment: {str(e)}")
    
    st.divider()
    st.info(
        "**How it works:** This tool analyzes extracted medical information to identify:\n"
        "• **Red Flags**: Critical findings suggesting serious conditions\n"
        "• **Data Gaps**: Missing clinical information needed for full evaluation\n"
        "• **Scenarios**: Worst-case diagnoses that should be considered and excluded"
    )

with tab_triage:
    st.subheader("🏥 Conservative Clinical Triage Router")
    st.caption("Routes patients to appropriate care tiers based on clinical information and risk assessment. Uses 'when in doubt, route up' philosophy.")
    
    st.divider()
    
    st.markdown("**Step 1: Patient Information**")
    narrative_for_triage = st.text_area(
        "Paste patient narrative here:",
        placeholder="Example: 55-year-old male with crushing chest pain for 30 minutes, sweating, shortness of breath.",
        height=120,
        label_visibility="collapsed",
        key="triage_narrative"
    )
    
    st.markdown("**Step 2: Optional Vital Signs**")
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        temp_triage = st.number_input("Temperature (°F)", 90.0, 110.0, 98.6, 0.1, key="temp_triage")
    with col_t2:
        hr_triage = st.number_input("Heart Rate (bpm)", 20, 250, 75, 1, key="hr_triage")
    with col_t3:
        spo2_triage = st.number_input("SpO₂ (%)", 50, 100, 98, 1, key="spo2_triage")
    with col_t4:
        sbp_triage = st.number_input("Systolic BP (mmHg)", 60, 260, 120, 1, key="sbp_triage")
    
    if st.button("Route Patient to Care Tier", type="primary", use_container_width=True):
        try:
            if not narrative_for_triage.strip():
                st.error("Please provide patient narrative.")
                st.stop()
            
            # Step 1: Extract entities
            with st.spinner("Step 1: Extracting medical entities..."):
                extracted_ents = extract_medical_entities(narrative_for_triage)
            
            # Step 2: Assess risk
            vitals_dict_triage = {
                "temperature": temp_triage,
                "heart_rate": hr_triage,
                "spo2": spo2_triage,
                "blood_pressure": f"{sbp_triage}/{int(sbp_triage * 0.6)}"
            }
            with st.spinner("Step 2: Assessing clinical risk..."):
                risk_assessment = assess_clinical_risk(extracted_ents, vitals_dict_triage)
            
            # Step 3: Route patient
            with st.spinner("Step 3: Routing to appropriate care tier..."):
                triage_decision = route_patient(extracted_ents, risk_assessment, vitals_dict_triage)
            
            st.success("Triage routing complete!")
            
            # Display care tier with appropriate styling
            tier = triage_decision['care_tier']
            tier_color = {
                'EMERGENCY': '#d32f2f',
                'URGENT': '#fbc02d',
                'NON-URGENT': '#2196f3',
                'HOME-CARE': '#388e3c'
            }.get(tier, '#999')
            
            tier_emoji = {
                'EMERGENCY': '🚨',
                'URGENT': '⚠️',
                'NON-URGENT': 'ℹ️',
                'HOME-CARE': '✅'
            }.get(tier, '•')
            
            st.markdown(f"""
            <div style='padding: 1.5rem; border-radius: 8px; background-color: {tier_color}20; border-left: 4px solid {tier_color}; margin: 1rem 0;'>
                <h3 style='color: {tier_color}; margin-top: 0;'>{tier_emoji} {tier}</h3>
                <p style='margin: 0.5rem 0; font-size: 1.1rem;'><strong>{triage_decision['clinical_justification']}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            col_actions, col_msg = st.columns(2)
            
            with col_actions:
                st.subheader("🎯 Immediate Actions")
                for i, action in enumerate(triage_decision['immediate_actions'], 1):
                    st.markdown(f"**{i}.** {action}")
            
            with col_msg:
                st.subheader("💬 Patient Message")
                st.info(f"_{triage_decision['patient_facing_message']}_")
            
            st.divider()
            
            # Show the workflow
            with st.expander("📊 Triage Workflow Details"):
                workflow_col1, workflow_col2, workflow_col3 = st.columns(3)
                
                with workflow_col1:
                    st.markdown("**Step 1: Extraction**")
                    st.markdown(f"- Age: {extracted_ents.get('age', 'Unknown')}")
                    st.markdown(f"- Sex: {extracted_ents.get('sex', 'Unknown').capitalize() if extracted_ents.get('sex') else 'Unknown'}")
                    st.markdown(f"- Chief: {extracted_ents.get('chief_complaint', 'Unknown')[:40]}...")
                
                with workflow_col2:
                    st.markdown("**Step 2: Risk Assessment**")
                    st.markdown(f"- Red Flags: {len(risk_assessment['red_flags_present'])}")
                    for flag in risk_assessment['red_flags_present'][:2]:
                        st.markdown(f"  • {flag[:50]}...")
                
                with workflow_col3:
                    st.markdown("**Step 3: Routing**")
                    st.markdown(f"- **Care Tier: {tier}**")
                    st.markdown(f"- Philosophy: Conservative")
                    st.markdown(f"- Status: Routed")
            
            # Download decision
            decision_json = json.dumps(triage_decision, indent=2)
            st.download_button(
                "📥 Download Triage Decision",
                data=decision_json,
                file_name=f"triage_decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )
        
        except Exception as e:
            st.error(f"Error during triage routing: {str(e)}")
    
    st.divider()
    st.info(
        "**Care Tiers:**\n"
        "• 🚨 **EMERGENCY**: Life-threatening → Call 911 / Go to ER NOW\n"
        "• ⚠️ **URGENT**: Serious symptoms → Visit ER/Urgent Care TODAY\n"
        "• ℹ️ **NON-URGENT**: Minor issues → Schedule routine visit\n"
        "• ✅ **HOME-CARE**: Stable/minor → Manage at home with monitoring\n\n"
        "**Philosophy**: 'When in doubt, route UP' — Conservative approach prioritizes patient safety."
    )
    if not has_any_symptom:
        st.info("👈 Go to **Symptoms** tab first, then come back here for nearby clinics.")
    elif not location:
        st.warning("📍 Enter your **City / ZIP code** in the sidebar to find nearby clinics.")
    else:
        loc_clean = location.strip()

        if st.session_state.is_guest:
            st.info("🔍 **Guest:** Basic clinic locations shown. Sign up for detailed guidance & tips.")

        if is_emergency:
            st.error("### 🚨 EMERGENCY — Find Nearest ER")
            st.markdown("Call **911** first.")
            query = urllib.parse.quote(f"Emergency Room near {loc_clean}")
            maps_url = f"https://www.google.com/maps/search/{query}"
            st.markdown(
                f"<a href='{maps_url}' target='_blank' class='pulse-glow' style='display:inline-block;"
                f"padding:1rem 2rem;background:#d32f2f;color:white;border-radius:8px;"
                f"text-decoration:none;font-weight:700;font-size:1.2rem;'>"
                f"📍 Show Emergency Rooms near {loc_clean}</a>",
                unsafe_allow_html=True,
            )
            st.markdown("""
            <div style="margin-top:1rem;padding:1rem;background:#ffebee;border-radius:8px;border-left:4px solid #d32f2f;">
            <strong>⚠️ Before you go:</strong>
            <ul>
            <li>Call 911 if you cannot drive safely</li>
            <li>Bring your ID, insurance card, and medication list</li>
            <li>Do not eat or drink if surgery may be needed</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        elif needs_doctor:
            st.warning("### 📅 Find a Doctor or Urgent Care")
            st.markdown("Visit an **Urgent Care** or call your **Primary Care Physician** today.")
            q_urgent = urllib.parse.quote(f"Urgent Care near {loc_clean}")
            q_pcp = urllib.parse.quote(f"Primary care doctor near {loc_clean}")
            u1, u2 = st.columns(2)
            with u1:
                st.markdown(
                    f"<a href='https://www.google.com/maps/search/{q_urgent}' target='_blank' "
                    f"style='display:block;text-align:center;padding:1rem;background:#fbc02d;"
                    f"color:#333;border-radius:8px;text-decoration:none;font-weight:700;'>"
                    f"🏥 Urgent Care near {loc_clean.split(',')[0]}</a>",
                    unsafe_allow_html=True,
                )
            with u2:
                st.markdown(
                    f"<a href='https://www.google.com/maps/search/{q_pcp}' target='_blank' "
                    f"style='display:block;text-align:center;padding:1rem;background:#fff3e0;"
                    f"color:#333;border-radius:8px;text-decoration:none;font-weight:700;'>"
                    f"👨‍⚕️ PCP near {loc_clean.split(',')[0]}</a>",
                    unsafe_allow_html=True,
                )
            st.markdown("""
            <div style="margin-top:1rem;padding:1rem;background:#fff8e1;border-radius:8px;border-left:4px solid #fbc02d;">
            <strong>💡 Tips:</strong>
            <ul>
            <li>Call ahead to check walk-in availability</li>
            <li>Bring your ID, insurance card, and symptom notes</li>
            <li>Go to ER if symptoms worsen suddenly</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.success("### 🏡 Self-Care — Nearby Resources")
            st.markdown("Monitor symptoms at home. Here are useful nearby places:")
            q_pharm = urllib.parse.quote(f"Pharmacy near {loc_clean}")
            q_clinic = urllib.parse.quote(f"Walk-in clinic near {loc_clean}")
            u1, u2 = st.columns(2)
            with u1:
                st.markdown(
                    f"<a href='https://www.google.com/maps/search/{q_pharm}' target='_blank' "
                    f"style='display:block;text-align:center;padding:1rem;background:#388e3c;"
                    f"color:white;border-radius:8px;text-decoration:none;font-weight:700;'>"
                    f"💊 Pharmacy near {loc_clean.split(',')[0]}</a>",
                    unsafe_allow_html=True,
                )
            with u2:
                st.markdown(
                    f"<a href='https://www.google.com/maps/search/{q_clinic}' target='_blank' "
                    f"style='display:block;text-align:center;padding:1rem;background:#e8f5e9;"
                    f"color:#333;border-radius:8px;text-decoration:none;font-weight:700;'>"
                    f"🏪 Walk-in Clinic near {loc_clean.split(',')[0]}</a>",
                    unsafe_allow_html=True,
                )
            st.markdown("""
            <div style="margin-top:1rem;padding:1rem;background:#e8f5e9;border-radius:8px;border-left:4px solid #388e3c;">
            <strong>✅ Self-Care Checklist:</strong>
            <ul>
            <li>Rest and stay hydrated</li>
            <li>OTC medication for fever/pain as needed</li>
            <li>Contact a doctor if symptoms persist > 7 days</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

st.divider()
st.caption(
    "⚠️ **Medical Disclaimer:** This tool provides **informational triage guidance only** and "
    "does **not** diagnose, treat, or replace professional medical advice. "
    "If you are experiencing a medical emergency, call emergency services immediately."
)
