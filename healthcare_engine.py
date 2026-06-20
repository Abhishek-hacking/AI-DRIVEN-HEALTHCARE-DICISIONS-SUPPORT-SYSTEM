from __future__ import annotations

from backend_models import ResultPayload
from knowledge_base import MedicalKnowledgeBase
from llm_client import LocalHealthcareLLM
from medical_knowledge import MedicalDocument
from safety_engine import evaluate_safety


MILD_SYMPTOMS = {"fever", "headache", "cold", "cough", "acidity", "body pain", "runny nose"}
MODERATE_SYMPTOMS = {"persistent fever", "vomiting", "severe headache", "diarrhea", "dizziness"}
SEVERE_SYMPTOMS = {
    "chest pain",
    "shortness of breath",
    "difficulty breathing",
    "breathlessness",
    "seizure",
    "unconscious",
    "severe bleeding",
    "pregnancy",
}


def classify_risk(user_text: str) -> str:
    text = user_text.lower()
    for symptom in SEVERE_SYMPTOMS:
        if symptom in text:
            return "SEVERE"
    for symptom in MODERATE_SYMPTOMS:
        if symptom in text:
            return "MODERATE"
    for symptom in MILD_SYMPTOMS:
        if symptom in text:
            return "MILD"
    return "UNKNOWN"


def estimate_confidence(user_text: str, documents: list[MedicalDocument]) -> int:
    text = user_text.lower()
    if not documents:
        return 40
    matches = 0
    for doc in documents:
        if any(symptom in text for symptom in doc.symptoms):
            matches += 1
    return min(95, 55 + matches * 15)


def generate_advice(condition: str | None, risk_level: str) -> str:
    if risk_level == "MODERATE":
        return "Monitor symptoms closely, rest, stay hydrated, and seek medical review if symptoms continue."
    if condition == "Fever":
        return "Rest, stay hydrated, and monitor temperature."
    if condition == "Headache":
        return "Rest, hydrate well, and reduce stress or screen exposure."
    if condition == "Acidity":
        return "Avoid spicy or oily food, eat lighter meals, and stay upright after eating."
    if condition == "Common Cold":
        return "Rest, fluids, and symptom monitoring are recommended."
    return "Use only safe general care and consult a doctor if symptoms worsen."


class HealthcareDecisionEngine:
    def __init__(self, knowledge_base: MedicalKnowledgeBase | None = None) -> None:
        self.knowledge_base = knowledge_base or MedicalKnowledgeBase()
        self.llm = LocalHealthcareLLM()

    def analyze(self, user_text: str) -> ResultPayload:
        risk_level = classify_risk(user_text)
        if risk_level == "SEVERE":
            return ResultPayload(
                status="doctor_required",
                reason="Severe risk detected from symptoms",
                note="Doctor intervention required",
            )

        retrieved = self.knowledge_base.search(user_text, top_k=2)
        confidence = estimate_confidence(user_text, retrieved)
        safety = evaluate_safety(user_text, retrieved, confidence)

        if not safety["allowed"]:
            return ResultPayload(
                status="doctor_required",
                reason=safety["reason"],
                note="Doctor intervention required",
                confidence=confidence,
            )

        primary = retrieved[0] if retrieved else None
        advice = generate_advice(primary.condition if primary else None, risk_level)
        llm_response, llm_backend = self.llm.generate_response(
            user_query=user_text,
            documents=retrieved,
            condition=primary.condition if primary else None,
            risk_level=risk_level,
            advice=advice,
        )
        return ResultPayload(
            status="ok",
            risk_level=risk_level,
            condition=primary.condition if primary else "Unknown condition",
            confidence=confidence,
            medication=safety["medication"],
            advice=llm_response,
            note=(
                "This is a decision support response, not a diagnosis. "
                f"Retrieval backend: {self.knowledge_base.backend_name()}. "
                f"LLM backend: {llm_backend}."
            ),
            knowledge=[doc.to_text() for doc in retrieved],
        )
