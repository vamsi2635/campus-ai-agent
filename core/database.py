import os
import pandas as pd
from datetime import datetime

DATA_FILE = "campus_ledger.xlsx"

CAMPUS_DEPARTMENTS = [
    "Admissions",
    "Accounts & Finance",
    "Examination Branch",
    "Academic & Certificates",
    "Training & Placement",
    "Human Resources (HR)",
    "Library",
    "Campus Facilities & Transport",
    "Accreditation & Compliance (IQAC)",
    "General Administration"
]

def classify_category(doc_type: str) -> str:
    """Classifies any document into specific campus departments."""
    doc = str(doc_type).lower()

    if any(k in doc for k in ["fee", "challan", "receipt", "invoice", "bill", "payment", "salary", "payroll", "voucher", "reimbursement"]):
        return "Accounts & Finance"
    elif any(k in doc for k in ["admission", "rank card", "allotment", "entrance", "undertaking", "affidavit", "eamcet", "jee"]):
        return "Admissions"
    elif any(k in doc for k in ["marks", "memo", "grade", "hall ticket", "admit card", "re-evaluation", "cml", "award list"]):
        return "Examination Branch"
    elif any(k in doc for k in ["transfer", "tc", "bonafide", "study certificate", "custodian", "migration", "no due", "degree", "provisional"]):
        return "Academic & Certificates"
    elif any(k in doc for k in ["resume", "cv", "offer letter", "internship", "mou", "placement", "nda"]):
        return "Training & Placement"
    elif any(k in doc for k in ["faculty", "leave application", "appraisal", "service book", "appointment", "resignation", "increment", "bio-data"]):
        return "Human Resources (HR)"
    elif any(k in doc for k in ["library", "accession", "journal", "book", "plagiarism"]):
        return "Library"
    elif any(k in doc for k in ["hostel", "mess", "bus", "transport", "amc", "maintenance", "vehicle", "fuel"]):
        return "Campus Facilities & Transport"
    elif any(k in doc for k in ["naac", "nba", "iqac", "aicte", "nirf", "feedback", "affiliation", "co-po"]):
        return "Accreditation & Compliance (IQAC)"
    return "General Administration"

def record_entry(entry: dict, status: str = "Approved") -> bool:
    doc_type = entry.get("document_type", "General Paperwork")
    category = classify_category(doc_type)

    row = {
        "Entry_ID": f"DOC-{int(datetime.now().timestamp() * 1000)}",
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Category": category,
        "Type": doc_type,
        "Name": entry.get("student_or_vendor_name", "N/A"),
        "ID/Ref": entry.get("identifier_number", "N/A"),
        "Branch": entry.get("department_or_branch", "General"),
        "Academic Metric": entry.get("academic_metric", "N/A"),
        "Amount (INR)": float(entry.get("primary_amount", 0.0) or 0.0),
        "Status": status
    }
    
    new_df = pd.DataFrame([row])
    
    if os.path.exists(DATA_FILE):
        existing_df = pd.read_excel(DATA_FILE)
        if "Category" not in existing_df.columns:
            existing_df["Category"] = existing_df["Type"].apply(classify_category)
        if "Entry_ID" not in existing_df.columns:
            existing_df["Entry_ID"] = [f"DOC-{i}" for i in range(len(existing_df))]
        combined = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined = new_df
        
    combined.to_excel(DATA_FILE, index=False)
    return True

def soft_delete_entry(entry_id: str) -> bool:
    """Marks a specific record as Deleted without removing it permanently."""
    if not os.path.exists(DATA_FILE):
        return False
    df = pd.read_excel(DATA_FILE)
    if "Entry_ID" in df.columns and (df["Entry_ID"] == entry_id).any():
        df.loc[df["Entry_ID"] == entry_id, "Status"] = "Deleted"
        df.to_excel(DATA_FILE, index=False)
        return True
    return False

def get_ledger_dataframe(category: str = None, include_deleted: bool = False) -> pd.DataFrame:
    cols = ["Entry_ID", "Timestamp", "Category", "Type", "Name", "ID/Ref", "Branch", "Academic Metric", "Amount (INR)", "Status"]
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=cols)

    df = pd.read_excel(DATA_FILE)
    if df.empty:
        return pd.DataFrame(columns=cols)

    # Paatha records ki Entry_ID lekapothe auto-generate chesthundi
    if "Entry_ID" not in df.columns:
        df["Entry_ID"] = [f"DOC-{1000 + i}" for i in range(len(df))]
        df.to_excel(DATA_FILE, index=False)

    if "Category" not in df.columns and "Type" in df.columns:
        df["Category"] = df["Type"].apply(classify_category)

    if "Status" not in df.columns:
        df["Status"] = "Approved"

    if not include_deleted and "Status" in df.columns:
        df = df[df["Status"] != "Deleted"]

    if category and category != "All":
        return df[df["Category"] == category]
    return df