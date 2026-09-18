import os
import json
from google import genai
from dotenv import load_dotenv
from core.database import get_ledger_dataframe

load_dotenv()
client = genai.Client(api_key=os.getenv("AQ.Ab8RN6LRrh7yNsE57OXdmEdlndZ0cUsHuPg6Z7SrWs8GSZLihA"))

def answer_campus_query(question: str, module_scope: str = "All") -> str:
    """Answers inquiries tailored to a specific module or the entire campus."""
    df = get_ledger_dataframe(category=module_scope)
    
    if df.empty:
        return f"Currently, there are no recorded entries under the '{module_scope}' scope in the ledger."

    records_summary = df.to_dict(orient="records")

    prompt = f"""
    You are the Executive Campus AI Voice Officer for institutional leadership.
    Scope of Inquiry: {module_scope.upper()}
    Verified Ledger Records:
    {json.dumps(records_summary, default=str)}

    User Query: {question}

    Instructions:
    1. Answer directly and concisely based strictly on the verified data above.
    2. If the user asks in Telugu / Telugu English (e.g., 'motham enni records vunnayi?'), respond in clear, easy Telugu or clear bilingual tone as appropriate.
    3. Include accurate counts, names, roll numbers, or financial amounts where requested.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[prompt]
        )
        return response.text.strip()
    except Exception as e:
        return f"Analysis error: {str(e)}"