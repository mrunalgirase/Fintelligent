from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"  # Can be changed to "mistral"

class FinancialLiteracyResponse(BaseModel):
    sip: dict
    emergency_fund: dict
    upi_overspending: dict
    credit_card: dict
    emi: dict

SYSTEM_PROMPT = """
You are an expert India-focused Financial Literacy Coach. 
Your goal is to educate Indian students and early professionals about financial concepts using local context.

INSTRUCTIONS:
1. Explain the following topics: SIP, Emergency Fund, UPI Overspending, Credit Card Traps, EMI Culture.
2. Use SIMPLE, clear language.
3. Use '₹' for all currency examples.
4. Mention relevant Indian context (e.g., 'chai', 'auto rides', 'Amazon Sale', 'Big Billion Days', 'Zomato').
5. For each topic, provide:
    - "explanation": Brief concept explanation (2-3 sentences).
    - "example": A relatable scenario with numbers in ₹.
    - "habit_action": ONE actionable habit to start today.
6. Return the result as strict JSON with keys: 'sip', 'emergency_fund', 'upi_overspending', 'credit_card', 'emi'.
7. Do NOT include any markdown formatting (like ```json), just the raw JSON object.

Example Structure for one key (e.g., 'sip'):
{
    "explanation": "...",
    "example": "...",
    "habit_action": "..."
}
"""

@app.post("/ai/financial-literacy")
async def get_financial_literacy_tips():
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": "Generate the financial literacy guide now.",
            "system": SYSTEM_PROMPT,
            "stream": False,
            "format": "json" 
        }
        
        # Note: 'format': 'json' ensures Ollama tries to enforce JSON mode if supported by the model version.
        # Otherwise, the prompt's instruction is the primary driver.

        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        
        data = response.json()
        raw_response = data.get("response", "")
        
        # Parse the JSON content from the LLM
        try:
            structured_data = json.loads(raw_response)
        except json.JSONDecodeError:
            # Fallback if model returns text around the JSON
            # This is a basic cleanup, primarily for models that might chat before the JSON
            # Ideally, a regex could extract the { ... } block
            raise HTTPException(status_code=500, detail="Failed to parse valid JSON from AI model.")

        return structured_data

    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Ollama is not running. Please run 'ollama serve' or check OLLAMA_SETUP.md.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
