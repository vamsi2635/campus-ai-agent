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

    # Accounts & Finance
    if any(k in doc for k in ["fee", "challan", "receipt", "invoice", "bill", "payment", "salary", "payroll", "voucher", "reimbursement"]):
        return "Accounts & Finance"

    # Admissions
    elif any(k in doc for k in ["admission", "rank card", "allotment", "entrance", "undertaking", "affidavit", "eamcet", "jee"]):
        return "Admissions"

    # Examination Branch
    elif any(k in doc for k in ["marks", "memo", "grade", "hall ticket", "admit card", "re-evaluation", "cml", "award list"]):
        return "Examination Branch"

    # Academic & Certificates
    elif any(k in doc for k in ["transfer", "tc", "bonafide", "study certificate", "custodian", "migration", "no due", "degree", "provisional"]):
        return "Academic & Certificates"

    # Training & Placement
    elif any(k in doc for k in ["resume", "cv", "offer letter", "internship", "mou", "placement", "nda"]):
        return "Training & Placement"

    # Human Resources
    elif any(k in doc for k in ["faculty", "leave application", "appraisal", "service book", "appointment", "resignation", "increment", "bio-data"]):
        return "Human Resources (HR)"

    # Library
    elif any(k in doc for k in ["library", "accession", "journal", "book", "plagiarism"]):
        return "Library"

    # Campus Facilities & Transport
    elif any(k in doc for k in ["hostel", "mess", "bus", "transport", "amc", "maintenance", "vehicle", "fuel"]):
        return "Campus Facilities & Transport"

    # Accreditation & Compliance
    elif any(k in doc for k in ["naac", "nba", "iqac", "aicte", "nirf", "feedback", "affiliation", "co-po"]):
        return "Accreditation & Compliance (IQAC)"

    # Default
    return "General Administration"

def record_entry(entry: dict, status: str = "Approved") -> bool:
    doc_type = entry.get("document_type", "General Paperwork")
    category = classify_category(doc_type)

    row = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Category": category,
        "Type": doc_type,
        "Name": entry.get("student_or_vendor_name", "N/A"),
        "ID/Ref": entry.get("identifier_number", "N/A"),
        "Branch": entry.get("department_or_branch", "General"),
        "Academic Metric": entry.get("academic_metric", "N/A"),
        "Amount (INR)": entry.get("primary_amount", 0.0),
        "Status": status
    }
    
    new_df = pd.DataFrame([row])
    
    if os.path.exists(DATA_FILE):
        existing_df = pd.read_excel(DATA_FILE)
        if "Category" not in existing_df.columns:
            existing_df["Category"] = existing_df["Type"].apply(classify_category)
        combined = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined = new_df
        
    combined.to_excel(DATA_FILE, index=False)
    return True

def get_ledger_dataframe(category: str = None) -> pd.DataFrame:
    cols = ["Timestamp", "Category", "Type", "Name", "ID/Ref", "Branch", "Academic Metric", "Amount (INR)", "Status"]
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=cols)

    df = pd.read_excel(DATA_FILE)
    if "Category" not in df.columns:
        df["Category"] = df["Type"].apply(classify_category)

    if category and category != "All":
        return df[df["Category"] == category]
    return df