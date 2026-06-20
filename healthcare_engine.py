from __future__ import annotations

from backend_models import ResultPayload
from knowledge_base import MedicalKnowledgeBase
from llm_client import LocalHealthcareLLM
from medical_knowledge import MedicalDocument
from safety_engine import evaluate_safety


MILD_SYMPTOMS = {
    "fever",
    "mild fever",
    "headache",
    "cold",
    "common cold",
    "cough",
    "dry cough",
    "acidity",
    "acid reflux",
    "heartburn",
    "body pain",
    "body ache",
    "runny nose",
    "sneezing",
    "stuffy nose",
    "nasal congestion",
    "sore throat",
    "indigestion",
    "bloating",
    "mild stomach discomfort",
    "nausea",
    "low energy",
    "fatigue",
    "tiredness",
    "weakness",
}
MODERATE_SYMPTOMS = {
    "persistent fever",
    "high fever",
    "vomiting",
    "repeated vomiting",
    "severe headache",
    "diarrhea",
    "loose stools",
    "watery stool",
    "dizziness",
    "moderate dizziness",
    "stomach pain",
    "persistent cough",
    "sinus pressure",
    "facial pain",
    "dehydration",
    "dry mouth",
    "reduced urination",
    "pain while swallowing",
    "worsening weakness",
}
SEVERE_SYMPTOMS = {
    "chest pain",
    "shortness of breath",
    "difficulty breathing",
    "breathlessness",
    "wheezing",
    "severe dehydration",
    "fainting",
    "confusion",
    "blood in stool",
    "black stool",
    "vomiting blood",
    "coughing blood",
    "one sided weakness",
    "vision loss",
    "unable to drink fluids",
    "unable to keep fluids down",
    "very high fever",
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
    if condition == "Viral Fever":
        return "Prioritize fluids, rest, temperature monitoring, and simple supportive care."
    if condition == "Headache":
        return "Rest, hydrate well, and reduce stress or screen exposure."
    if condition == "Tension Headache":
        return "Rest, hydrate well, reduce screen exposure, and try to improve sleep and stress control."
    if condition == "Acidity":
        return "Avoid spicy or oily food, eat lighter meals, and stay upright after eating."
    if condition == "Indigestion":
        return "Eat light meals, avoid heavy or oily food, and observe whether symptoms improve after rest."
    if condition == "Stomach Irritation":
        return "Prefer bland food, avoid triggers, stay hydrated, and monitor for worsening pain."
    if condition == "Common Cold":
        return "Rest, fluids, and symptom monitoring are recommended."
    if condition == "Allergic Rhinitis":
        return "Avoid likely triggers such as dust and use only safe supportive care if symptoms are mild."
    if condition == "Sore Throat":
        return "Rest your voice, stay hydrated, and monitor swallowing difficulty or worsening discomfort."
    if condition == "Mild Cough":
        return "Stay hydrated, avoid irritants, and monitor whether the cough becomes persistent or more severe."
    if condition == "Sinus Congestion":
        return "Rest, hydration, and monitoring of nasal and facial symptoms are recommended."
    if condition == "Body Pain":
        return "Rest, fluids, and monitoring for worsening pain or weakness are recommended."
    if condition == "Mild Dehydration":
        return "Increase fluids carefully, consider ORS, and watch for worsening dizziness or poor urine output."
    if condition == "Mild Diarrhea":
        return "Focus on fluids and ORS, eat light food, and monitor for worsening frequency or weakness."
    if condition == "Nausea":
        return "Take small sips of fluids, avoid heavy meals, and monitor whether vomiting develops."
    if condition == "Fatigue and Weakness":
        return "Rest, hydration, light nutrition, and monitoring for new symptoms are recommended."
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
