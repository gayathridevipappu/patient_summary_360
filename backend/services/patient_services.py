from pathlib import Path
from fastapi import HTTPException
import json

DATA_DIR = Path(__file__).resolve().parent.parent/"data"

def load_patient(patient_id: int) -> dict:
    file_path = DATA_DIR/f"patient_{patient_id}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="patient not found")
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="patient file is corrupted")
    
def build_patient360(patient: dict) -> dict:

    demographics = patient.get("demographics", {})
    claims = patient.get("claims", [])
    orders = patient.get("orders", [])

    active_claims = sum(1 for c in claims if c.get("status") == "ACTIVE")
    total_claims = len(claims)

    last_order_status = "unknown"
    if orders:
        last_order_status = orders[-1].get("status", "unknown")
    
    return {
        "patient_id": patient.get("id", 0),
        "patient_name": demographics.get("name", "unknown"),
        "age": demographics.get("age", "unknown"),
        "gender": demographics.get("gender", "unknown"),
        "total_claims": total_claims,
        "active_claims": active_claims,
        "last_order_status": last_order_status,
        "claims": claims,
        "orders": orders,
    }