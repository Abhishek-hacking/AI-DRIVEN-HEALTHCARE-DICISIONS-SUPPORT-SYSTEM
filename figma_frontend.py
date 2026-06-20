from __future__ import annotations

import json
import os
from base64 import b64encode
from datetime import datetime
from html import escape
from pathlib import Path
from urllib import error, request

import streamlit as st

ASSET_DIR = Path(__file__).resolve().parent / "assets"
BOOKINGS_FILE = Path(__file__).resolve().parent / "appointments.json"
TIME_SLOTS = ["09:00 AM", "10:30 AM", "12:00 PM", "02:00 PM", "04:30 PM", "06:00 PM"]
CONSULTATION_TYPES = ["Video Call", "In-person Visit", "Phone Consultation"]

DOCTORS = [
    ("Dr. Sarah Johnson", "Cardiologist", "4.9", "127", "15+ years", "New York, NY", "Video & In-person consultations", "$150", "Available Today", "doctor_card_1.svg"),
    ("Dr. Michael Chen", "Pediatrician", "4.8", "98", "12+ years", "San Francisco, CA", "Video & In-person consultations", "$120", "Available Tomorrow", "doctor_card_2.svg"),
    ("Dr. Emily Rodriguez", "Dermatologist", "4.9", "156", "10+ years", "Los Angeles, CA", "Video & In-person consultations", "$130", "Available Today", "doctor_card_3.svg"),
    ("Dr. James Patel", "General Physician", "4.7", "84", "9+ years", "Chicago, IL", "Video consultations", "$90", "Available Today", "doctor_card_3.svg"),
    ("Dr. Priya Nair", "Neurologist", "4.9", "112", "14+ years", "Seattle, WA", "Video & In-person consultations", "$180", "Available Tomorrow", "doctor_card_1.svg"),
    ("Dr. Robert Kim", "Orthopedic", "4.8", "103", "11+ years", "Austin, TX", "In-person consultations", "$140", "Available Today", "doctor_card_2.svg"),
]

QUICK_OPTIONS = [
    "Headache",
    "Fever",
    "Cough",
    "Cold",
    "Body pain",
    "Dizziness",
    "Low energy",
    "Weakness",
    "Stomach pain",
    "Acidity",
    "Nausea",
    "Indigestion",
    "Runny nose",
    "Sore throat",
    "Sneezing",
    "Breathing issue",
    "Allergy",
    "Diarrhea",
    "Dry mouth",
    "Fatigue",
]
API_BASE_URL = os.getenv("HEALTHCARE_API_URL", "http://127.0.0.1:8001")
API_TIMEOUT_SECONDS = int(os.getenv("HEALTHCARE_API_TIMEOUT", "45"))


def now_text() -> str:
    return datetime.now().strftime("%I:%M %p").lstrip("0")


def welcome_message() -> dict[str, str]:
    return {
        "role": "assistant",
        "content": (
            "Hello! I'm your HealthCare+ AI assistant. I'll help you understand your symptoms through a few questions.\n\n"
            "This is for informational purposes only and not a substitute for professional medical advice.\n\n"
            "Let's start: What symptoms are you experiencing right now?"
        ),
        "timestamp": now_text(),
    }


def init_state() -> None:
    st.session_state.setdefault("page", "Home")
    st.session_state.setdefault("chat_log", [welcome_message()])
    st.session_state.setdefault("latest_result", None)
    st.session_state.setdefault("booked_doctor", None)
    st.session_state.setdefault("selected_doctor_index", None)
    st.session_state.setdefault("booking_notice", None)
    st.session_state.setdefault("session_id", None)
    st.session_state.setdefault("api_error", None)
    st.session_state.setdefault("is_loading", False)


def go_to(page: str) -> None:
    st.session_state.page = page


def reset_chat() -> None:
    st.session_state.chat_log = [welcome_message()]
    st.session_state.latest_result = None
    st.session_state.session_id = None
    st.session_state.api_error = None
    st.session_state.is_loading = False


