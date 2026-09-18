import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
from core.database import get_ledger_dataframe, CAMPUS_DEPARTMENTS, record_entry
from core.extractor import extract_document_data
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
    .desk-heading {
        width: min(100%, 820px);
        margin: 24px 0 6px;
        margin-left: auto;
        margin-right: auto;
        color: #e2e8f0;
        font-size: 1rem;
        font-weight: 800;
        line-height: 1.25;
        text-align: center;
        letter-spacing: 0.01em;
    }
    .desk-heading::after {
        content: "";
        display: block;
        width: 42px;
        height: 2px;
        margin: 7px auto 0;
        border-radius: 2px;
        background: #6366f1;
    }
    .desk-caption {
        display: block;
        width: min(100%, 760px);
        margin: 0 auto 10px;
        color: #94a3b8;
        font-size: 0.76rem;
        line-height: 1.45;
        text-align: center;
    }
    [data-testid="stFileUploader"] section {
        min-height: 0 !important;
        padding: 8px 12px !important;
        border: 1px solid rgba(148, 163, 184, 0.24) !important;
        border-radius: 12px !important;
        background: rgba(15, 23, 42, 0.72) !important;
    }
    [data-testid="stFileUploader"] {
        width: min(100%, 820px) !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    [data-testid="stFileUploader"] section > div {
        padding: 0 !important;
    }
    [data-testid="stFileUploader"] button {
        min-height: 30px !important;
        height: 30px !important;
        padding: 0 12px !important;
        border-radius: 15px !important;
        font-size: 0.72rem !important;
    }
    [data-testid="stFileUploader"] small {
        font-size: 0.68rem !important;
    }
    .st-key-bulk-scan-action {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    .st-key-bulk-scan-action div.stButton {
        width: auto !important;
    }
    .st-key-bulk-scan-action div.stButton > button {
        width: 240px !important;
        min-width: 240px !important;
        height: 38px !important;
        min-height: 38px !important;
        margin: 0 auto !important;
        padding: 0 14px !important;
        border-radius: 19px !important;
        font-size: 0.78rem !important;
        text-align: center !important;
    }
    .st-key-bulk-scan-action div.stButton > button p {
        width: 100% !important;
        margin: 0 !important;
        text-align: center !important;
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
        .desk-heading {
            margin-top: 20px;
            font-size: 0.88rem;
        }
        .desk-caption {
            padding: 0 8px;
            font-size: 0.68rem;
        }
        [data-testid="stFileUploader"] section {
            padding: 7px 8px !important;
        }
        [data-testid="stFileUploader"] section > div {
            gap: 6px !important;
        }
        .st-key-bulk-scan-action div.stButton > button {
            width: 100% !important;
            min-width: 0 !important;
            height: 36px !important;
            min-height: 36px !important;
            font-size: 0.7rem !important;
        }
        .st-key-bulk-scan-action div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            gap: 0 !important;
        }
        .st-key-bulk-scan-action div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            flex: 0 0 15% !important;
            width: 15% !important;
            min-width: 15% !important;
        }
        .st-key-bulk-scan-action div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
            flex: 0 0 70% !important;
            width: 70% !important;
            min-width: 70% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

if "selected_department" not in st.session_state:
    st.session_state.selected_department = "Overview"

if "bulk_scanned_results" not in st.session_state:
    st.session_state.bulk_scanned_results = []

if "bulk_uploader_version" not in st.session_state:
    st.session_state.bulk_uploader_version = 0

# Read recognized speech from query param
voice_input_param = st.query_params.get("voice_q", "")
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

    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

    # =========================================================
    # 🚀 BULK AI DOCUMENT PROCESSING DESK (DRAG & DROP)
    # =========================================================
    st.markdown('<div class="desk-heading">📂 Bulk Document Ingestion Desk</div>', unsafe_allow_html=True)
    st.markdown('<span class="desk-caption">Upload multiple document scans (Images / Photos) at once to instantly parse and commit to the master ledger.</span>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Choose files", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True, 
        key=f"bulk_file_uploader_{st.session_state.bulk_uploader_version}",
        label_visibility="collapsed"
    )

    upload_signature = tuple((file.name, file.size) for file in uploaded_files) if uploaded_files else ()
    previous_upload_signature = st.session_state.get("last_bulk_upload_signature", ())
    if upload_signature != previous_upload_signature:
        st.session_state.last_bulk_upload_signature = upload_signature
        st.rerun()

    if uploaded_files:
        scan_action = st.container(key="bulk-scan-action")
        with scan_action:
            scan_spacer_left, scan_button_col, scan_spacer_right = st.columns([1, 2, 1])
            with scan_button_col:
                if st.button(
                    f"⚡ Scan & Extract {len(uploaded_files)} Documents",
                    key="btn_scan_bulk",
                    use_container_width=True
                ):
                    st.session_state.bulk_scanned_results = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for i, file in enumerate(uploaded_files):
                        status_text.text(f"Processing ({i+1}/{len(uploaded_files)}): {file.name}...")
                        temp_p = f"temp_bulk_{i}_{file.name}"
                        with open(temp_p, "wb") as f:
                            f.write(file.getbuffer())

                        try:
                            data = extract_document_data(temp_p)
                            data["filename"] = file.name
                            st.session_state.bulk_scanned_results.append(data)
                        except Exception as err:
                            st.error(f"Error reading {file.name}: {str(err)}")
                        finally:
                            if os.path.exists(temp_p):
                                os.remove(temp_p)
                        progress_bar.progress((i + 1) / len(uploaded_files))

                    status_text.success(f"Successfully processed {len(st.session_state.bulk_scanned_results)} documents!")
                    st.session_state.bulk_uploader_version += 1
                    st.rerun()

    # Display Scanned Results Preview & One-click Commit
    if st.session_state.bulk_scanned_results:
        st.markdown("##### 📋 Scanned Documents Preview")
        preview_data = []
        for d in st.session_state.bulk_scanned_results:
            preview_data.append({
                "File": d.get("filename", ""),
                "Type": d.get("document_type", ""),
                "Candidate/Vendor": d.get("student_or_vendor_name", ""),
                "ID/Ref": d.get("identifier_number", ""),
                "Branch": d.get("department_or_branch", ""),
                "Metric": d.get("academic_metric", ""),
                "Amount (₹)": d.get("primary_amount", 0.0)
            })
        st.dataframe(pd.DataFrame(preview_data), use_container_width=True)

        st.markdown("""
        <style>
            .st-key-bulk-review-actions div[data-testid="stHorizontalBlock"] {
                justify-content: center !important;
                align-items: center !important;
                gap: 12px !important;
                flex-wrap: nowrap !important;
            }
            .st-key-bulk-review-actions div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
                flex: 0 0 210px !important;
                width: 210px !important;
                min-width: 210px !important;
                display: flex !important;
                justify-content: center !important;
            }
            .st-key-bulk-review-actions div.stButton > button {
                width: 210px !important;
                min-width: 210px !important;
                height: 40px !important;
                min-height: 40px !important;
                padding: 0 12px !important;
                margin: 0 !important;
                border-radius: 20px !important;
                text-align: center !important;
                justify-content: center !important;
                font-size: 0.78rem !important;
            }
            .st-key-bulk-review-actions div.stButton > button p {
                width: 100% !important;
                margin: 0 !important;
                text-align: center !important;
            }
            .st-key-bulk-review-actions div[data-testid="stHorizontalBlock"] > div:first-child button {
                background: #22c55e !important;
                border-color: #16a34a !important;
                color: #052e16 !important;
            }
            .st-key-bulk-review-actions div[data-testid="stHorizontalBlock"] > div:last-child button {
                background: #ef4444 !important;
                border-color: #dc2626 !important;
                color: #ffffff !important;
            }
            @media (max-width: 768px) {
                .st-key-bulk-review-actions div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
                    flex: 0 0 calc(50% - 6px) !important;
                    width: calc(50% - 6px) !important;
                    min-width: calc(50% - 6px) !important;
                }
                .st-key-bulk-review-actions div.stButton > button {
                    width: 100% !important;
                    min-width: 0 !important;
                    height: 36px !important;
                    min-height: 36px !important;
                    font-size: 0.68rem !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)

        review_actions = st.container(key="bulk-review-actions")
        with review_actions:
            col_approve, col_dismiss = st.columns([1, 1], gap="small")
            with col_approve:
                if st.button(f"✅ Approve & Commit All ({len(preview_data)} Records)", key="btn_commit_bulk", use_container_width=True):
                    for rec in st.session_state.bulk_scanned_results:
                        record_entry(rec, status="Approved")
                    st.session_state.bulk_scanned_results = []
                    st.success("All records committed directly to the Campus Master Ledger!")
                    st.rerun()

            with col_dismiss:
                if st.button("❌ Discard Batch", key="btn_discard_bulk", use_container_width=True):
                    st.session_state.bulk_scanned_results = []
                    st.rerun()

    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="desk-heading">🔍 Global Campus Intelligence Desk</div>', unsafe_allow_html=True)
    st.markdown('<span class="desk-caption">Click microphone to speak your question, or type manually, then click \'⚡ Get Answer\'.</span>', unsafe_allow_html=True)

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
        rec.lang = 'en-US';
        rec.interimResults = false;

        document.getElementById('micBtn').style.background = '#ef4444';
        document.getElementById('micLabel').innerText = 'Listening... Speak now';
        document.getElementById('micLabel').style.color = '#ef4444';

        rec.onresult = function(e) {
            var text = e.results[0][0].transcript;
            document.getElementById('micLabel').innerText = 'Recognized: "' + text + '"';
            document.getElementById('micLabel').style.color = '#34d399';

            submitVoiceQuery(text, 'Spoken text appears here');
        };
        function submitVoiceQuery(text, placeholderText) {
            try {
                var parentDoc = window.parent.document;
                var input = parentDoc.querySelector('input[placeholder*="' + placeholderText + '"]');
                if (!input) {
                    document.getElementById('micLabel').innerText = 'Voice captured. Click Get Answer.';
                    return;
                }
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
                            return;
                        }
                    }
                }, 200);
            } catch(err) {
                document.getElementById('micLabel').innerText = 'Voice captured. Click Get Answer.';
            }
        }
        rec.onerror = function(e) {
            document.getElementById('micBtn').style.background = '#6366f1';
            document.getElementById('micLabel').innerText = 'Error or Mic Denied. Please allow microphone.';
            document.getElementById('micLabel').style.color = '#ef4444';
        };
        rec.onend = function() {
            document.getElementById('micBtn').style.background = '#6366f1';
        };
        rec.start();
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

    if submit_run and query_val:
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
            rec.lang = 'en-US';
            rec.interimResults = false;

            document.getElementById('deptMicBtn').style.background = '#ef4444';
            document.getElementById('deptMicLabel').innerText = 'Listening... Speak now';
            document.getElementById('deptMicLabel').style.color = '#ef4444';

            rec.onresult = function(e) {{
                var text = e.results[0][0].transcript;
                document.getElementById('deptMicLabel').innerText = 'Recognized: "' + text + '"';
                document.getElementById('deptMicLabel').style.color = '#34d399';

                submitDeptVoiceQuery(text);
            }};
            function submitDeptVoiceQuery(text) {{
                try {{
                    var parentDoc = window.parent.document;
                    var input = parentDoc.querySelector('input[placeholder*="Ask about"]');
                    if (!input) {{
                        document.getElementById('deptMicLabel').innerText = 'Voice captured. Click Get Answer.';
                        return;
                    }}
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
                                return;
                            }}
                        }}
                    }}, 200);
                }} catch(err) {{
                    document.getElementById('deptMicLabel').innerText = 'Voice captured. Click Get Answer.';
                }}
            }}
            rec.onerror = function(e) {{
                document.getElementById('deptMicBtn').style.background = '#6366f1';
                document.getElementById('deptMicLabel').innerText = 'Error or Mic Denied. Please allow microphone.';
                document.getElementById('deptMicLabel').style.color = '#ef4444';
            }};
            rec.onend = function() {{
                document.getElementById('deptMicBtn').style.background = '#6366f1';
            }};
            rec.start();
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

        if dept_run and dept_val:
            with st.spinner(f"Analyzing {active_dept} records..."):
                ans = answer_campus_query(dept_val, module_scope=active_dept)
                st.markdown(f"""
                <div class="ai-bubble">
                    <span style="font-size:0.75rem; color:#818cf8; font-weight:800; text-transform:uppercase; letter-spacing:0.05em;">{active_dept} Response</span>
                    <div style="margin-top:8px; font-size:1.02rem;">{ans}</div>
                </div>
                """, unsafe_allow_html=True)

    with tab_ledger:
        from core.database import soft_delete_entry

        # --- Industry Standard Sleek Modal Popup ---
        @st.dialog("Delete Record")
        def confirm_delete_modal(record_id):
            st.markdown("""
            <style>
                div[data-testid="stDialog"] div[role="dialog"] {
                    border-radius: 18px !important;
                    background: #0f172a !important;
                    border: 1px solid rgba(255, 255, 255, 0.12) !important;
                    box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.7) !important;
                }
                .st-key-delete-confirm-action,
                .st-key-delete-cancel-action {
                    display: flex !important;
                    justify-content: center !important;
                    width: 100% !important;
                }
                .st-key-delete-confirm-action div.stButton,
                .st-key-delete-cancel-action div.stButton {
                    width: auto !important;
                }
                .st-key-delete-confirm-action div.stButton > button {
                    all: unset !important;
                    box-sizing: border-box !important;
                    display: inline-flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    height: 34px !important;
                    min-height: 34px !important;
                    width: 108px !important;
                    padding: 0 14px !important;
                    border-radius: 17px !important;
                    background: #ef4444 !important;
                    border: 1px solid #dc2626 !important;
                    color: #ffffff !important;
                    font-size: 0.82rem !important;
                    font-weight: 700 !important;
                    cursor: pointer !important;
                    transition: opacity 0.15s ease !important;
                }
                .st-key-delete-confirm-action div.stButton > button:hover {
                    opacity: 0.88 !important;
                }
                .st-key-delete-cancel-action div.stButton > button {
                    all: unset !important;
                    box-sizing: border-box !important;
                    display: inline-flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    height: 34px !important;
                    min-height: 34px !important;
                    width: 108px !important;
                    padding: 0 14px !important;
                    border-radius: 17px !important;
                    background: #22c55e !important;
                    border: 1px solid #16a34a !important;
                    color: #052e16 !important;
                    font-size: 0.82rem !important;
                    font-weight: 600 !important;
                    cursor: pointer !important;
                    transition: background 0.15s ease !important;
                }
                .st-key-delete-cancel-action div.stButton > button:hover {
                    background: #4ade80 !important;
                    color: #052e16 !important;
                }
                .st-key-delete-confirm-action div.stButton > button p,
                .st-key-delete-cancel-action div.stButton > button p {
                    margin: 0 !important;
                    font-size: 0.82rem !important;
                    line-height: 1 !important;
                }
                @media (max-width: 768px) {
                    div[data-testid="stDialog"] div[role="dialog"] {
                        width: calc(100vw - 24px) !important;
                        max-width: calc(100vw - 24px) !important;
                        padding: 16px !important;
                    }
                    .st-key-delete-confirm-action div.stButton > button,
                    .st-key-delete-cancel-action div.stButton > button {
                        width: 88px !important;
                        min-width: 88px !important;
                        height: 32px !important;
                        min-height: 32px !important;
                        padding: 0 8px !important;
                        font-size: 0.72rem !important;
                    }
                    .st-key-delete-confirm-action div.stButton > button p,
                    .st-key-delete-cancel-action div.stButton > button p {
                        font-size: 0.72rem !important;
                    }
                }
            </style>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="font-size:0.92rem; color:#cbd5e1; line-height:1.5; margin-bottom:18px;">
                Are you sure you want to soft delete record <b style="color:#f8fafc;">{record_id}</b>?
                <br><span style="font-size:0.78rem; color:#64748b;">This record will be safely archived and hidden from live modules.</span>
            </div>
            """, unsafe_allow_html=True)

            action_spacer_left, action_group, action_spacer_right = st.columns([1, 2, 1])
            with action_group:
                action_col1, action_col2 = st.columns([1, 1], gap="small")

            with action_col1:
                delete_action = st.container(key="delete-confirm-action")
                with delete_action:
                    if st.button("Yes, Delete", key=f"dlg_yes_{record_id}", use_container_width=True):
                        soft_delete_entry(record_id)
                        st.rerun()

            with action_col2:
                cancel_action = st.container(key="delete-cancel-action")
                with cancel_action:
                    if st.button("Cancel", key=f"dlg_no_{record_id}", use_container_width=True):
                        st.rerun()

        if not df_dept.empty:
            cols_show = ["Timestamp", "Type", "Name", "ID/Ref", "Branch", "Status"]
            if "Amount (INR)" in df_dept.columns and df_dept["Amount (INR)"].sum() > 0:
                cols_show.append("Amount (INR)")
            if "Academic Metric" in df_dept.columns:
                cols_show.append("Academic Metric")

            # Inline Action Row Styling
            st.markdown("""
            <style>
                .ledger-row-header {
                    font-size: 0.72rem;
                    font-weight: 700;
                    color: #94a3b8;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    padding: 8px 10px;
                    border-bottom: 2px solid rgba(255,255,255,0.12);
                }
                .ledger-cell {
                    font-size: 0.86rem;
                    color: #f1f5f9;
                    padding: 10px 10px;
                    display: flex;
                    align-items: center;
                    word-break: break-word;
                }
                .mobile-field-label {
                    display: none;
                }
                .st-key-mobile-ledger {
                    display: none !important;
                }
                .st-key-mobile-delete-actions {
                    display: none !important;
                }
                div.del-btn-wrap div.stButton > button {
                    all: unset !important;
                    box-sizing: border-box !important;
                    display: inline-flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    width: 32px !important;
                    height: 32px !important;
                    min-height: 32px !important;
                    max-height: 32px !important;
                    border-radius: 8px !important;
                    background: rgba(239, 68, 68, 0.12) !important;
                    border: 1px solid rgba(239, 68, 68, 0.3) !important;
                    color: #fca5a5 !important;
                    cursor: pointer !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    transition: all 0.15s ease !important;
                }
                div.del-btn-wrap div.stButton > button:hover {
                    background: #ef4444 !important;
                    color: #ffffff !important;
                    border-color: #ef4444 !important;
                }
                div.del-btn-wrap div.stButton > button p {
                    margin: 0 !important;
                    font-size: 0.95rem !important;
                    line-height: 1 !important;
                }
                @media (max-width: 768px) {
                    div[data-testid="stHorizontalBlock"]:has(.ledger-row-header),
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) {
                        display: flex !important;
                        flex-wrap: nowrap !important;
                        min-width: 830px !important;
                        overflow: visible !important;
                        gap: 0 !important;
                        margin-bottom: 2px !important;
                    }
                    div[data-testid="stVerticalBlock"]:has(.ledger-row-header) {
                        display: block !important;
                        width: 100% !important;
                        max-width: 100% !important;
                        overflow-x: auto !important;
                        padding-bottom: 8px !important;
                        scrollbar-width: thin !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-row-header),
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) {
                        width: max-content !important;
                        min-width: 700px !important;
                        max-width: none !important;
                        padding-right: 0 !important;
                    }
                    .st-key-mobile-ledger div[data-testid="stHorizontalBlock"] {
                        display: none !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-row-header) > div[data-testid="stColumn"],
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) > div[data-testid="stColumn"] {
                        flex: 0 0 auto !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-row-header) > div[data-testid="stColumn"]:nth-child(1),
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) > div[data-testid="stColumn"]:nth-child(1) {
                        flex: 0 0 115px !important;
                        width: 115px !important;
                        min-width: 115px !important;
                        max-width: 115px !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-row-header) > div[data-testid="stColumn"]:nth-child(2),
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) > div[data-testid="stColumn"]:nth-child(2) {
                        flex: 0 0 110px !important;
                        width: 110px !important;
                        min-width: 110px !important;
                        max-width: 110px !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-row-header) > div[data-testid="stColumn"]:nth-child(3),
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) > div[data-testid="stColumn"]:nth-child(3) {
                        flex: 0 0 120px !important;
                        width: 120px !important;
                        min-width: 120px !important;
                        max-width: 120px !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-row-header) > div[data-testid="stColumn"]:nth-child(4),
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) > div[data-testid="stColumn"]:nth-child(4) {
                        flex: 0 0 105px !important;
                        width: 105px !important;
                        min-width: 105px !important;
                        max-width: 105px !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-row-header) > div[data-testid="stColumn"]:nth-child(5),
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) > div[data-testid="stColumn"]:nth-child(5) {
                        flex: 0 0 120px !important;
                        width: 120px !important;
                        min-width: 120px !important;
                        max-width: 120px !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-row-header) > div[data-testid="stColumn"]:nth-child(6),
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) > div[data-testid="stColumn"]:nth-child(6) {
                        flex: 0 0 75px !important;
                        width: 75px !important;
                        min-width: 75px !important;
                        max-width: 75px !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-row-header) > div[data-testid="stColumn"]:nth-child(7),
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) > div[data-testid="stColumn"]:nth-child(7) {
                        flex: 0 0 55px !important;
                        width: 55px !important;
                        min-width: 55px !important;
                        max-width: 55px !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-row-header) .ledger-row-header {
                        font-size: 0.62rem !important;
                        padding: 5px 6px !important;
                        background: #111827 !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) .ledger-cell {
                        min-height: 0 !important;
                        height: auto !important;
                        padding: 4px 6px !important;
                        font-size: 0.7rem !important;
                        line-height: 1.1 !important;
                        border-bottom: 1px solid rgba(148, 163, 184, 0.12) !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) .mobile-field-label {
                        display: none !important;
                    }
                    div[data-testid="stHorizontalBlock"]:has(.ledger-cell) .del-btn-wrap div.stButton > button {
                        width: 30px !important;
                        height: 26px !important;
                        min-height: 26px !important;
                        padding: 0 !important;
                    }
                }
            </style>
            """, unsafe_allow_html=True)

            # Table Header
            h_cols = st.columns([1.6, 1.4, 1.8, 1.4, 2, 1.2, 0.8], vertical_alignment="center")
            header_titles = ["Timestamp", "Type", "Name", "ID/Ref", "Branch", "Status", "Action"]
            for h_col, h_text in zip(h_cols, header_titles):
                with h_col:
                    st.markdown(f'<div class="ledger-row-header">{h_text}</div>', unsafe_allow_html=True)

            # Table Rows
            for idx, row in df_dept.iterrows():
                e_id = str(row.get("Entry_ID", f"DOC-{idx}"))
                r_cols = st.columns([1.6, 1.4, 1.8, 1.4, 2, 1.2, 0.8], vertical_alignment="center")

                with r_cols[0]:
                    st.markdown(f'<div class="ledger-cell" style="color:#94a3b8; font-size:0.8rem;"><span class="mobile-field-label">Timestamp</span>{row.get("Timestamp", "-")}</div>', unsafe_allow_html=True)
                with r_cols[1]:
                    st.markdown(f'<div class="ledger-cell"><span class="mobile-field-label">Type</span><b>{row.get("Type", "-")}</b></div>', unsafe_allow_html=True)
                with r_cols[2]:
                    st.markdown(f'<div class="ledger-cell"><span class="mobile-field-label">Name</span>{row.get("Name", "-")}</div>', unsafe_allow_html=True)
                with r_cols[3]:
                    st.markdown(f'<div class="ledger-cell" style="font-family:monospace; color:#818cf8;"><span class="mobile-field-label">ID / Ref</span>{row.get("ID/Ref", "-")}</div>', unsafe_allow_html=True)
                with r_cols[4]:
                    st.markdown(f'<div class="ledger-cell"><span class="mobile-field-label">Branch</span>{row.get("Branch", "-")}</div>', unsafe_allow_html=True)
                with r_cols[5]:
                    status_colr = "#34d399" if str(row.get("Status")).lower() in ["approved", "verified"] else "#fbbf24"
                    st.markdown(f'<div class="ledger-cell"><span class="mobile-field-label">Status</span><span style="color:{status_colr}; font-weight:700;">{row.get("Status", "-")}</span></div>', unsafe_allow_html=True)
                with r_cols[6]:
                    st.markdown('<div class="ledger-cell del-btn-wrap"><span class="mobile-field-label">Action</span>', unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_row_btn_{e_id}_{idx}", help=f"Delete record {e_id}"):
                        confirm_delete_modal(e_id)
                    st.markdown('</div>', unsafe_allow_html=True)

            mobile_ledger = st.container(key="mobile-ledger")
            with mobile_ledger:
                mobile_header_cols = st.columns([1.6, 1.4, 1.8, 1.4, 2, 1.2, 0.8])
                for mobile_col, mobile_title in zip(mobile_header_cols, header_titles):
                    with mobile_col:
                        st.markdown(f'<div class="ledger-row-header">{mobile_title}</div>', unsafe_allow_html=True)

                for mobile_idx, mobile_row in df_dept.iterrows():
                    mobile_id = str(mobile_row.get("Entry_ID", f"DOC-{mobile_idx}"))
                    mobile_cols = st.columns([1.6, 1.4, 1.8, 1.4, 2, 1.2, 0.8])
                    mobile_status_color = "#34d399" if str(mobile_row.get("Status")).lower() in ["approved", "verified"] else "#fbbf24"
                    mobile_values = [
                        f'<div class="ledger-cell" style="color:#94a3b8; font-size:0.8rem;">{mobile_row.get("Timestamp", "-")}</div>',
                        f'<div class="ledger-cell"><b>{mobile_row.get("Type", "-")}</b></div>',
                        f'<div class="ledger-cell">{mobile_row.get("Name", "-")}</div>',
                        f'<div class="ledger-cell" style="font-family:monospace; color:#818cf8;">{mobile_row.get("ID/Ref", "-")}</div>',
                        f'<div class="ledger-cell">{mobile_row.get("Branch", "-")}</div>',
                        f'<div class="ledger-cell"><span style="color:{mobile_status_color}; font-weight:700;">{mobile_row.get("Status", "-")}</span></div>',
                    ]
                    for mobile_col, mobile_value in zip(mobile_cols[:6], mobile_values):
                        with mobile_col:
                            st.markdown(mobile_value, unsafe_allow_html=True)
                    with mobile_cols[6]:
                        st.markdown('<div class="ledger-cell del-btn-wrap">', unsafe_allow_html=True)
                        if st.button("🗑️", key=f"mobile_del_row_btn_{mobile_id}_{mobile_idx}", help=f"Delete record {mobile_id}"):
                            confirm_delete_modal(mobile_id)
                        st.markdown('</div>', unsafe_allow_html=True)

            st.write("")
            csv_table = df_dept[[c for c in cols_show if c in df_dept.columns]]
            csv_data = csv_table.to_csv(index=False).encode('utf-8')
        else:
            st.info(f"No records have been filed under {active_dept} yet.")

        st.markdown("""
        <style>
            .st-key-ledger-actions {
                position: sticky !important;
                bottom: 0 !important;
                z-index: 20 !important;
                padding: 8px 0 !important;
                background: #0b0f19 !important;
                border-top: 1px solid rgba(148, 163, 184, 0.16) !important;
            }
            .st-key-ledger-actions div[data-testid="stHorizontalBlock"] {
                align-items: center !important;
                justify-content: center !important;
                gap: 12px !important;
                flex-wrap: nowrap !important;
            }
            .st-key-ledger-actions div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
                flex: 0 0 180px !important;
                width: 180px !important;
                min-width: 180px !important;
                display: flex !important;
                justify-content: center !important;
            }
            .st-key-ledger-actions div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
                padding-top: 0 !important;
            }
            .st-key-ledger-actions div.stButton > button,
            .st-key-ledger-actions div.stDownloadButton > button {
                width: 180px !important;
                min-width: 180px !important;
                min-height: 38px !important;
                height: 38px !important;
                padding: 0 10px !important;
                margin: 0 auto !important;
                border-radius: 19px !important;
                font-size: 0.76rem !important;
                white-space: nowrap !important;
                text-align: center !important;
                justify-content: center !important;
            }
            .st-key-ledger-actions div.stButton > button p,
            .st-key-ledger-actions div.stDownloadButton > button p {
                width: 100% !important;
                margin: 0 !important;
                text-align: center !important;
            }
            @media (max-width: 768px) {
                .st-key-ledger-actions {
                    position: fixed !important;
                    left: 0 !important;
                    right: 0 !important;
                    bottom: 0 !important;
                    width: 100vw !important;
                    margin: 0 !important;
                    padding: 8px 12px calc(8px + env(safe-area-inset-bottom)) !important;
                    background: rgba(11, 15, 25, 0.98) !important;
                    box-shadow: 0 -6px 18px rgba(0, 0, 0, 0.28) !important;
                }
                .st-key-ledger-actions div.stButton > button,
                .st-key-ledger-actions div.stDownloadButton > button {
                    width: 100% !important;
                    min-width: 0 !important;
                    min-height: 34px !important;
                    height: 34px !important;
                    border-radius: 17px !important;
                    font-size: 0.68rem !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)

        ledger_actions = st.container(key="ledger-actions")
        with ledger_actions:
            export_col, refresh_col = st.columns([1, 1], gap="small")
            with export_col:
                if not df_dept.empty:
                    st.download_button(
                        label=f"⬇️ Export {active_dept} Ledger (CSV)",
                        data=csv_data,
                        file_name=f"{active_dept.lower().replace(' ', '_')}_records.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            with refresh_col:
                if st.button("Refresh Records", key="refresh_department_records", use_container_width=True):
                    st.rerun()