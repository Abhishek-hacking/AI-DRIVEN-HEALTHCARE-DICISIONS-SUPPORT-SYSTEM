from __future__ import annotations

import json
import os
from datetime import datetime
from html import escape
from urllib import error, request

import streamlit as st

DOCTORS = [
    ("Dr. Sarah Johnson", "Cardiologist", "4.9", "127", "15+ years", "New York, NY", "Video & In-person consultations", "$150", "Available Today", "linear-gradient(135deg,#33231d,#72584c,#f1ebe6)"),
    ("Dr. Michael Chen", "Pediatrician", "4.8", "98", "12+ years", "San Francisco, CA", "Video & In-person consultations", "$120", "Available Tomorrow", "linear-gradient(135deg,#99673b,#d2b085,#3b8ede)"),
    ("Dr. Emily Rodriguez", "Dermatologist", "4.9", "156", "10+ years", "Los Angeles, CA", "Video & In-person consultations", "$130", "Available Today", "linear-gradient(135deg,#e0e6ee,#afc0d4,#596f92)"),
    ("Dr. James Patel", "General Physician", "4.7", "84", "9+ years", "Chicago, IL", "Video consultations", "$90", "Available Today", "linear-gradient(135deg,#7bb4d7,#f1f7ff,#7ca1c7)"),
    ("Dr. Priya Nair", "Neurologist", "4.9", "112", "14+ years", "Seattle, WA", "Video & In-person consultations", "$180", "Available Tomorrow", "linear-gradient(135deg,#4d4a55,#847a88,#e5e0db)"),
    ("Dr. Robert Kim", "Orthopedic", "4.8", "103", "11+ years", "Austin, TX", "In-person consultations", "$140", "Available Today", "linear-gradient(135deg,#cfd5de,#eef3f8,#6784a5)"),
]

QUICK_OPTIONS = ["Headache", "Fever", "Cough", "Stomach pain"]
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
    st.session_state.setdefault("session_id", None)
    st.session_state.setdefault("api_error", None)


def go_to(page: str) -> None:
    st.session_state.page = page


def reset_chat() -> None:
    st.session_state.chat_log = [welcome_message()]
    st.session_state.latest_result = None
    st.session_state.session_id = None
    st.session_state.api_error = None


