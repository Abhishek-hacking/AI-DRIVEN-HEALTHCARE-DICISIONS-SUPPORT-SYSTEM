from __future__ import annotations

from typing import Iterable

from medical_knowledge import MedicalDocument


ALLOWED_OTC = {"paracetamol", "antacids", "ors", "cetirizine"}
BLOCKED_MEDICATIONS = {
    "sleeping pill",
    "sleeping pills",
    "antibiotic",
    "antibiotics",
    "opioid",
    "steroid",
    "antidepressant",
    "prescription",
    "painkiller",
}
HIGH_RISK_SYMPTOMS = {
    "chest pain",
    "shortness of breath",
    "difficulty breathing",
    "breathlessness",
    "seizure",
    "unconscious",
    "severe bleeding",
    "pregnancy",
}


def evaluate_safety(user_text: str, retrieved_docs: Iterable[MedicalDocument], confidence: int) -> dict:
    text = user_text.lower()

    for symptom in HIGH_RISK_SYMPTOMS:
        if symptom in text:
            return {
                "allowed": False,
                "reason": "High-risk symptoms detected",
                "status": "doctor_required",
            }

    for keyword in BLOCKED_MEDICATIONS:
        if keyword in text:
            return {
                "allowed": False,
                "reason": "Prescription or unsafe medication request detected",
                "status": "doctor_required",
            }

    if confidence < 60:
        return {
            "allowed": False,
            "reason": "Low confidence - requires doctor review",
            "status": "doctor_required",
        }

    allowed_meds = []
    for doc in retrieved_docs:
        for med in doc.otc_medications:
            if med.lower() in ALLOWED_OTC:
                allowed_meds.append(med)

    return {
        "allowed": True,
        "status": "ok",
        "medication": sorted(set(allowed_meds)),
    }
