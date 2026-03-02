from pydantic import BaseModel, Field, ValidationError
from typing import List
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3"  

class StructuredSummary(BaseModel):
    patient_name: str
    patient_id: int
    active_claims: int
    total_claims: int
    last_order_status: str
    key_flags: List[str] = Field(default_factory=list)

class LLMResponse(BaseModel):
    text_summary: str
    structured: StructuredSummary
    meta: dict

SYSTEM_PROMPT = """You are a healthcare summarization assistant.
Use ONLY the provided JSON context.
Do NOT invent or assume anything.
If a field is missing, use "unknown" or 0 and record it in missing_fields.
Return VALID JSON only. No extra text.
Do NOT wrap it in markdown.
Do NOT include any explanation or extra text.
The first character must be { and the last character must be }.
"""

def build_user_prompt(context_json: dict) -> str:
    schema = {
        "text_summary": "string",
        "structured": {
            "patient_name": "string",
            "patient_id": "number",
            "active_claims": "number",
            "total_claims": "number",
            "last_order_status": "string",
            "key_flags": ["string"]
        },
        "meta": {
            "source": "llm",
            "missing_fields": ["string"]
        }
    }

    return f"""Create:
1) a clean text summary for an agent (1-3 lines)
2) a structured JSON object exactly matching the schema

Context JSON:
{json.dumps(context_json, indent=2)}

Schema:
{json.dumps(schema, indent=2)}
"""

LLM_JSON_SCHEMA = {
    "name": "Patient360Summary",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": ["text_summary", "structured", "meta"],
        "properties": {
            "text_summary": {"type": "string"},
            "structured": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "patient_name",
                    "patient_id",
                    "active_claims",
                    "total_claims",
                    "last_order_status",
                    "key_flags",
                ],
                "properties": {
                    "patient_name": {"type": "string"},
                    "patient_id": {"type": "integer"},
                    "active_claims": {"type": "integer"},
                    "total_claims": {"type": "integer"},
                    "last_order_status": {"type": "string"},
                    "key_flags": {"type": "array", "items": {"type": "string"}},
                },
            },
            "meta": {
                "type": "object",
                "additionalProperties": False,
                "required": ["source", "missing_fields"],
                "properties": {
                    "source": {"type": "string"},
                    "missing_fields": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    },
}

def call_llm(system_prompt: str, user_prompt: str) -> str:

    payload = {
        "model": OLLAMA_MODEL,
        "messages":[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}            
        ],
        "options":{
            "temperature":0.2
        },
        "stream": False
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=60)
    r.raise_for_status()

    data = r.json()
    return data["message"]["content"]

    # return json.dumps({
    #     "text_summary": "Patient summary generated. (Replace mock with real LLM call.)",
    #     "structured": {
    #         "patient_name": "unknown",
    #         "patient_id": 0,
    #         "active_claims": 0,
    #         "total_claims": 0,
    #         "last_order_status": "unknown",
    #         "key_flags": []
    #     },
    #     "meta": {
    #         "source": "llm",
    #         "missing_fields": ["patient_name", "patient_id", "active_claims", "total_claims", "last_order_status"]
    #     }
    # })

def generate_summary(context_json: dict) -> dict:

    user_prompt = build_user_prompt(context_json)
    raw = call_llm(SYSTEM_PROMPT, user_prompt)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "text_summary": "Unable to generate summary (invalid model output).",
            "structured": {
                "patient_name": context_json.get("patient_name", "unknown"),
                "patient_id": int(context_json.get("patient_id", 0) or 0),
                "active_claims": int(context_json.get("active_claims", 0) or 0),
                "total_claims": int(context_json.get("total_claims", 0) or 0),
                "last_order_status": context_json.get("last_order_status", "unknown"),
                "key_flags": ["llm_output_invalid_json"]
            },
            "meta": {
                "source": "fallback",
                "missing_fields": []
            }
        }
    
    try:
        validated = LLMResponse.model_validate(parsed)
        return validated.model_dump()
    
    except ValidationError as e:
        return {
            "text_summary": "Unable to generate summary (schema mismatch).",
            "structured": {
                "patient_name": context_json.get("patient_name", "unknown"),
                "patient_id": int(context_json.get("patient_id", 0) or 0),
                "active_claims": int(context_json.get("active_claims", 0) or 0),
                "total_claims": int(context_json.get("total_claims", 0) or 0),
                "last_order_status": context_json.get("last_order_status", "unknown"),
                "key_flags": ["llm_output_schema_mismatch"]
            },
            "meta": {
                "source": "fallback",
                "missing_fields": []
            }
        }