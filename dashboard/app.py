import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
from core.database import get_ledger_dataframe, CAMPUS_DEPARTMENTS
from dashboard.voice_agent import answer_campus_query

st.set_page_config(
    page_title="CampusOS | Executive AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional Header & Card Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* Top padding so header never gets cut off */
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 1280px;
    }

    /* Top Stat Cards */
    .stat-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .stat-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 18px 22px;
        backdrop-filter: blur(14px);
        box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.4);
    }
    .stat-label {
        font-size: 0.72rem;
        color: #94a3b8;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .stat-value {
        font-size: 1.65rem;
        color: #f8fafc;
        font-weight: 800;
        margin-top: 4px;
    }

    /* Department Cards */
    div.stButton > button {
        width: 100% !important;
        min-height: 130px !important;
        background: linear-gradient(145deg, #111827 0%, #0b0f19 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 18px !important;
        padding: 18px 16px !important;
        text-align: left !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        align-items: flex-start !important;
        box-shadow: 0 8px 22px -5px rgba(0, 0, 0, 0.5) !important;
        transition: all 0.22s ease-in-out !important;
        margin-bottom: 14px !important;
    }
    div.stButton > button:hover {
        border-color: #6366f1 !important;
        transform: translateY(-3px) !important;
        background: linear-gradient(145deg, #1e1b4b 0%, #0f172a 100%) !important;
        box-shadow: 0 14px 30px -6px rgba(99, 102, 241, 0.35) !important;
    }
    div.stButton > button p {
        white-space: pre-line !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        color: #f8fafc !important;
        line-height: 1.45 !important;
        margin: 0 !important;
    }
    div.stButton > button p strong {
        display: block !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        line-height: 1.35 !important;
        margin-bottom: 8px !important;
    }

    /* Cute Compact Back Button */
    div.back-btn-box button {
        min-height: 34px !important;
        height: 34px !important;
        padding: 2px 14px !important;
        border-radius: 20px !important;
        background: rgba(99, 102, 241, 0.18) !important;
        border: 1px solid rgba(99, 102, 241, 0.45) !important;
        color: #c7d2fe !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        width: auto !important;
    }
    div.back-btn-box button:hover {
        background: #6366f1 !important;
        color: #ffffff !important;
        border-color: #818cf8 !important;
    }
    div.back-btn-box button p {
        font-size: 0.8rem !important;
    }

    .ai-bubble {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.85));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-left: 5px solid #6366f1;
        border-radius: 16px;
        padding: 20px 24px;
        margin-top: 16px;
        color: #f1f5f9;
        line-height: 1.65;
        box-shadow: 0 10px 28px -8px rgba(0, 0, 0, 0.45);
    }

    /* Mobile media query: 2 cards per row on mobile phones */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 2.8rem !important;
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
        }
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            width: calc(50% - 8px) !important;
            flex: 0 0 calc(50% - 8px) !important;
            min-width: calc(50% - 8px) !important;
        }
        div.stButton > button {
            min-height: 120px !important;
            padding: 12px 10px !important;
        }
        div.stButton > button p {
            font-size: 0.72rem !important;
        }
        div.stButton > button p strong {
            font-size: 0.9rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

if "selected_department" not in st.session_state:
    st.session_state.selected_department = "Overview"

# Read recognized speech from query param
voice_input_param = st.query_params.get("voice_q", "")
voice_query_active = bool(voice_input_param)
if voice_input_param:
    default_query_text = voice_input_param
    st.query_params.clear()
else:
    default_query_text = ""

df_all = get_ledger_dataframe("All")

DEPT_ICONS = {
    "Admissions": "🎓",
    "Accounts & Finance": "💳",
    "Examination Branch": "📑",
    "Academic & Certificates": "📜",
    "Training & Placement": "💼",
    "Human Resources (HR)": "👥",
    "Library": "📚",
    "Campus Facilities & Transport": "🚌",
    "Accreditation & Compliance (IQAC)": "🛡️",
    "General Administration": "🏛️"
}

# --- UNIFIED PARALLEL HEADER BAR ---
st.markdown("""
<style>
    /* Keep the navigation button compact and aligned to the header's right edge. */
    .st-key-header-nav {
        display: flex !important;
        justify-content: flex-end !important;
        width: 100% !important;
    }
    .st-key-header-nav div.stButton {
        display: flex !important;
        justify-content: flex-end !important;
        width: auto !important;
        margin-left: auto !important;
    }
    .st-key-header-nav div.stButton > button {
        all: unset !important;
        box-sizing: border-box !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        padding: 0 16px !important;
        border-radius: 18px !important;
        background: rgba(99, 102, 241, 0.22) !important;
        border: 1px solid rgba(99, 102, 241, 0.5) !important;
        color: #c7d2fe !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        cursor: pointer !important;
        box-shadow: none !important;
        margin-left: auto !important;
    }
    .st-key-header-nav div.stButton > button:hover {
        background: #6366f1 !important;
        color: #ffffff !important;
        border-color: #818cf8 !important;
    }
    .st-key-header-nav div.stButton > button p {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        color: inherit !important;
        line-height: 1 !important;
        white-space: nowrap !important;
    }
    .st-key-refresh-records {
        display: flex !important;
        justify-content: flex-start !important;
        width: 100% !important;
    }
    .st-key-refresh-records div.stButton {
        width: auto !important;
    }
    .st-key-refresh-records div.stButton > button {
        all: unset !important;
        box-sizing: border-box !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: auto !important;
        min-width: 0 !important;
        height: 36px !important;
        min-height: 36px !important;
        padding: 0 16px !important;
        border-radius: 18px !important;
        background: rgba(99, 102, 241, 0.18) !important;
        border: 1px solid rgba(99, 102, 241, 0.45) !important;
        color: #c7d2fe !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        cursor: pointer !important;
        box-shadow: none !important;
    }
    .st-key-refresh-records div.stButton > button:hover {
        background: #6366f1 !important;
        color: #ffffff !important;
        border-color: #818cf8 !important;
    }
    .st-key-refresh-records div.stButton > button p {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
        color: inherit !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        white-space: nowrap !important;
    }
    @media (max-width: 768px) {
        .st-key-header-nav div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            gap: 8px !important;
        }
        .st-key-header-nav div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {
            flex: 1 1 auto !important;
            width: auto !important;
            min-width: 0 !important;
        }
        .st-key-header-nav div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child {
            flex: 0 0 88px !important;
            width: 88px !important;
            min-width: 88px !important;
        }
        .st-key-header-nav div.stButton > button {
            padding: 0 10px !important;
            font-size: 0.78rem !important;
        }
        .st-key-refresh-records div.stButton > button {
            height: 34px !important;
            min-height: 34px !important;
            padding: 0 12px !important;
            font-size: 0.76rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

header_nav = st.container(key="header-nav")
head_col1, head_col2 = header_nav.columns([5.2, 1], vertical_alignment="center")

with head_col1:
    st.markdown("""
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:nowrap;">
            <span style="font-size:1.45rem; font-weight:800; color:#f8fafc; line-height:1;">⚡ CampusOS</span>
            <span style="font-size:0.68rem; color:#818cf8; font-weight:700; padding:2px 6px; border-radius:6px; background:rgba(99,102,241,0.15);">ENTERPRISE</span>
        </div>
        <div style="font-size:0.8rem; color:#94a3b8; margin-top:3px;">
            Multimodal Vision Governance & Executive Intelligence Architecture
        </div>
    """, unsafe_allow_html=True)

with head_col2:
    if st.session_state.selected_department != "Overview":
        st.markdown('<div class="cute-nav-btn">', unsafe_allow_html=True)
        if st.button("← Back", key="cute_back_btn"):
            st.session_state.selected_department = "Overview"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# =========================================================
# VIEW 1: OVERVIEW DASHBOARD
# =========================================================
if st.session_state.selected_department == "Overview":

    total_scans = len(df_all)
    approved_scans = len(df_all[df_all["Status"] == "Approved"]) if not df_all.empty else 0
    total_rev = df_all[(df_all["Category"] == "Accounts & Finance") & (df_all["Status"] == "Approved")]["Amount (INR)"].sum() if not df_all.empty else 0.0

    st.markdown(f"""
    <div class="stat-container">
        <div class="stat-box">
            <div class="stat-label">Total Documents Processed</div>
            <div class="stat-value">{total_scans}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Verified & Approved</div>
            <div class="stat-value" style="color:#34d399;">{approved_scans}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Accounts Reconciliation</div>
            <div class="stat-value" style="color:#60a5fa;">₹{total_rev:,.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='color:#cbd5e1; margin-top:8px; margin-bottom:14px; font-weight:700;'>Campus Department Modules</h4>", unsafe_allow_html=True)

    # 4 cards per row for Web Desktop, Mobile gets 2 per row
    row1 = st.columns(4)
    row2 = st.columns(4)
    row3 = st.columns(4)
    grid_slots = row1 + row2 + row3

    for idx, dept in enumerate(CAMPUS_DEPARTMENTS):
        icon = DEPT_ICONS.get(dept, "📁")
        dept_df = df_all[df_all["Category"] == dept]
        records_count = len(dept_df)

        card_title = f"**{icon}  {dept}**\n\n📊 {records_count} Records"

        with grid_slots[idx]:
            if st.button(card_title, key=f"dept_btn_{idx}", use_container_width=True):
                st.session_state.selected_department = dept
                st.rerun()

    st.markdown("<div style='margin-top:22px;'></div>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#cbd5e1; margin-bottom:4px; font-weight:700;'>🔍 Global Campus Intelligence Desk</h4>", unsafe_allow_html=True)
    st.caption("Click microphone to speak your question, or type manually, then click '⚡ Get Answer':")

    mic_html = """
    <div style="display:flex; align-items:center; gap:12px; background:#0f172a; padding:12px 16px; border-radius:14px; border:1px solid #334155; margin-bottom:10px;">
        <button id="micBtn" onclick="runSpeech()" style="background:#6366f1; border:none; border-radius:50%; width:44px; height:44px; font-size:19px; color:white; cursor:pointer; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
            🎙️
        </button>
        <span id="micLabel" style="font-size:0.92rem; color:#94a3b8; font-weight:500;">Tap mic to speak your question...</span>
    </div>
    <script>
    function runSpeech() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Speech recognition browser lo support ledhu. Chrome/Edge use cheyandi.');
            return;
        }
        var SRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        var rec = new SRec();
        rec.lang = 'en-IN';
        rec.interimResults = false;
        rec.maxAlternatives = 1;

        document.getElementById('micBtn').style.background = '#ef4444';
        document.getElementById('micLabel').innerText = 'Listening... Speak now';
        document.getElementById('micLabel').style.color = '#ef4444';

        rec.onresult = function(e) {
            var text = e.results[0][0].transcript;
            document.getElementById('micLabel').innerText = 'Recognized: "' + text + '"';
            document.getElementById('micLabel').style.color = '#34d399';

            fillAndSubmitQuery(text);
        };
        function fillAndSubmitQuery(text) {
            try {
                var parentDoc = window.parent.document;
                var input = parentDoc.querySelector('input[placeholder*="Spoken text"]');
                if (!input) return;
                var setter = Object.getOwnPropertyDescriptor(
                    window.parent.HTMLInputElement.prototype, 'value'
                ).set;
                setter.call(input, text);
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                setTimeout(function() {
                    var buttons = parentDoc.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        if (buttons[i].innerText.indexOf('Get Answer') !== -1) {
                            buttons[i].click();
                            break;
                        }
                    }
                }, 150);
            } catch(err) {
                document.getElementById('micLabel').innerText = 'Voice captured. Click Get Answer.';
            }
        }
        rec.onerror = function(e) {
            document.getElementById('micBtn').style.background = '#6366f1';
            var errorText = e.error === 'no-speech'
                ? 'No speech detected. Tap the mic and speak clearly.'
                : e.error === 'not-allowed'
                ? 'Microphone blocked. Allow microphone for localhost, then try again.'
                : e.error === 'audio-capture'
                    ? 'No microphone found or it is busy.'
                    : 'Speech error: ' + (e.error || 'unknown error');
            document.getElementById('micLabel').innerText = errorText;
            document.getElementById('micLabel').style.color = '#ef4444';
        };
        rec.onend = function() {
            document.getElementById('micBtn').style.background = '#6366f1';
        };
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(function(stream) {
                stream.getTracks().forEach(function(track) { track.stop(); });
                rec.start();
            })
            .catch(function() {
                document.getElementById('micBtn').style.background = '#6366f1';
                document.getElementById('micLabel').innerText = 'Microphone blocked. Allow it in browser site settings.';
                document.getElementById('micLabel').style.color = '#ef4444';
            });
    }
    </script>
    """
    st.components.v1.html(mic_html, height=72)

    with st.form("global_search_form"):
        col_text, col_btn = st.columns([3.8, 1.2])
        with col_text:
            query_val = st.text_input(
                "Query",
                value=default_query_text,
                placeholder="Spoken text appears here, or type...",
                label_visibility="collapsed"
            )
        with col_btn:
            submit_run = st.form_submit_button("⚡ Get Answer", use_container_width=True)

    if (submit_run or voice_query_active) and query_val:
        with st.spinner("Analyzing ledger records..."):
            ans = answer_campus_query(query_val, module_scope="All")
            st.markdown(f"""
            <div class="ai-bubble">
                <span style="font-size:0.75rem; color:#818cf8; font-weight:800; text-transform:uppercase; letter-spacing:0.05em;">AI Executive Insight</span>
                <div style="margin-top:8px; font-size:1.02rem;">{ans}</div>
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# VIEW 2: DEPARTMENT MODULE CONSOLE
# =========================================================
else:
    active_dept = st.session_state.selected_department
    df_dept = get_ledger_dataframe(active_dept)
    icon = DEPT_ICONS.get(active_dept, "🏢")

    total_dept_items = len(df_dept)
    approved_dept_items = len(df_dept[df_dept["Status"] == "Approved"]) if not df_dept.empty else 0

    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #1e1e38 0%, #0f172a 100%); border:1px solid #312e81; border-radius:18px; padding:22px; margin-bottom:18px;">
        <div style="font-size:1.5rem; font-weight:800; color:#f8fafc; display:flex; align-items:center; gap:12px;">
            <span>{icon}</span> {active_dept}
        </div>
        <p style="color:#94a3b8; font-size:0.9rem; margin-top:6px; margin-bottom:16px;">
            Verified records and isolated intelligence for {active_dept}.
        </p>
        <div style="display:flex; gap:14px; flex-wrap:wrap;">
            <div style="background:rgba(255,255,255,0.06); padding:10px 18px; border-radius:12px; border:1px solid rgba(255,255,255,0.1);">
                <span style="font-size:0.72rem; color:#94a3b8; font-weight:700;">LOGGED RECORDS</span><br>
                <b style="font-size:1.2rem; color:#f8fafc;">{total_dept_items}</b>
            </div>
            <div style="background:rgba(255,255,255,0.06); padding:10px 18px; border-radius:12px; border:1px solid rgba(255,255,255,0.1);">
                <span style="font-size:0.72rem; color:#94a3b8; font-weight:700;">VERIFIED & ACTIVE</span><br>
                <b style="font-size:1.2rem; color:#34d399;">{approved_dept_items}</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_desk, tab_ledger = st.tabs(["🔍 Department AI Desk", "📊 Verified Department Ledger"])

    with tab_desk:
        st.markdown(f"##### Ask {active_dept} Intelligence")
        st.caption(f"Inquiries are strictly isolated to verified documents within {active_dept}.")

        mic_html_dept = f"""
        <div style="display:flex; align-items:center; gap:12px; background:#0f172a; padding:12px 16px; border-radius:14px; border:1px solid #334155; margin-bottom:10px;">
            <button id="deptMicBtn" onclick="runDeptSpeech()" style="background:#6366f1; border:none; border-radius:50%; width:44px; height:44px; font-size:19px; color:white; cursor:pointer; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                🎙️
            </button>
            <span id="deptMicLabel" style="font-size:0.92rem; color:#94a3b8; font-weight:500;">Tap mic to speak about {active_dept}...</span>
        </div>
        <script>
        function runDeptSpeech() {{
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                alert('Speech recognition browser lo support ledhu. Chrome/Edge use cheyandi.');
                return;
            }}
            var SRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            var rec = new SRec();
            rec.lang = 'en-IN';
            rec.interimResults = false;
            rec.maxAlternatives = 1;

            document.getElementById('deptMicBtn').style.background = '#ef4444';
            document.getElementById('deptMicLabel').innerText = 'Listening... Speak now';
            document.getElementById('deptMicLabel').style.color = '#ef4444';

            rec.onresult = function(e) {{
                var text = e.results[0][0].transcript;
                document.getElementById('deptMicLabel').innerText = 'Recognized: "' + text + '"';
                document.getElementById('deptMicLabel').style.color = '#34d399';

                fillDeptQuery(text);
            }};
            function fillDeptQuery(text) {{
                try {{
                    var parentDoc = window.parent.document;
                    var input = parentDoc.querySelector('input[placeholder*="Ask about"]');
                    if (!input) return;
                    var setter = Object.getOwnPropertyDescriptor(
                        window.parent.HTMLInputElement.prototype, 'value'
                    ).set;
                    setter.call(input, text);
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    setTimeout(function() {{
                        var buttons = parentDoc.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {{
                            if (buttons[i].innerText.indexOf('Get Answer') !== -1) {{
                                buttons[i].click();
                                break;
                            }}
                        }}
                    }}, 150);
                }} catch(err) {{
                    document.getElementById('deptMicLabel').innerText = 'Voice captured. Click Get Answer.';
                }}
            }}
            rec.onerror = function(e) {{
                document.getElementById('deptMicBtn').style.background = '#6366f1';
                var errorText = e.error === 'no-speech'
                    ? 'No speech detected. Tap the mic and speak clearly.'
                    : e.error === 'not-allowed'
                    ? 'Microphone blocked. Allow microphone for localhost, then try again.'
                    : e.error === 'audio-capture'
                        ? 'No microphone found or it is busy.'
                        : 'Speech error: ' + (e.error || 'unknown error');
                document.getElementById('deptMicLabel').innerText = errorText;
                document.getElementById('deptMicLabel').style.color = '#ef4444';
            }};
            rec.onend = function() {{
                document.getElementById('deptMicBtn').style.background = '#6366f1';
            }};
            navigator.mediaDevices.getUserMedia({{ audio: true }})
                .then(function(stream) {{
                    stream.getTracks().forEach(function(track) {{ track.stop(); }});
                    rec.start();
                }})
                .catch(function() {{
                    document.getElementById('deptMicBtn').style.background = '#6366f1';
                    document.getElementById('deptMicLabel').innerText = 'Microphone blocked. Allow it in browser site settings.';
                    document.getElementById('deptMicLabel').style.color = '#ef4444';
                }});
        }}
        </script>
        """
        st.components.v1.html(mic_html_dept, height=72)

        with st.form("dept_search_form"):
            col_d_text, col_d_btn = st.columns([3.8, 1.2])
            with col_d_text:
                dept_val = st.text_input(
                    f"Query {active_dept}",
                    value=default_query_text,
                    placeholder=f"Ask about {active_dept} records...",
                    label_visibility="collapsed"
                )
            with col_d_btn:
                dept_run = st.form_submit_button("⚡ Get Answer", use_container_width=True)

        if (dept_run or voice_query_active) and dept_val:
            with st.spinner(f"Analyzing {active_dept} records..."):
                ans = answer_campus_query(dept_val, module_scope=active_dept)
                st.markdown(f"""
                <div class="ai-bubble">
                    <span style="font-size:0.75rem; color:#818cf8; font-weight:800; text-transform:uppercase; letter-spacing:0.05em;">{active_dept} Response</span>
                    <div style="margin-top:8px; font-size:1.02rem;">{ans}</div>
                </div>
                """, unsafe_allow_html=True)

    with tab_ledger:
        if not df_dept.empty:
            cols_show = ["Timestamp", "Type", "Name", "ID/Ref", "Branch", "Status"]
            if "Amount (INR)" in df_dept.columns and df_dept["Amount (INR)"].sum() > 0:
                cols_show.append("Amount (INR)")
            if "Academic Metric" in df_dept.columns:
                cols_show.append("Academic Metric")

            clean_table = df_dept[[c for c in cols_show if c in df_dept.columns]]
            table_height = 38 + (len(clean_table) * 35)
            st.dataframe(clean_table, use_container_width=True, height=table_height)

            csv_data = clean_table.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"⬇️ Export {active_dept} Ledger (CSV)",
                data=csv_data,
                file_name=f"{active_dept.lower().replace(' ', '_')}_records.csv",
                mime="text/csv"
            )
        else:
            st.info(f"No records have been filed under {active_dept} yet.")

        st.write("")
        refresh_container = st.container(key="refresh-records")
        with refresh_container:
            if st.button("Refresh Department Records", key="refresh_department_records"):
                st.rerun()