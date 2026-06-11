import streamlit as st
from datetime import datetime
import re
import urllib.parse
from medtriage import get_db, signup_user, login_user, validate_email

st.set_page_config(page_title="MedTriage Pro+", page_icon="🏥", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Color+Emoji&amp;display=swap');
html, body, .stApp, .stApp * {
    font-family: 'Noto Color Emoji', 'Apple Color Emoji', 'Segoe UI Emoji', sans-serif;
}
.emoji { font-family: 'Noto Color Emoji', 'Apple Color Emoji', 'Segoe UI Emoji', sans-serif; }
.circle-red { display:inline-block; width:12px; height:12px; border-radius:50%; background:#d32f2f; margin-right:4px; }
.circle-yellow { display:inline-block; width:12px; height:12px; border-radius:50%; background:#fbc02d; margin-right:4px; }
.circle-green { display:inline-block; width:12px; height:12px; border-radius:50%; background:#388e3c; margin-right:4px; }
.badge-emergency { background:#d32f2f; color:#fff; padding:2px 10px; border-radius:4px; font-weight:700; font-size:0.85rem; }
.badge-doctor { background:#fbc02d; color:#333; padding:2px 10px; border-radius:4px; font-weight:700; font-size:0.85rem; }
.badge-home { background:#388e3c; color:#fff; padding:2px 10px; border-radius:4px; font-weight:700; font-size:0.85rem; }
.action-card {
    padding: 1rem; border-radius: 8px; margin: 0.5rem 0;
    border: 1px solid #e0e0e0; background: #fafafa;
}
.clinic-item {
    padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;
    border-left: 4px solid;
    background: #ffffff;
}
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

if not st.session_state.authenticated:

    st.title("🏥 MedTriage Pro+")
    st.markdown("**Medical Symptom Checker & Triage Assistant**")
    st.caption("Please sign in or create an account to continue.")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔑 Sign In", use_container_width=True):
            st.session_state.auth_page = "login"
    with col2:
        if st.button("📝 Sign Up", use_container_width=True):
            st.session_state.auth_page = "signup"

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

    st.divider()
    st.caption(
        "⚠️ **Disclaimer:** This tool provides informational triage guidance only. "
        "It does not diagnose or replace professional medical advice."
    )
    st.stop()

col_title, col_user, col_reset = st.columns([4, 2, 1])
with col_title:
    st.title("🏥 Enhanced Symptom Checker & Triage")
    st.caption("⚕️ Informational triage guidance only — does **not** replace professional medical advice.")
with col_user:
    st.markdown(f"👤 **{st.session_state.username}**  \n{st.session_state.user_email}")
with col_reset:
    if st.button("🚪 Logout", use_container_width=True):
        for k in ["authenticated", "username", "user_email", "auth_page"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

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

    st.divider()
    st.subheader("📍 Your Location")
    location = st.text_input("City / ZIP code", placeholder="e.g. New York, NY or 10001",
                              help="Enter your city or ZIP code to find nearby clinics")
    if st.button("📍 Detect My Location", use_container_width=True):
        st.info("Allow browser location access when prompted, then refresh.")
        st.markdown(
            """
            <script>
            navigator.geolocation.getCurrentPosition(function(pos) {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                const input = window.parent.document.querySelector('input[aria-label="City / ZIP code"]');
                if (input) input.value = lat + ',' + lon;
            });
            </script>
            """,
            unsafe_allow_html=True,
        )

tab_sym, tab_pain, tab_report, tab_nearby = st.tabs(["🤒 Symptoms", "📍 Pain", "📄 Report", "📍 Nearby Clinics"])

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

with tab_report:
    all_symptoms = emergency + general + respiratory + digestive + neuro + skin
    has_any_symptom = bool(all_symptoms or pain_level > 0 or pain_loc)

    if not has_any_symptom:
        st.info("👈 Select symptoms or rate your pain to generate a report.")
    else:
        red_flags, yellow_flags = [], []

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
        if "Pregnancy" in preexisting and any(s in emergency for s in ["Chest pain or pressure", "Severe shortness of breath", "Severe bleeding"]):
            red_flags.append("Pregnancy with critical symptoms")

        crit_symptoms = {"Chest pain or pressure", "Severe shortness of breath",
                         "Sudden weakness/numbness (one side)", "Difficulty speaking",
                         "Loss of consciousness", "Severe bleeding",
                         "Head injury with confusion", "Severe allergic reaction",
                         "Suicidal thoughts", "Severe abdominal pain", "Seizure"}
        is_emergency = bool(set(emergency) & crit_symptoms) or bool(red_flags) or pain_level >= 9
        is_emergency = is_emergency or ("Fainting" in general and age >= 60)

        needs_doctor = (temp >= 102) or len(yellow_flags) >= 3 or duration >= 7
        needs_doctor = needs_doctor or pain_level >= 5
        needs_doctor = needs_doctor or "Headache (severe)" in neuro
        needs_doctor = needs_doctor or ("Signs of infection (redness, warmth)" in skin)
        needs_doctor = needs_doctor or ("Chest" in pain_loc and pain_level >= 4)
        needs_doctor = needs_doctor or {"Vomiting", "Diarrhea"}.issubset(set(digestive))

        triage_label = "EMERGENCY" if is_emergency else "NEEDS DOCTOR" if needs_doctor else "HOME CARE"

        triage_color = "#d32f2f" if is_emergency else "#fbc02d" if needs_doctor else "#388e3c"

        st.subheader("📋 Triage Assessment")

        col_alert, col_metrics = st.columns([2, 1])
        with col_alert:
            if is_emergency:
                st.error("### 🚨 URGENT — EMERGENCY CARE REQUIRED")
                st.markdown("Call **911** immediately. Do not wait.")
            elif needs_doctor:
                st.warning("### 📅 SCHEDULE A DOCTOR VISIT")
                st.markdown("Contact your PCP or visit Urgent Care today.")
            else:
                st.success("### 🏡 HOME CARE & MONITORING")
                st.markdown("Rest, hydrate, and monitor symptoms.")
        with col_metrics:
            st.metric("Triage Level", triage_label, delta_color="off")
            st.metric("Pain Level", f"{pain_level}/10" if pain_level > 0 else "None")
            st.metric("Duration", f"{duration} day(s)")

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
                    ("🚨 Emergency", emergency), ("🫁 Respiratory", respiratory),
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

        st.divider()

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
  Triage: {triage_label}
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

        st.divider()

        st.subheader("⚡ Quick Actions")
        qc1, qc2, qc3 = st.columns(3)
        with qc1:
            if is_emergency:
                st.markdown(
                    "<a href='tel:911' target='_blank' style='display:block;text-align:center;"
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
                    f"text-decoration:none;font-weight:700;'>🗺️ Find Near {location.split(',')[0]}</a>",
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

with tab_nearby:
    if not has_any_symptom:
        st.info("👈 Go to **Symptoms** tab first, then come back here for nearby clinics.")
    elif not location:
        st.warning("📍 Enter your **City / ZIP code** in the sidebar to find nearby clinics.")
    else:
        loc_clean = location.strip()

        if is_emergency:
            st.error("### 🚨 EMERGENCY — Find Nearest ER")
            st.markdown("Call **911** first. If you can drive, here are nearby Emergency Rooms:")

            query = urllib.parse.quote(f"Emergency Room near {loc_clean}")
            maps_url = f"https://www.google.com/maps/search/{query}"
            st.markdown(
                f"<a href='{maps_url}' target='_blank' style='display:inline-block;"
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
