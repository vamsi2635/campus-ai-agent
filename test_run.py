from core.extractor import extract_document_data
from core.database import record_entry

data = extract_document_data("test.jpg")
print("Extracted Data:", data)
record_entry(data, status="Verified")
print("Saved to campus_ledger.xlsx successfully.")