def read_appointments() -> list[dict]:
    if not BOOKINGS_FILE.exists():
        return []
    try:
        return json.loads(BOOKINGS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_appointment(appointment: dict) -> None:
    appointments = read_appointments()
    appointments.append(appointment)
    BOOKINGS_FILE.write_text(json.dumps(appointments, indent=2), encoding="utf-8")


def start_booking(index: int) -> None:
    st.session_state.selected_doctor_index = index
    st.session_state.booking_notice = None


def cancel_booking() -> None:
    st.session_state.selected_doctor_index = None


def confirm_booking(doctor: tuple[str, ...], preferred_date, preferred_time: str, consultation_type: str, reason: str) -> None:
    name, specialty, _, _, _, location, _, fee, _, _ = doctor
    appointment = {
        "doctor_name": name,
        "specialty": specialty,
        "location": location,
        "consultation_fee": fee,
        "preferred_date": preferred_date.isoformat(),
        "preferred_time": preferred_time,
        "consultation_type": consultation_type,
        "reason": reason.strip(),
        "status": "confirmed",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    save_appointment(appointment)
    st.session_state.booked_doctor = name
    st.session_state.booking_notice = f"Booking confirmed with {name} on {preferred_date.strftime('%d %b %Y')} at {preferred_time}."
    st.session_state.selected_doctor_index = None


def log_message(role: str, content: str) -> None:
    st.session_state.chat_log.append({"role": role, "content": content, "timestamp": now_text()})


def get_quick_options() -> list[str]:
    if not st.session_state.chat_log:
        return QUICK_OPTIONS[:4]

    last_assistant = next(
        (item["content"].lower() for item in reversed(st.session_state.chat_log) if item["role"] == "assistant"),
        "",
    )

    if "how long" in last_assistant:
        return ["A few hours", "1-2 days", "3-7 days", "More than a week", "More than a month"]
    if "body pain or headache" in last_assistant:
        return ["Yes", "No", "Only body pain", "Only headache"]
    if "measured your temperature" in last_assistant:
        return ["No", "99 F", "101 F", "Above 102 F", "Not sure"]
    if "where exactly is the headache" in last_assistant:
        return ["Forehead", "One side", "Behind eyes", "Whole head"]
    if "how severe is the headache" in last_assistant:
        return ["Mild", "Moderate", "Severe", "Very severe"]
    if "stress or poor sleep" in last_assistant:
        return ["Yes", "No", "Poor sleep", "Stress"]
    if "burning in the stomach or chest" in last_assistant:
        return ["Stomach", "Chest", "Both", "Not sure"]
    if "spicy or oily food" in last_assistant:
        return ["Yes", "No", "Spicy food", "Oily food"]
    if "worse after meals" in last_assistant:
        return ["Yes", "No", "Sometimes", "Not sure"]
    if "runny nose or sneezing" in last_assistant:
        return ["Runny nose", "Sneezing", "Both", "No"]
    if "sore throat" in last_assistant:
        return ["Yes", "No", "Mild", "Severe"]
    if "weakness or tiredness" in last_assistant:
        return ["Yes", "No", "Weakness", "Tiredness"]
    if "dry or with mucus" in last_assistant:
        return ["Dry", "With mucus", "Both", "Not sure"]
    if "fever or sore throat" in last_assistant:
        return ["Fever", "Sore throat", "Both", "Neither"]
    if "worse at night or after cold exposure" in last_assistant:
        return ["At night", "Cold exposure", "Both", "No"]
    if "painful to swallow" in last_assistant:
        return ["Yes", "No", "Mild pain", "Severe pain"]
    if "fever, cough, or runny nose" in last_assistant:
        return ["Fever", "Cough", "Runny nose", "More than one"]
    if "itchy nose or eyes" in last_assistant:
        return ["Itchy nose", "Itchy eyes", "Both", "No"]
    if "dust, weather change, or strong smells" in last_assistant:
        return ["Dust", "Weather change", "Strong smells", "Not sure"]
    if "breathing difficulty or wheezing" in last_assistant:
        return ["No", "Breathing difficulty", "Wheezing", "Both"]
    if "where exactly is the stomach pain located" in last_assistant:
        return ["Upper abdomen", "Lower abdomen", "Whole stomach", "Not sure"]
    if "after meals or outside food" in last_assistant:
        return ["After meals", "Outside food", "Both", "Not sure"]
    if "vomiting, loose stools, or acidity" in last_assistant:
        return ["Vomiting", "Loose stools", "Acidity", "More than one"]
    if "loose stools have you had today" in last_assistant:
        return ["1-2", "3-4", "5 or more", "Not sure"]
    if "able to drink fluids normally" in last_assistant:
        return ["Yes", "No", "Small sips only", "Not sure"]
    if "fever, vomiting, or stomach cramps" in last_assistant:
        return ["Fever", "Vomiting", "Stomach cramps", "More than one"]
    if "have you vomited or only felt like vomiting" in last_assistant:
        return ["Only nausea", "Vomited once", "Vomited many times", "Not sure"]
    if "keep fluids down" in last_assistant:
        return ["Yes", "No", "Only small amounts", "Not sure"]
    if "dry mouth, dizziness, or reduced urination" in last_assistant:
        return ["Dry mouth", "Dizziness", "Reduced urination", "More than one"]
    if "fever, vomiting, diarrhea, or low fluid intake" in last_assistant:
        return ["Fever", "Vomiting", "Diarrhea", "Low fluid intake"]
    if "drink ors or water comfortably" in last_assistant:
        return ["Yes", "No", "Small sips only", "Not sure"]
    if "generalized or limited to one area" in last_assistant:
        return ["Generalized", "One area", "Mostly back", "Mostly legs"]
    if "after fever, strain, or poor sleep" in last_assistant:
        return ["After fever", "After strain", "Poor sleep", "Not sure"]
    if "weakness or low energy" in last_assistant:
        return ["A day", "2-3 days", "A week", "More than a week"]
    if "after fever, poor sleep, stress, or low food intake" in last_assistant:
        return ["After fever", "Poor sleep", "Stress", "Low food intake"]
    if "dizziness, dry mouth, or body pain" in last_assistant:
        return ["Dizziness", "Dry mouth", "Body pain", "More than one"]
    if "dizziness mild, moderate, or severe" in last_assistant:
        return ["Mild", "Moderate", "Severe", "Very severe"]
    if "low food intake, fever, or dehydration" in last_assistant:
        return ["Low food intake", "Fever", "Dehydration", "Not sure"]
    if "weakness, vomiting, or headache" in last_assistant:
        return ["Weakness", "Vomiting", "Headache", "More than one"]
    if "what symptoms are you experiencing" in last_assistant:
        return QUICK_OPTIONS[:12]
    return QUICK_OPTIONS[:12]


def asset_data_uri(filename: str) -> str:
    path = ASSET_DIR / filename
    encoded = b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def call_api(path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{API_BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=API_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def render_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
        :root{--blue:#1668c7;--ink:#1d284c;--muted:#7f91b2;--line:#dbe6f3;--shadow:0 18px 40px rgba(19,50,94,.10);}
        *{font-family:'Manrope',sans-serif}.stApp{background:linear-gradient(180deg,#f7fbff 0%,#eef5ff 30%,#fff 100%);color:var(--ink)}
        [data-testid="stHeader"]{background:transparent}[data-testid="stSidebar"]{display:none}[data-testid="stToolbar"]{display:none}.block-container{max-width:1140px;padding-top:.2rem;padding-bottom:1.5rem}
        .brand{display:flex;align-items:center;gap:12px;font-weight:700;color:var(--blue);font-size:1.05rem}.brand-mark{width:38px;height:38px;border-radius:12px;display:inline-flex;align-items:center;justify-content:center;background:var(--blue);color:#fff;font-weight:800}
        .badge{display:inline-flex;align-items:center;gap:8px;background:#eef5ff;color:#3c82dd;border-radius:999px;padding:8px 14px;font-size:.88rem;margin-bottom:12px}
        .hero-title{font-size:clamp(2.7rem,5vw,4.4rem);line-height:1.04;letter-spacing:-.05em;font-weight:800;color:#1f2750;margin:0 0 12px}.hero-copy{color:var(--muted);font-size:1.03rem;line-height:1.65;max-width:560px}
        .hero-card{position:relative;min-height:410px;border-radius:26px;overflow:hidden;box-shadow:var(--shadow);background:#dde8f1}
        .hero-image,.cta-real-image,.doctor-photo{width:100%;height:100%;object-fit:cover;display:block}
        .floating-doctors{position:absolute;left:-24px;bottom:22px;background:rgba(255,255,255,.98);border-radius:20px;box-shadow:0 18px 40px rgba(25,61,114,.18);padding:16px 18px;display:flex;align-items:center;gap:14px;min-width:245px}
        .pulse{width:54px;height:54px;border-radius:50%;background:#e7fff0;color:#1ca05c;display:inline-flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:700}
        .metric-band{background:var(--blue);margin:22px calc(50% - 50vw) 0;padding:22px 0 24px}.metric-inner{max-width:1140px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:14px;color:#fff;text-align:center}.metric-value{font-size:2rem;font-weight:800;margin-top:6px}
        .section-title{text-align:center;font-size:clamp(2rem,3.4vw,3rem);color:#17244f;font-weight:800;letter-spacing:-.04em;margin:44px 0 8px}.section-copy{text-align:center;color:var(--muted);max-width:760px;margin:0 auto 26px;font-size:1.02rem;line-height:1.6}
        .feature-card,.search-panel,.doctor-card,.chat-shell,.result-panel{border:1px solid var(--line);background:#fff;border-radius:24px;box-shadow:0 12px 28px rgba(19,50,94,.05)}.feature-card{padding:20px;min-height:190px}.feature-icon{width:42px;height:42px;border-radius:14px;background:#eaf2ff;color:var(--blue);display:inline-flex;align-items:center;justify-content:center;font-size:1.05rem;margin-bottom:16px}.feature-title{font-weight:800;color:#23345c;font-size:1.1rem;margin-bottom:10px}.feature-copy,.panel-muted,.page-subtitle,.doctor-specialty,.doctor-line,.doctor-meta,.doctor-mode,.doctor-fee-row,.subtle{color:var(--muted);line-height:1.55}
        .cta-panel{display:grid;grid-template-columns:1fr 1fr;margin-top:36px;background:var(--blue);border-radius:26px;overflow:hidden;box-shadow:var(--shadow)}.cta-copy-wrap{padding:42px 30px;color:#fff}.cta-title{font-size:2.2rem;font-weight:800;letter-spacing:-.04em;margin-bottom:12px}.cta-copy{opacity:.92;line-height:1.65}.cta-image{min-height:360px;background:#eef4fb}
        .page-title{font-size:2.8rem;font-weight:800;color:#1d284c;margin:4px 0 6px;letter-spacing:-.04em}
        .page-shell{max-width:1120px;margin:0 auto}
        .notice{border:1px solid #bfdaff;background:#f1f7ff;color:#38558d;border-radius:18px;padding:14px 18px;margin-bottom:16px;line-height:1.55}
        .chat-shell{border:1px solid var(--line);background:#fff;border-radius:22px;box-shadow:0 14px 34px rgba(19,50,94,.06);overflow:hidden}
        .chat-body{min-height:220px;max-height:420px;overflow-y:auto;padding:18px 20px 10px;background:#ffffff}
        .chat-row{display:flex;align-items:flex-start;gap:10px;margin-bottom:10px}
        .chat-row.user{justify-content:flex-end}
        .avatar{width:40px;height:40px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#1f74db,#1668c7);color:#fff;font-size:.92rem;flex:0 0 auto}
        .message-wrap{flex:0 0 auto;max-width:74%}
        .chat-row.user .message-wrap{display:flex;flex-direction:column;align-items:flex-end}
        .bubble{display:inline-block;width:auto;max-width:100%;min-width:110px;border:1px solid #dbe6f3;background:#fff;border-radius:18px;padding:15px 16px;color:#28365d;line-height:1.65;white-space:pre-wrap;word-break:keep-all;overflow-wrap:normal}
        .chat-row.user .bubble{background:linear-gradient(135deg,#2d84ea,#1668c7);color:#fff;border-color:transparent;border-radius:18px;min-width:92px}
        .bubble-time{font-size:.78rem;color:#98a6c4;margin-top:4px}
        .typing-row{display:flex;align-items:center;gap:10px;margin-bottom:8px;animation:fadeIn .25s ease}
        .typing-bubble{background:#ffffff;border:1px solid #dbe6f3;border-radius:18px 18px 18px 8px;padding:12px 14px;box-shadow:0 10px 26px rgba(19,50,94,.05)}
        .typing-dots{display:flex;gap:6px}
        .typing-dots span{width:8px;height:8px;border-radius:999px;background:#8fb0da;animation:typingPulse 1.1s infinite ease-in-out}
        .typing-dots span:nth-child(2){animation-delay:.15s}
        .typing-dots span:nth-child(3){animation-delay:.3s}
        .chat-footer{border-top:1px solid var(--line);background:#fff}
        .quick-strip{padding:10px 16px 12px 16px;background:#fff}
        .quick-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
        .quick-chip{width:100%}
        .composer-wrap{border-top:1px solid var(--line);padding:12px 16px 8px 16px;background:#fff}
        .danger-banner{margin-top:10px;border:1px solid #ffcbcb;background:#fff0f0;color:#9f2c2c;border-radius:16px;padding:12px 14px;line-height:1.5}
        .result-panel{margin-top:14px;padding:18px;border-radius:22px;box-shadow:0 18px 38px rgba(19,50,94,.09);border:1px solid #dbe6f3;background:linear-gradient(180deg,#ffffff 0%,#f9fcff 100%)}
        .pill{display:inline-flex;align-items:center;border-radius:999px;padding:7px 12px;font-size:.82rem;font-weight:800;letter-spacing:.05em;margin-bottom:10px}
        .pill.safe{background:#edfdf4;color:#1f9d62}
        .pill.danger{background:#fff0f0;color:#c83f3f}
        .result-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:10px 0 14px 0}
        .result-stat{border:1px solid #e0ebf6;border-radius:16px;padding:12px;background:#ffffff}
        .result-stat-label{font-size:.76rem;text-transform:uppercase;letter-spacing:.08em;color:#91a2bf;font-weight:800}
        .result-stat-value{font-size:1.02rem;color:#22325d;font-weight:800;margin-top:4px}
        .doctor-modal{border:1px solid #ffd1d1;background:linear-gradient(180deg,#fff8f8 0%,#fff0f0 100%);border-radius:22px;padding:18px;box-shadow:0 18px 36px rgba(200,63,63,.10)}
        .doctor-modal-title{font-size:1.25rem;font-weight:800;color:#b23333;margin-bottom:6px}
        .doctor-modal-copy{color:#a04646;line-height:1.6}
        @keyframes typingPulse{0%,80%,100%{transform:scale(.8);opacity:.55}40%{transform:scale(1);opacity:1}}
        @keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}
        .doctor-page-shell{max-width:1120px;margin:0 auto}
        .doctor-page-top{display:flex;justify-content:space-between;align-items:end;gap:18px;margin-bottom:14px}
        .doctor-page-copy{max-width:620px}
        .search-panel{padding:18px 20px;margin-bottom:18px;border-radius:26px;box-shadow:0 16px 34px rgba(19,50,94,.06)}
        .doctor-card{overflow:hidden;min-height:498px;border-radius:24px;box-shadow:0 18px 34px rgba(19,50,94,.08)}
        .doctor-image{height:190px;position:relative;background:#dfe8f1}
        .doctor-chip{position:absolute;top:14px;right:14px;background:rgba(255,255,255,.96);color:#5a6b90;border-radius:999px;padding:7px 12px;font-size:.76rem;font-weight:800;box-shadow:0 8px 20px rgba(19,50,94,.10)}
        .doctor-content{padding:18px 20px 20px}
        .doctor-name{font-size:1.26rem;color:#22325d;font-weight:800;margin-bottom:6px}
        .doctor-meta{display:flex;gap:14px;flex-wrap:wrap;margin-top:14px}
        .doctor-stat{display:inline-flex;align-items:center;gap:6px}
        .doctor-mode{margin-top:8px;padding-bottom:10px;border-bottom:1px solid #e7eef8}
        .doctor-fee-row{display:flex;justify-content:space-between;align-items:center;margin-top:10px;font-size:1rem}
        .fee-value{color:#2d82eb;font-weight:800;font-size:1.15rem}
        .booking-panel{margin:8px 0 20px 0;padding:22px;border:1px solid #dbe6f3;border-radius:26px;background:linear-gradient(180deg,#ffffff 0%,#f7fbff 100%);box-shadow:0 20px 42px rgba(19,50,94,.10)}
        .booking-title{font-size:1.5rem;font-weight:800;color:#22325d;margin-bottom:4px}
        .booking-subtitle{color:#7486aa;margin-bottom:16px}
        .booking-strip{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:16px}
        .booking-pill{display:inline-flex;align-items:center;padding:8px 12px;border-radius:999px;background:#edf5ff;color:#3268b2;font-size:.84rem;font-weight:700}
        .stButton,.stFormSubmitButton{margin:0}.stButton button,.stFormSubmitButton button{width:100%;min-height:44px;border-radius:12px;border:1px solid #d7e4f6;padding:.58rem .95rem;font-weight:700;box-shadow:none;background:#ffffff!important;color:#23345c!important;white-space:nowrap!important}
        .stButton button[kind="primary"]{background:var(--blue)!important;color:#fff!important;border-color:var(--blue)!important}
        .stButton button[kind="secondary"]{background:#fff!important;color:#23345c!important;border-color:#d7e4f6!important}
        .stFormSubmitButton button, div[data-testid="stFormSubmitButton"] button{background:var(--blue)!important;color:#fff!important;border-color:var(--blue)!important}
        .stFormSubmitButton button:hover, div[data-testid="stFormSubmitButton"] button:hover{background:#0f56a6!important;color:#fff!important;border-color:#0f56a6!important}
        .stButton button:hover{border-color:#bcd2ef!important;color:#1668c7!important}
        .stButton button[kind="primary"]:hover{background:#0f56a6!important;color:#fff!important;border-color:#0f56a6!important}
        [data-testid="column"]{padding-top:0!important}
        div[data-testid="stHorizontalBlock"]{gap:.5rem}
        .quick-btn button{padding:.34rem .7rem!important;border-radius:12px!important;font-size:.86rem!important;min-height:34px!important;white-space:nowrap!important;width:100%!important}
        .input-label{font-weight:800;color:#2b3b62;margin-bottom:8px;font-size:.96rem}
        div[data-testid="stTextInput"] input{
            border-radius:12px!important;
            border:1px solid #d7e4f6!important;
            padding:.88rem 1rem!important;
            background:#ffffff!important;
            color:#22325d!important;
            box-shadow:none!important;
        }
        div[data-testid="stTextInput"] input::placeholder{
            color:#8a9abb!important;
            opacity:1!important;
        }
        div[data-testid="stTextInput"] > div{background:#ffffff!important}
        div[data-testid="stSelectbox"] > div,
        div[data-testid="stDateInput"] > div,
        div[data-testid="stTextArea"] > div{
            border-radius:12px!important;
            border:1px solid #d7e4f6!important;
            background:#ffffff!important;
            box-shadow:none!important;
        }
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        div[data-testid="stDateInput"] input,
        div[data-testid="stTextArea"] textarea{
            background:#ffffff!important;
            color:#22325d!important;
        }
        div[data-testid="stTextArea"] textarea::placeholder{
            color:#8a9abb!important;
            opacity:1!important;
        }
        .chat-controls{max-width:1120px;margin:8px auto 0 auto}
        @media (max-width:900px){.metric-inner{grid-template-columns:repeat(2,1fr)}.cta-panel{grid-template-columns:1fr}.bubble{max-width:88%}.result-grid{grid-template-columns:1fr}.quick-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_navbar() -> None:
    with st.container(border=True):
        left, mid, right = st.columns([1.35, 1.95, 1.15], vertical_alignment="center")
        with left:
            st.markdown('<div class="brand"><span class="brand-mark">+</span><span>HealthCare+</span></div>', unsafe_allow_html=True)
        with mid:
            nav_cols = st.columns([1, 1.35, 1], gap="small")
            for col, page in zip(nav_cols, ["Home", "Symptom Checker", "Doctors"]):
                with col:
                    if st.button(page, key=f"nav_{page}", use_container_width=True, type="secondary"):
                        go_to(page)
                        st.rerun()
        with right:
            if st.button("Book Appointment", key="book_top", use_container_width=True, type="primary"):
                go_to("Doctors")
                st.rerun()


def render_home() -> None:
    hero_image = asset_data_uri("hero_scene.svg")
    cta_image = asset_data_uri("cta_doctor.svg")
    left, right = st.columns([1.05, 0.95], gap="large", vertical_alignment="center")
    with left:
        st.markdown('<div class="badge">Trusted Healthcare Platform</div><div class="hero-title">Your Health, Our<br>Priority</div><div class="hero-copy">Experience modern healthcare with AI-powered symptom checking, easy doctor consultations, and 24/7 medical support, all in one platform.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Check Symptoms", key="hero_symptoms", use_container_width=True, type="primary"):
                go_to("Symptom Checker")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("Find a Doctor", key="hero_doctors", use_container_width=True, type="secondary"):
                go_to("Doctors")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown(f'<div class="hero-card"><img class="hero-image" src="{hero_image}" alt="Healthcare consultation visual"><div class="floating-doctors"><div class="pulse">+</div><div><div class="subtle">Available Now</div><div style="color:#2e82ea;font-weight:800;font-size:1.35rem;">200+ Doctors Online</div></div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-band"><div class="metric-inner"><div><div style="font-size:1.9rem;">O</div><div class="metric-value">50K+</div><div>Active Patients</div></div><div><div style="font-size:1.9rem;">U</div><div class="metric-value">200+</div><div>Certified Doctors</div></div><div><div style="font-size:1.9rem;">H</div><div class="metric-value">98%</div><div>Success Rate</div></div><div><div style="font-size:1.9rem;">+</div><div class="metric-value">15+</div><div>Countries</div></div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Why Choose HealthCare+</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">We combine cutting-edge technology with compassionate care to deliver the best healthcare experience.</div>', unsafe_allow_html=True)
    items = [("AI", "AI Symptom Checker", "Get instant insights about your symptoms with our intelligent chatbot assistant."), ("AP", "Easy Appointments", "Book consultations with top doctors at your convenience."), ("DR", "Expert Doctors", "Access a network of certified healthcare professionals."), ("24", "24/7 Support", "Round-the-clock medical assistance whenever you need it.")]
    for col, item in zip(st.columns(4), items):
        icon, title, copy = item
        with col:
            st.markdown(f'<div class="feature-card"><div class="feature-icon">{icon}</div><div class="feature-title">{title}</div><div class="feature-copy">{copy}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cta-panel"><div class="cta-copy-wrap"><div class="cta-title">Start Your Health Journey Today</div><div class="cta-copy">Join thousands of patients who trust us for their healthcare needs. Get started with our AI symptom checker or book an appointment now.</div></div><div class="cta-image"><img class="cta-real-image" src="{cta_image}" alt="Doctor visual"></div></div>', unsafe_allow_html=True)
    a1, a2, _ = st.columns([1.1, 1.1, 2.2])
    with a1:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Get Started", key="cta_get_started", use_container_width=True, type="secondary"):
            go_to("Symptom Checker")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with a2:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("View Doctors", key="cta_view_doctors", use_container_width=True, type="secondary"):
            go_to("Doctors")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_chat_messages() -> None:
    for item in st.session_state.chat_log:
        is_user = item["role"] == "user"
        row_class = "chat-row user" if is_user else "chat-row assistant"
        avatar = "U" if is_user else "AI"
        content = escape(item["content"]).replace("\n", "<br>")
        left_avatar = f'<div class="avatar">{avatar}</div>' if not is_user else ""
        right_avatar = f'<div class="avatar">{avatar}</div>' if is_user else ""
        st.markdown(f'<div class="{row_class}">{left_avatar}<div class="message-wrap"><div class="bubble">{content}</div><div class="bubble-time">{item["timestamp"]}</div></div>{right_avatar}</div>', unsafe_allow_html=True)
    if st.session_state.is_loading:
        st.markdown(
            '<div class="typing-row"><div class="avatar">AI</div><div class="typing-bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div></div>',
            unsafe_allow_html=True,
        )


def handle_chat_submission(user_text: str) -> None:
    text = user_text.strip()
    if not text:
        return
    log_message("user", text)
    st.session_state.is_loading = True
    try:
        if st.session_state.session_id:
            outcome = call_api("/chat/reply", {"session_id": st.session_state.session_id, "answer": text})
        else:
            outcome = call_api("/chat/start", {"message": text})
    except (error.URLError, error.HTTPError, TimeoutError, ValueError) as exc:
        st.session_state.api_error = (
            f"API connection failed or took too long. Check the FastAPI server at {API_BASE_URL}. Details: {exc}"
        )
        st.session_state.is_loading = False
        return

    st.session_state.api_error = None
    st.session_state.is_loading = False
    st.session_state.session_id = outcome.get("session_id")

    if outcome["stage"] == "interview":
        log_message("assistant", outcome["question"])
        st.session_state.latest_result = None
        return

    result = outcome["result"]
    st.session_state.session_id = None
    st.session_state.latest_result = result
    reply = result.get("advice") or result.get("note") or result.get("reason") or "Analysis complete."
    if result.get("status") == "doctor_required":
        reply = "Doctor intervention required. Medical attention is recommended."
    log_message("assistant", reply)


def render_result_panel() -> None:
    result = st.session_state.latest_result
    if not result:
        return
    st.markdown('<div class="result-panel">', unsafe_allow_html=True)
    if result.get("status") == "doctor_required":
        st.markdown('<div class="doctor-modal">', unsafe_allow_html=True)
        st.markdown('<div class="pill danger">MEDICAL ATTENTION REQUIRED</div>', unsafe_allow_html=True)
        st.markdown('<div class="doctor-modal-title">Doctor intervention required</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="doctor-modal-copy">Reason: {result.get("reason", "High-risk or uncertain case")}. '
            'Please connect with a qualified doctor for further evaluation.</div>',
            unsafe_allow_html=True,
        )
        if st.button("Connect to Doctor", key="connect_doctor", use_container_width=True, type="primary"):
            go_to("Doctors")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown('<div class="pill safe">SAFE GUIDANCE</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="result-grid">
                <div class="result-stat">
                    <div class="result-stat-label">Condition</div>
                    <div class="result-stat-value">{result.get('condition', 'Unknown')}</div>
                </div>
                <div class="result-stat">
                    <div class="result-stat-label">Risk Level</div>
                    <div class="result-stat-value">{result.get('risk_level', 'UNKNOWN')}</div>
                </div>
                <div class="result-stat">
                    <div class="result-stat-label">Confidence</div>
                    <div class="result-stat-value">{result.get('confidence', 0)}%</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        meds = result.get("medication") or []
        if meds:
            st.write(f"**Medication:** {', '.join(meds)}")
        st.write(f"**Advice:** {result.get('advice', 'Use only safe general care.')}")
        st.markdown(f'<div class="panel-muted">{result.get("note", "")}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_booking_panel() -> None:
    selected_index = st.session_state.selected_doctor_index
    if selected_index is None:
        return

    doctor = DOCTORS[selected_index]
    name, specialty, _, _, _, _, _, fee, _, _ = doctor
    _, center, _ = st.columns([0.9, 1.7, 0.9])
    with center:
        with st.container(border=True):
            st.markdown(f'<div class="booking-title">Book Appointment with {name}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="booking-subtitle">{specialty} - {fee} consultation fee</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="booking-strip">'
                '<div class="booking-pill">Preferred date</div>'
                '<div class="booking-pill">Preferred time</div>'
                '<div class="booking-pill">Consultation type</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            with st.form(f"booking_form_{selected_index}", clear_on_submit=False):
                c1, c2 = st.columns(2)
                with c1:
                    preferred_date = st.date_input("Preferred Date", min_value=datetime.now().date())
                with c2:
                    preferred_time = st.selectbox("Preferred Time", TIME_SLOTS, key=f"time_slot_{selected_index}")
                c3, c4 = st.columns([1.05, 1.35])
                with c3:
                    consultation_type = st.selectbox("Consultation Type", CONSULTATION_TYPES, key=f"consult_type_{selected_index}")
                with c4:
                    reason = st.text_area("Reason for Visit", placeholder="Briefly describe your health concern...", height=104, key=f"booking_reason_{selected_index}")
                a1, a2 = st.columns([1.2, 1])
                with a1:
                    confirm = st.form_submit_button("Confirm Booking", use_container_width=True, type="primary")
                with a2:
                    cancel = st.form_submit_button("Cancel", use_container_width=True, type="secondary")

                if confirm:
                    confirm_booking(doctor, preferred_date, preferred_time, consultation_type, reason)
                    st.rerun()
                if cancel:
                    cancel_booking()
                    st.rerun()


def render_recent_bookings() -> None:
    appointments = read_appointments()
    if not appointments:
        return

    st.markdown('<div class="recent-bookings">', unsafe_allow_html=True)
    st.markdown('<div class="recent-title">Recent Confirmed Bookings</div>', unsafe_allow_html=True)
    for appointment in reversed(appointments[-3:]):
        st.markdown(
            f'''
            <div class="recent-booking-row">
                <div>
                    <div style="font-weight:800;color:#22325d;">{escape(appointment["doctor_name"])}</div>
                    <div class="recent-meta">{escape(appointment["specialty"])} - {escape(appointment["consultation_type"])}</div>
                </div>
                <div class="recent-meta" style="text-align:right;">
                    {escape(appointment["preferred_date"])}<br>{escape(appointment["preferred_time"])}
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
def render_symptom_checker() -> None:
    st.markdown('<div class="page-shell">', unsafe_allow_html=True)
    st.markdown('<div class="page-title">AI Health Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Chat with our AI to understand your symptoms</div>', unsafe_allow_html=True)
    st.markdown('<div class="notice"><strong>Important:</strong> This AI assistant provides general health information only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical concerns.</div>', unsafe_allow_html=True)
    chat_box = st.container(border=True)
    with chat_box:
        render_chat_messages()
        st.divider()
        with st.form("chat_form", clear_on_submit=True):
            c1, c2 = st.columns([7.2, 1])
            with c1:
                user_text = st.text_input("Type your response", placeholder="Type your response...", label_visibility="collapsed")
            with c2:
                submitted = st.form_submit_button("Send", use_container_width=True, type="secondary")
            if submitted:
                handle_chat_submission(user_text)
                st.rerun()

        st.caption("Quick options:")
        options = get_quick_options()[:12]
        rows = [options[0:4], options[4:8], options[8:12]]
        for row_index, row in enumerate(rows):
            if not row:
                continue
            cols = st.columns(len(row))
            for idx, (col, option) in enumerate(zip(cols, row)):
                with col:
                    if st.button(option, key=f"quick_inline_{row_index}_{idx}_{option}", use_container_width=True, type="secondary"):
                        handle_chat_submission(option)
                        st.rerun()
    control_col1, control_col2 = st.columns([1, 1.3])
    with control_col1:
        if st.button("Restart Chat", key="restart_chat", use_container_width=True, type="secondary"):
            reset_chat()
            st.rerun()
    if st.session_state.api_error:
        st.error(st.session_state.api_error)
    render_result_panel()
    st.markdown('<div class="danger-banner"><strong>Emergency?</strong> If you are experiencing a medical emergency, call 911 or your local emergency services immediately.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def doctor_card(doctor: tuple[str, ...], index: int) -> None:
    name, specialty, rating, reviews, experience, location, mode, fee, availability, image_name = doctor
    image_uri = asset_data_uri(image_name)
    st.markdown(
        f'<div class="doctor-card"><div class="doctor-image"><img class="doctor-photo" src="{image_uri}" alt="{name}">'
        f'<div class="doctor-chip">{availability}</div></div><div class="doctor-content"><div class="doctor-name">{name}</div>'
        f'<div class="doctor-specialty">{specialty}</div><div class="doctor-meta"><span class="doctor-stat">Star {rating} ({reviews})</span>'
        f'<span class="doctor-stat">{experience}</span></div><div class="doctor-line">{location}</div>'
        f'<div class="doctor-mode">{mode}</div><div class="doctor-fee-row"><span>Consultation Fee</span><span class="fee-value">{fee}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="primary-btn" style="margin-top:14px;">', unsafe_allow_html=True)
    if st.button("Book Appointment", key=f"doctor_book_{index}", use_container_width=True, type="primary"):
        start_booking(index)
        st.rerun()
    st.markdown("</div></div></div>", unsafe_allow_html=True)


def render_doctors() -> None:
    st.markdown('<div class="doctor-page-shell">', unsafe_allow_html=True)
    st.markdown('<div class="doctor-page-top"><div class="doctor-page-copy"><div class="page-title">Find a Doctor</div><div class="page-subtitle">Book an appointment with our certified healthcare professionals</div></div></div>', unsafe_allow_html=True)
    with st.container(border=True):
        c1, c2 = st.columns([1.4, 1.2])
        with c1:
            st.markdown('<div class="input-label">Search Doctors</div>', unsafe_allow_html=True)
            search = st.text_input("Search doctors", placeholder="Search by name or specialty...", label_visibility="collapsed").strip().lower()
        with c2:
            st.markdown('<div class="input-label">Specialty</div>', unsafe_allow_html=True)
            specialty = st.selectbox("Specialty", ["All Specialties", "Cardiologist", "Pediatrician", "Dermatologist", "General Physician", "Neurologist", "Orthopedic"], label_visibility="collapsed")
    filtered = []
    for doctor_index, doctor in enumerate(DOCTORS):
        name, doc_specialty = doctor[0], doctor[1]
        if (not search or search in name.lower() or search in doc_specialty.lower()) and (specialty == "All Specialties" or specialty == doc_specialty):
            filtered.append((doctor_index, doctor))
    st.markdown(f'<div class="subtle" style="margin-bottom:14px;">Showing {len(filtered)} doctors</div>', unsafe_allow_html=True)
    if st.session_state.booking_notice:
        st.success(st.session_state.booking_notice)
    render_booking_panel()
    for start in range(0, len(filtered), 3):
        cols = st.columns(3)
        for col_idx, booking_item in enumerate(filtered[start:start + 3]):
            doctor_index, doctor = booking_item
            with cols[col_idx]:
                doctor_card(doctor, doctor_index)
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    init_state()
    render_styles()
    render_navbar()
    if st.session_state.page == "Home":
        render_home()
    elif st.session_state.page == "Symptom Checker":
        render_symptom_checker()
    else:
        render_doctors()


if __name__ == "__main__":
    main()