def log_message(role: str, content: str) -> None:
    st.session_state.chat_log.append({"role": role, "content": content, "timestamp": now_text()})


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
        .nav-shell{background:rgba(255,255,255,.94);border:1px solid rgba(219,230,243,.85);border-radius:20px;backdrop-filter:blur(10px);box-shadow:0 12px 28px rgba(19,50,94,.06);padding:10px 16px;margin-bottom:10px}
        .brand{display:flex;align-items:center;gap:12px;font-weight:700;color:var(--blue);font-size:1.05rem}.brand-mark{width:38px;height:38px;border-radius:12px;display:inline-flex;align-items:center;justify-content:center;background:var(--blue);color:#fff;font-weight:800}
        .badge{display:inline-flex;align-items:center;gap:8px;background:#eef5ff;color:#3c82dd;border-radius:999px;padding:8px 14px;font-size:.88rem;margin-bottom:12px}
        .hero-title{font-size:clamp(2.7rem,5vw,4.4rem);line-height:1.04;letter-spacing:-.05em;font-weight:800;color:#1f2750;margin:0 0 12px}.hero-copy{color:var(--muted);font-size:1.03rem;line-height:1.65;max-width:560px}
        .hero-card{position:relative;min-height:410px;border-radius:26px;overflow:hidden;box-shadow:var(--shadow);background:linear-gradient(120deg,rgba(17,44,78,.70),rgba(17,44,78,.05) 36%),radial-gradient(circle at 15% 20%,rgba(148,196,160,.50),transparent 16%),radial-gradient(circle at 82% 14%,rgba(255,255,255,.85),transparent 14%),linear-gradient(135deg,#4c6461 0%,#95a4a3 38%,#f6f8f9 100%)}
        .hero-card:before{content:"";position:absolute;inset:18% 12% 18% 20%;border-radius:20px;background:linear-gradient(180deg,rgba(255,255,255,.92),rgba(233,241,248,.92));box-shadow:0 24px 32px rgba(10,33,68,.18);transform:perspective(900px) rotateY(-14deg) rotateX(5deg)}
        .floating-doctors{position:absolute;left:-24px;bottom:22px;background:rgba(255,255,255,.98);border-radius:20px;box-shadow:0 18px 40px rgba(25,61,114,.18);padding:16px 18px;display:flex;align-items:center;gap:14px;min-width:245px}
        .pulse{width:54px;height:54px;border-radius:50%;background:#e7fff0;color:#1ca05c;display:inline-flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:700}
        .metric-band{background:var(--blue);margin:22px calc(50% - 50vw) 0;padding:22px 0 24px}.metric-inner{max-width:1140px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:14px;color:#fff;text-align:center}.metric-value{font-size:2rem;font-weight:800;margin-top:6px}
        .section-title{text-align:center;font-size:clamp(2rem,3.4vw,3rem);color:#17244f;font-weight:800;letter-spacing:-.04em;margin:44px 0 8px}.section-copy{text-align:center;color:var(--muted);max-width:760px;margin:0 auto 26px;font-size:1.02rem;line-height:1.6}
        .feature-card,.search-panel,.doctor-card,.chat-shell,.result-panel{border:1px solid var(--line);background:#fff;border-radius:24px;box-shadow:0 12px 28px rgba(19,50,94,.05)}.feature-card{padding:20px;min-height:190px}.feature-icon{width:42px;height:42px;border-radius:14px;background:#eaf2ff;color:var(--blue);display:inline-flex;align-items:center;justify-content:center;font-size:1.05rem;margin-bottom:16px}.feature-title{font-weight:800;color:#23345c;font-size:1.1rem;margin-bottom:10px}.feature-copy,.panel-muted,.page-subtitle,.doctor-specialty,.doctor-line,.doctor-meta,.doctor-mode,.doctor-fee-row,.subtle{color:var(--muted);line-height:1.55}
        .cta-panel{display:grid;grid-template-columns:1fr 1fr;margin-top:36px;background:var(--blue);border-radius:26px;overflow:hidden;box-shadow:var(--shadow)}.cta-copy-wrap{padding:42px 30px;color:#fff}.cta-title{font-size:2.2rem;font-weight:800;letter-spacing:-.04em;margin-bottom:12px}.cta-copy{opacity:.92;line-height:1.65}.cta-image{min-height:360px;background:radial-gradient(circle at 38% 28%,rgba(46,109,232,.8),transparent 7%),radial-gradient(circle at 40% 28%,rgba(255,255,255,.92),transparent 2.8%),linear-gradient(90deg,#f8fbff 0%,#eef4fb 40%,#fff 100%);position:relative}.cta-image:before{content:"";position:absolute;right:22%;top:8%;width:46%;height:86%;border-radius:36px 36px 18px 18px;background:linear-gradient(180deg,#fff 0%,#fbfdff 55%,#eef3fa 100%);box-shadow:0 26px 40px rgba(19,50,94,.10)}.cta-image:after{content:"";position:absolute;right:37%;top:13%;width:18%;height:24%;border-radius:0 0 50% 50%;background:linear-gradient(180deg,#4278de 0%,#8ab2ff 100%)}
        .page-title{font-size:2.8rem;font-weight:800;color:#1d284c;margin:4px 0 6px;letter-spacing:-.04em}.notice{border:1px solid #bfdaff;background:#f1f7ff;color:#38558d;border-radius:18px;padding:14px 18px;margin-bottom:12px;line-height:1.55}
        .chat-body{min-height:360px;max-height:360px;overflow-y:auto;padding:16px 16px 10px;background:linear-gradient(180deg,#fff 0%,#fdfefe 100%)}.chat-row{display:flex;align-items:flex-start;gap:10px;margin-bottom:12px}.chat-row.user{justify-content:flex-end}.avatar{width:36px;height:36px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;background:var(--blue);color:#fff;font-size:.9rem;flex:0 0 auto}.bubble{max-width:72%;border:1px solid var(--line);background:#fff;border-radius:18px;padding:12px 14px;color:#28365d;line-height:1.6;white-space:pre-wrap}.chat-row.user .bubble{background:linear-gradient(135deg,#1d73d3,#1668c7);color:#fff;border-color:transparent}.bubble-time{font-size:.78rem;color:#98a6c4;margin-top:4px}
        .quick-strip{border-top:1px solid var(--line);padding:10px 14px;background:#fbfdff}.composer-wrap{border-top:1px solid var(--line);padding:8px 14px;background:#fff}.danger-banner{margin-top:10px;border:1px solid #ffcbcb;background:#fff0f0;color:#9f2c2c;border-radius:16px;padding:12px 14px;line-height:1.5}.result-panel{margin-top:10px;padding:14px}.pill{display:inline-flex;align-items:center;border-radius:999px;padding:7px 12px;font-size:.82rem;font-weight:800;letter-spacing:.05em;margin-bottom:10px}.pill.safe{background:#edfdf4;color:#1f9d62}.pill.danger{background:#fff0f0;color:#c83f3f}
        .search-panel{padding:16px;margin-bottom:14px}.doctor-card{overflow:hidden;min-height:470px}.doctor-image{height:170px;position:relative}.doctor-chip{position:absolute;top:12px;right:12px;background:#fff;color:#5a6b90;border-radius:999px;padding:6px 10px;font-size:.76rem;font-weight:700;box-shadow:0 8px 20px rgba(19,50,94,.10)}.doctor-content{padding:16px 18px 18px}.doctor-name{font-size:1.18rem;color:#22325d;font-weight:800;margin-bottom:6px}.doctor-meta{display:flex;gap:14px;flex-wrap:wrap;margin-top:12px}.doctor-mode{margin-top:6px;padding-bottom:8px;border-bottom:1px solid #e7eef8}.doctor-fee-row{display:flex;justify-content:space-between;align-items:center;margin-top:8px;font-size:1rem}.fee-value{color:#2d82eb;font-weight:800;font-size:1.1rem}
        .stButton{margin:0}.stButton button{width:100%;border-radius:12px;border:1px solid #d7e4f6;padding:.58rem .95rem;font-weight:700;box-shadow:none;background:#ffffff;color:#23345c}
        .stButton button[kind="primary"]{background:var(--blue)!important;color:#fff!important;border-color:var(--blue)!important}
        .stButton button[kind="secondary"]{background:#fff!important;color:#23345c!important;border-color:#d7e4f6!important}
        .stButton button:hover{border-color:#bcd2ef!important;color:#1668c7!important}
        .stButton button[kind="primary"]:hover{background:#0f56a6!important;color:#fff!important;border-color:#0f56a6!important}
        [data-testid="column"]{padding-top:0!important}
        div[data-testid="stHorizontalBlock"]{gap:.85rem}
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
        div[data-testid="stForm"] button[kind="secondary"]{
            background:var(--blue)!important;
            color:#ffffff!important;
            border-color:var(--blue)!important;
        }
        div[data-testid="stSelectbox"]>div{border-radius:12px}
        @media (max-width:900px){.metric-inner{grid-template-columns:repeat(2,1fr)}.cta-panel{grid-template-columns:1fr}.bubble{max-width:88%}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_navbar() -> None:
    st.markdown('<div class="nav-shell">', unsafe_allow_html=True)
    left, mid, right = st.columns([1.4, 1.8, 1.1], vertical_alignment="center")
    with left:
        st.markdown('<div class="brand"><span class="brand-mark">+</span><span>HealthCare+</span></div>', unsafe_allow_html=True)
    with mid:
        for col, page in zip(st.columns(3), ["Home", "Symptom Checker", "Doctors"]):
            with col:
                css = "flat-btn active" if st.session_state.page == page else "flat-btn"
                st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
                if st.button(page, key=f"nav_{page}", use_container_width=True, type="secondary"):
                    go_to(page)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
        if st.button("Book Appointment", key="book_top", use_container_width=True, type="primary"):
            go_to("Doctors")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_home() -> None:
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
        st.markdown('<div class="hero-card"><div class="floating-doctors"><div class="pulse">+</div><div><div class="subtle">Available Now</div><div style="color:#2e82ea;font-weight:800;font-size:1.35rem;">200+ Doctors Online</div></div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-band"><div class="metric-inner"><div><div style="font-size:1.9rem;">O</div><div class="metric-value">50K+</div><div>Active Patients</div></div><div><div style="font-size:1.9rem;">U</div><div class="metric-value">200+</div><div>Certified Doctors</div></div><div><div style="font-size:1.9rem;">H</div><div class="metric-value">98%</div><div>Success Rate</div></div><div><div style="font-size:1.9rem;">+</div><div class="metric-value">15+</div><div>Countries</div></div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Why Choose HealthCare+</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">We combine cutting-edge technology with compassionate care to deliver the best healthcare experience.</div>', unsafe_allow_html=True)
    items = [("AI", "AI Symptom Checker", "Get instant insights about your symptoms with our intelligent chatbot assistant."), ("AP", "Easy Appointments", "Book consultations with top doctors at your convenience."), ("DR", "Expert Doctors", "Access a network of certified healthcare professionals."), ("24", "24/7 Support", "Round-the-clock medical assistance whenever you need it.")]
    for col, item in zip(st.columns(4), items):
        icon, title, copy = item
        with col:
            st.markdown(f'<div class="feature-card"><div class="feature-icon">{icon}</div><div class="feature-title">{title}</div><div class="feature-copy">{copy}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="cta-panel"><div class="cta-copy-wrap"><div class="cta-title">Start Your Health Journey Today</div><div class="cta-copy">Join thousands of patients who trust us for their healthcare needs. Get started with our AI symptom checker or book an appointment now.</div></div><div class="cta-image"></div></div>', unsafe_allow_html=True)
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
    st.markdown('<div class="chat-body">', unsafe_allow_html=True)
    for item in st.session_state.chat_log:
        is_user = item["role"] == "user"
        row_class = "chat-row user" if is_user else "chat-row assistant"
        avatar = "U" if is_user else "AI"
        content = escape(item["content"]).replace("\n", "<br>")
        left_avatar = f'<div class="avatar">{avatar}</div>' if not is_user else ""
        right_avatar = f'<div class="avatar">{avatar}</div>' if is_user else ""
        st.markdown(f'<div class="{row_class}">{left_avatar}<div><div class="bubble">{content}</div><div class="bubble-time">{item["timestamp"]}</div></div>{right_avatar}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def handle_chat_submission(user_text: str) -> None:
    text = user_text.strip()
    if not text:
        return
    log_message("user", text)
    try:
        if st.session_state.session_id:
            outcome = call_api("/chat/reply", {"session_id": st.session_state.session_id, "answer": text})
        else:
            outcome = call_api("/chat/start", {"message": text})
    except (error.URLError, error.HTTPError, TimeoutError, ValueError) as exc:
        st.session_state.api_error = (
            f"API connection failed or took too long. Check the FastAPI server at {API_BASE_URL}. Details: {exc}"
        )
        return

    st.session_state.api_error = None
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
        st.markdown('<div class="pill danger">EMERGENCY REVIEW</div>', unsafe_allow_html=True)
        st.markdown("**Medical attention required**")
        st.write("Doctor intervention required.")
        st.markdown(f'<div class="panel-muted">Reason: {result.get("reason", "High-risk or uncertain case")}</div>', unsafe_allow_html=True)
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        st.button("Connect to Doctor", key="connect_doctor", use_container_width=True, type="primary")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown('<div class="pill safe">SAFE GUIDANCE</div>', unsafe_allow_html=True)
        st.markdown(f"**Condition:** {result.get('condition', 'Unknown')}")
        st.markdown(f"**Risk Level:** {result.get('risk_level', 'UNKNOWN')}")
        st.markdown(f"**Confidence:** {result.get('confidence', 0)}%")
        meds = result.get("medication") or []
        if meds:
            st.write(f"**Medication:** {', '.join(meds)}")
        st.write(f"**Advice:** {result.get('advice', 'Use only safe general care.')}")
        st.markdown(f'<div class="panel-muted">{result.get("note", "")}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_symptom_checker() -> None:
    st.markdown('<div class="page-title">AI Health Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Chat with our AI to understand your symptoms</div>', unsafe_allow_html=True)
    st.markdown('<div class="notice"><strong>Important:</strong> This AI assistant provides general health information only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical concerns.</div>', unsafe_allow_html=True)
    _, right = st.columns([4.2, 1])
    with right:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Restart Chat", key="restart_chat", use_container_width=True, type="secondary"):
            reset_chat()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="chat-shell">', unsafe_allow_html=True)
    render_chat_messages()
    st.markdown('<div class="quick-strip"><div class="subtle" style="margin-bottom:10px;">Quick options:</div>', unsafe_allow_html=True)
    for col, option in zip(st.columns(4), QUICK_OPTIONS):
        with col:
            st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
            if st.button(option, key=f"quick_{option}", use_container_width=True, type="secondary"):
                handle_chat_submission(option)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="composer-wrap">', unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([6.6, 1])
        with c1:
            user_text = st.text_input("Type your response", placeholder="Type your response...", label_visibility="collapsed")
        with c2:
            submitted = st.form_submit_button("Send", use_container_width=True, type="secondary")
        if submitted:
            handle_chat_submission(user_text)
            st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)
    if st.session_state.api_error:
        st.error(st.session_state.api_error)
    render_result_panel()
    st.markdown('<div class="danger-banner"><strong>Emergency?</strong> If you are experiencing a medical emergency, call 911 or your local emergency services immediately.</div>', unsafe_allow_html=True)


def doctor_card(doctor: tuple[str, ...], index: int) -> None:
    name, specialty, rating, reviews, experience, location, mode, fee, availability, accent = doctor
    st.markdown(f'<div class="doctor-card"><div class="doctor-image" style="background:{accent};"><div class="doctor-chip">{availability}</div></div><div class="doctor-content"><div class="doctor-name">{name}</div><div class="doctor-specialty">{specialty}</div><div class="doctor-meta"><span>Star {rating} ({reviews})</span><span>{experience}</span></div><div class="doctor-line" style="margin-top:8px;">{location}</div><div class="doctor-mode">{mode}</div><div class="doctor-fee-row"><span>Consultation Fee</span><span class="fee-value">{fee}</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="primary-btn" style="margin-top:14px;">', unsafe_allow_html=True)
    if st.button("Book Appointment", key=f"doctor_book_{index}", use_container_width=True, type="primary"):
        st.session_state.booked_doctor = name
    st.markdown("</div></div></div>", unsafe_allow_html=True)


def render_doctors() -> None:
    st.markdown('<div class="page-title">Find a Doctor</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Book an appointment with our certified healthcare professionals</div>', unsafe_allow_html=True)
    st.markdown('<div class="search-panel">', unsafe_allow_html=True)
    c1, c2 = st.columns([1.4, 1.2])
    with c1:
        st.markdown('<div class="input-label">Search Doctors</div>', unsafe_allow_html=True)
        search = st.text_input("Search doctors", placeholder="Search by name or specialty...", label_visibility="collapsed").strip().lower()
    with c2:
        st.markdown('<div class="input-label">Specialty</div>', unsafe_allow_html=True)
        specialty = st.selectbox("Specialty", ["All Specialties", "Cardiologist", "Pediatrician", "Dermatologist", "General Physician", "Neurologist", "Orthopedic"], label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    filtered = []
    for doctor in DOCTORS:
        name, doc_specialty = doctor[0], doctor[1]
        if (not search or search in name.lower() or search in doc_specialty.lower()) and (specialty == "All Specialties" or specialty == doc_specialty):
            filtered.append(doctor)
    st.markdown(f'<div class="subtle" style="margin-bottom:14px;">Showing {len(filtered)} doctors</div>', unsafe_allow_html=True)
    if st.session_state.booked_doctor:
        st.success(f"Appointment request started for {st.session_state.booked_doctor}.")
    for start in range(0, len(filtered), 3):
        cols = st.columns(3)
        for idx, doctor in enumerate(filtered[start:start + 3], start=start):
            with cols[idx - start]:
                doctor_card(doctor, idx)


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
