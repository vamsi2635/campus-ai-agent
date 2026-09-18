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

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1240px;
    }

    .stat-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 20px;
        backdrop-filter: blur(12px);
    }
    .stat-label {
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stat-value {
        font-size: 1.55rem;
        color: #f8fafc;
        font-weight: 700;
        margin-top: 4px;
    }

    .dept-hero {
        background: linear-gradient(135deg, #1e1e38 0%, #0f172a 100%);
        border: 1px solid #312e81;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .dept-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 18px;
        transition: all 0.2s ease-in-out;
    }
    .dept-card:hover {
        border-color: #6366f1;
        box-shadow: 0 8px 24px -8px rgba(99, 102, 241, 0.25);
    }
    .dept-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-top: 8px;
        margin-bottom: 6px;
    }
    .badge-pill {
        display: inline-block;
        padding: 3px 10px;
        background: rgba(99, 102, 241, 0.12);
        color: #818cf8;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .ai-bubble {
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid #334155;
        border-left: 5px solid #6366f1;
        border-radius: 14px;
        padding: 20px 24px;
        margin-top: 16px;
        color: #f1f5f9;
        line-height: 1.65;
        font-size: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

if "selected_department" not in st.session_state:
    st.session_state.selected_department = "Overview"

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

top_left, top_right = st.columns([3, 1.2])
with top_left:
    st.markdown("## ⚡ CampusOS <span style='font-size:0.85rem; color:#818cf8; font-weight:700; padding:3px 10px; border-radius:8px; background:rgba(99,102,241,0.15); margin-left:6px;'>ENTERPRISE</span>", unsafe_allow_html=True)
    st.caption("Multimodal Vision Governance & Executive Intelligence Architecture")

with top_right:
    if st.session_state.selected_department != "Overview":
        st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
        if st.button("← Return to Overview", use_container_width=True):
            st.session_state.selected_department = "Overview"
            st.rerun()

st.divider()

if st.session_state.selected_department == "Overview":
    total_scans = len(df_all)
    approved_scans = len(df_all[df_all["Status"] == "Approved"]) if not df_all.empty else 0
    total_rev = df_all[(df_all["Category"] == "Accounts & Finance") & (df_all["Status"] == "Approved")]["Amount (INR)"].sum() if not df_all.empty else 0.0

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Total Documents Processed</div>
            <div class="stat-value">{total_scans}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Verified & Approved</div>
            <div class="stat-value" style="color:#34d399;">{approved_scans}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Accounts Reconciliation</div>
            <div class="stat-value" style="color:#60a5fa;">₹{total_rev:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    dept_options = ["Overview"] + CAMPUS_DEPARTMENTS
    chosen = st.selectbox("Direct Department Selector:", dept_options, label_visibility="collapsed")
    if chosen != "Overview":
        st.session_state.selected_department = chosen
        st.rerun()

    st.markdown("<h4 style='color:#cbd5e1; margin-top:8px; margin-bottom:14px;'>Campus Department Modules</h4>", unsafe_allow_html=True)

    grid_cols = st.columns(3)
    for idx, dept in enumerate(CAMPUS_DEPARTMENTS):
        icon = DEPT_ICONS.get(dept, "📁")
        dept_df = df_all[df_all["Category"] == dept]
        records_count = len(dept_df)

        with grid_cols[idx % 3]:
            st.markdown(f"""
            <div class="dept-card">
                <span style="font-size: 1.6rem;">{icon}</span>
                <div class="dept-title">{dept}</div>
                <span class="badge-pill">{records_count} Records Logged</span>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Enter {dept} Console", key=f"open_{idx}", use_container_width=True):
                st.session_state.selected_department = dept
                st.rerun()
            st.write("")

    st.markdown("---")

    st.markdown("<h4 style='color:#cbd5e1;'>🔍 Global Campus Intelligence Desk</h4>", unsafe_allow_html=True)
    st.caption("Click microphone to speak, question will appear below, then click '⚡ Get Answer':")

    mic_html_overview = """
    <div style="display:flex; align-items:center; gap:10px; background:#0f172a; padding:10px 14px; border-radius:12px; border:1px solid #334155;">
        <button id="micBtn" onclick="runSpeech()" style="background:#6366f1; border:none; border-radius:50%; width:40px; height:40px; font-size:18px; color:white; cursor:pointer; display:flex; align-items:center; justify-content:center;">
            🎙️
        </button>
        <span id="micLabel" style="font-size:0.9rem; color:#94a3b8;">Click mic to speak your question...</span>
    </div>
    <script>
    function runSpeech() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
            return;
        }
        var SRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        var rec = new SRec();
        rec.lang = 'en-US';
        rec.interimResults = false;

        document.getElementById('micBtn').style.background = '#ef4444';
        document.getElementById('micLabel').innerText = 'Listening... Speak now';
        document.getElementById('micLabel').style.color = '#ef4444';

        rec.onresult = function(e) {
            var text = e.results[0][0].transcript;
            document.getElementById('micLabel').innerText = 'Recognized: "' + text + '"';
            document.getElementById('micLabel').style.color = '#34d399';

            try {
                var pInputs = window.parent.document.querySelectorAll('input[type="text"]');
                for (var i = 0; i < pInputs.length; i++) {
                    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    setter.call(pInputs[i], text);
                    pInputs[i].dispatchEvent(new Event('input', { bubbles: true }));
                    pInputs[i].dispatchEvent(new Event('change', { bubbles: true }));
                }
            } catch(err) {}
        };
        rec.onend = function() {
            document.getElementById('micBtn').style.background = '#6366f1';
        };
        rec.start();
    }
    </script>
    """
    st.components.v1.html(mic_html_overview, height=65)

    with st.form("global_search_form"):
        col_text, col_btn = st.columns([4, 1.2])
        with col_text:
            query_val = st.text_input("Query", placeholder="Spoken question will appear here, or type manually...", label_visibility="collapsed")
        with col_btn:
            submit_run = st.form_submit_button("⚡ Get Answer", use_container_width=True)

    if submit_run and query_val:
        with st.spinner("Analyzing ledger records..."):
            ans = answer_campus_query(query_val, module_scope="All")
            st.markdown(f"""
            <div class="ai-bubble">
                <span style="font-size:0.8rem; color:#818cf8; font-weight:700; text-transform:uppercase;">AI Executive Insight</span>
                <div style="margin-top:8px; font-size:1.05rem;">{ans}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    active_dept = st.session_state.selected_department
    df_dept = get_ledger_dataframe(active_dept)
    icon = DEPT_ICONS.get(active_dept, "🏢")

    total_dept_items = len(df_dept)
    approved_dept_items = len(df_dept[df_dept["Status"] == "Approved"]) if not df_dept.empty else 0

    st.markdown(f"""
    <div class="dept-hero">
        <div style="font-size:1.6rem; font-weight:700; color:#f8fafc; display:flex; align-items:center; gap:12px;">
            <span>{icon}</span> {active_dept}
        </div>
        <p style="color:#94a3b8; font-size:0.9rem; margin-top:6px; margin-bottom:16px;">
            Verified records and isolated intelligence for {active_dept}.
        </p>
        <div style="display:flex; gap:16px; flex-wrap:wrap;">
            <div style="background:rgba(255,255,255,0.06); padding:8px 16px; border-radius:8px; border:1px solid rgba(255,255,255,0.1);">
                <span style="font-size:0.75rem; color:#94a3b8; font-weight:600;">LOGGED RECORDS</span><br>
                <b style="font-size:1.1rem; color:#f8fafc;">{total_dept_items}</b>
            </div>
            <div style="background:rgba(255,255,255,0.06); padding:8px 16px; border-radius:8px; border:1px solid rgba(255,255,255,0.1);">
                <span style="font-size:0.75rem; color:#94a3b8; font-weight:600;">VERIFIED & ACTIVE</span><br>
                <b style="font-size:1.1rem; color:#34d399;">{approved_dept_items}</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_desk, tab_ledger = st.tabs(["🔍 Department AI Desk", "📊 Verified Department Ledger"])

    with tab_desk:
        st.markdown(f"#### Ask {active_dept} Intelligence")
        st.caption(f"Inquiries are strictly isolated to verified documents within {active_dept}.")

        mic_html_dept = f"""
        <div style="display:flex; align-items:center; gap:10px; background:#0f172a; padding:10px 14px; border-radius:12px; border:1px solid #334155;">
            <button id="deptMicBtn" onclick="runDeptSpeech()" style="background:#6366f1; border:none; border-radius:50%; width:40px; height:40px; font-size:18px; color:white; cursor:pointer; display:flex; align-items:center; justify-content:center;">
                🎙️
            </button>
            <span id="deptMicLabel" style="font-size:0.9rem; color:#94a3b8;">Click mic to speak about {active_dept}...</span>
        </div>
        <script>
        function runDeptSpeech() {{
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
                return;
            }}
            var SRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            var rec = new SRec();
            rec.lang = 'en-US';
            rec.interimResults = false;

            document.getElementById('deptMicBtn').style.background = '#ef4444';
            document.getElementById('deptMicLabel').innerText = 'Listening... Speak now';
            document.getElementById('deptMicLabel').style.color = '#ef4444';

            rec.onresult = function(e) {{
                var text = e.results[0][0].transcript;
                document.getElementById('deptMicLabel').innerText = 'Recognized: "' + text + '"';
                document.getElementById('deptMicLabel').style.color = '#34d399';

                try {{
                    var pInputs = window.parent.document.querySelectorAll('input[type="text"]');
                    for (var i = 0; i < pInputs.length; i++) {{
                        var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                        setter.call(pInputs[i], text);
                        pInputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                        pInputs[i].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }} catch(err) {{}}
            }};
            rec.onend = function() {{
                document.getElementById('deptMicBtn').style.background = '#6366f1';
            }};
            rec.start();
        }}
        </script>
        """
        st.components.v1.html(mic_html_dept, height=65)

        with st.form("dept_search_form"):
            col_d_text, col_d_btn = st.columns([4, 1.2])
            with col_d_text:
                dept_val = st.text_input(f"Query {active_dept}", placeholder=f"Ask about {active_dept} records...", label_visibility="collapsed")
            with col_d_btn:
                dept_run = st.form_submit_button("⚡ Get Answer", use_container_width=True)

        if dept_run and dept_val:
            with st.spinner(f"Analyzing {active_dept} records..."):
                ans = answer_campus_query(dept_val, module_scope=active_dept)
                st.markdown(f"""
                <div class="ai-bubble">
                    <span style="font-size:0.8rem; color:#818cf8; font-weight:700; text-transform:uppercase;">{active_dept} Response</span>
                    <div style="margin-top:8px; font-size:1.05rem;">{ans}</div>
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
            st.dataframe(clean_table, use_container_width=True, height=360)

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
        if st.button("Refresh Department Records"):
            st.rerun()