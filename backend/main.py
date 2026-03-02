from pydantic import BaseModel
from fastapi import FastAPI
from services.patient_services import load_patient, build_patient360
from services.llm_service import generate_summary

class PatientSummaryRequest(BaseModel):
    patient_id: int

app = FastAPI()

@app.post("/patient360/summary")
def patient360_summary(req: PatientSummaryRequest):

    patient = load_patient(req.patient_id)
    
    context = build_patient360(patient)

    result = generate_summary(context)

    return result
