import json
import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("AQ.Ab8RN6Iv0p9oZxRnIPiw9QHaAeTx4sQ4cQ3djBXSfoJX5UC0DA"))

DOCUMENT_EXTRACTION_PROMPT = """
You are an expert registrar and financial auditor for a higher education campus.
Analyze this scanned physical document, photo, or certificate.

Identify the exact nature of the paperwork dynamically based on its title and layout.

Extract and normalize the following data points into strict, raw JSON:
{
  "document_type": "Exact detected document title (e.g., 'Marks Memo', 'Degree Certificate', 'Bank Challan', 'Fee Receipt', 'Transfer Certificate', 'Purchase Invoice')",
  "student_or_vendor_name": "Full name of the student or vendor/payee, or 'N/A'",
  "identifier_number": "Hall Ticket / Roll / Application / Challan / Invoice number",
  "primary_amount": 0.0,
  "academic_metric": "Marks, Grade, CGPA, or Percentage (with totals if available, e.g., '1471/2500 (58.84%)'), else 'N/A'",
  "department_or_branch": "Course/Department found (e.g., 'B.Sc Sciences', 'B.Tech CSE'), or 'General'",
  "verification_flags": ["List any issues like blurred text, missing signature, stamp, or mismatched data"],
  "is_valid": true
}

Return ONLY the raw JSON object. Do not include markdown code fences, backticks, or explanatory text.
"""

def extract_document_data(image_path: str, max_retries: int = 5) -> dict:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    target_model = "gemini-3.6-flash"

    for attempt in range(1, max_retries + 1):
        try:
            print(f"AI ప్రాసెసింగ్ ప్రయత్నం {attempt}/{max_retries}...")
            response = client.models.generate_content(
                model=target_model,
                contents=[
                    DOCUMENT_EXTRACTION_PROMPT,
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                ]
            )
            clean_output = response.text.strip()
            if clean_output.startswith("```json"):
                clean_output = clean_output[7:]
            if clean_output.endswith("```"):
                clean_output = clean_output[:-3]
            clean_output = clean_output.strip()

            return json.loads(clean_output)

        except Exception as e:
            err_str = str(e)
            print(f"హెచ్చరిక: ప్రయత్నం {attempt} లో సమస్య ({err_str[:60]}...)")
            
            # 503 రద్దీ లేదా రేట్ లిమిట్ వస్తే కొన్ని సెకన్లు ఆగి రీట్రై చేస్తుంది
            if ("503" in err_str or "429" in err_str or "UNAVAILABLE" in err_str) and attempt < max_retries:
                wait_time = attempt * 3
                print(f"సర్వర్ బిజీగా ఉంది. {wait_time} సెకన్లు ఆగి మళ్లీ ప్రయత్నిస్తున్నాం...")
                time.sleep(wait_time)
                continue
            elif attempt == max_retries:
                # అన్ని ప్రయత్నాలు ముగిసినా ఫెయిల్ అయితే బ్యాకప్ స్ట్రక్చర్ ఇస్తుంది
                return {
                    "document_type": "Manual Review Needed",
                    "student_or_vendor_name": "Check Document",
                    "identifier_number": "N/A",
                    "primary_amount": 0.0,
                    "academic_metric": "N/A",
                    "department_or_branch": "General",
                    "verification_flags": ["Temporary Google Server Spike. Please retry."],
                    "is_valid": False
                }
            raise e