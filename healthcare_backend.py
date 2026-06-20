from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


MEDICAL_DOCUMENTS = [
    """
    Condition: Fever
    Symptoms: high body temperature, body pain, headache
    Description: Fever is a temporary increase in body temperature, often due to infection.
    OTC Medication: Paracetamol
    Safety Notes: Avoid overdose. Consult a doctor if fever lasts more than 3 days.
    """.strip(),
    """
    Condition: Headache
    Symptoms: head pain, pressure, mild dizziness
    Description: Headache may occur due to stress, dehydration, or lack of sleep.
    OTC Medication: Paracetamol
    Safety Notes: Seek medical attention if severe or persistent.
    """.strip(),
    """
    Condition: Acidity
    Symptoms: stomach burning, acid reflux, indigestion
    Description: Acidity occurs due to excess stomach acid.
    OTC Medication: Antacids
    Safety Notes: Avoid spicy food. Consult a doctor if frequent.
    """.strip(),
    """
    Condition: Common Cold
    Symptoms: runny nose, sneezing, sore throat
    Description: Common cold is a viral infection affecting the nose and throat.
    OTC Medication: Cetirizine, Paracetamol
    Safety Notes: Rest and hydration are recommended.
    """.strip(),
]

OTC_MEDICATIONS = {"paracetamol", "antacids", "ors", "cetirizine"}

BLOCKED_MEDICATION_KEYWORDS = {
    "sleeping pill",
    "sleeping pills",
    "antibiotic",
    "antibiotics",
    "painkiller",
    "opioid",
    "steroid",
    "antidepressant",
    "antipsychotic",
    "sedative",
    "benzodiazepine",
}

HIGH_RISK_SYMPTOMS = {
    "chest pain",
    "shortness of breath",
    "difficulty breathing",
    "breathlessness",
    "seizure",
    "unconscious",
    "pregnancy",
    "suicidal",
    "severe bleeding",
}

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

SYMPTOM_QUESTIONS = {
    "fever": [
        "How long have you had the fever?",
        "Do you also have body pain or headache?",
        "Have you measured your temperature?",
    ],
    "headache": [
        "Where exactly is the headache located?",
        "How severe is the headache?",
        "Have you been under stress or had poor sleep recently?",
    ],
    "acidity": [
        "Do you feel burning in your stomach or chest?",
        "Did you eat spicy or oily food recently?",
        "Is the discomfort worse after meals?",
    ],
    "cold": [
        "Do you have a runny nose or sneezing?",
        "Do you have a sore throat?",
        "Do you feel body weakness?",
    ],
    "body pain": [
        "Is the pain affecting your whole body or one area?",
        "Did this start after fever, strain, or physical activity?",
        "Do you also feel weakness or tiredness?",
    ],
}


@dataclass
class InterviewState:
    symptom: Optional[str] = None
    questions: List[str] = field(default_factory=list)
    answers: List[str] = field(default_factory=list)
    current_question: int = 0

    def reset(self) -> None:
        self.symptom = None
        self.questions = []
        self.answers = []
        self.current_question = 0


def tokenize(text: str) -> set[str]:
    return {word.strip(".,!?").lower() for word in text.split() if word.strip()}


def search_medical_knowledge(query: str, top_k: int = 2) -> List[str]:
    query_tokens = tokenize(query)
    scored_docs = []

    for doc in MEDICAL_DOCUMENTS:
        doc_tokens = tokenize(doc)
        overlap = len(query_tokens & doc_tokens)
        scored_docs.append((overlap, doc))

    scored_docs.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in scored_docs[:top_k]]


def medication_safety_check(user_input: str, retrieved_docs: List[str]) -> Dict[str, object]:
    text = user_input.lower()

    for symptom in HIGH_RISK_SYMPTOMS:
        if symptom in text:
            return {
                "status": "ESCALATE",
                "reason": "High-risk symptoms detected",
                "action": "Doctor intervention required",
            }

    for keyword in BLOCKED_MEDICATION_KEYWORDS:
        if keyword in text:
            return {
                "status": "ESCALATE",
                "reason": "Prescription or dangerous medication request detected",
                "action": "Doctor intervention required",
            }

    safe_meds = []
    for doc in retrieved_docs:
        lower_doc = doc.lower()
        for med in OTC_MEDICATIONS:
            if med in lower_doc:
                safe_meds.append(med.title())

    return {
        "status": "SAFE",
        "medications": sorted(set(safe_meds)),
        "action": "OTC medication guidance allowed" if safe_meds else "General advice only",
    }


def classify_risk(user_input: str) -> str:
    text = user_input.lower()

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


def build_llm_context(retrieved_docs: List[str]) -> str:
    return "\n\n".join(retrieved_docs)


def simulated_llm_response(context: str, user_query: str) -> str:
    lower_query = user_query.lower()

    if "fever" in lower_query:
        return (
            "Your symptoms may fit a mild viral illness. Stay hydrated, rest well, "
            "and monitor your temperature. Seek medical care if the fever continues "
            "for more than 3 days or becomes high."
        )

    if "headache" in lower_query:
        return (
            "This may be a mild headache related to stress, dehydration, or poor sleep. "
            "Rest, fluids, and light activity reduction may help."
        )

    if "acidity" in lower_query:
        return (
            "This looks consistent with acidity or indigestion. Avoid oily and spicy food, "
            "eat lighter meals, and monitor whether the discomfort worsens after eating."
        )

    if "cold" in lower_query or "runny nose" in lower_query:
        return (
            "These symptoms may be consistent with a common cold. Rest, hydration, and "
            "symptom monitoring are usually helpful."
        )

    return (
        "Based on the available knowledge base, your symptoms appear to be low to moderate risk. "
        "Use only safe OTC guidance and consult a doctor if symptoms worsen or do not improve."
    )


def doctor_escalation_handler(reason: str) -> Dict[str, str]:
    return {
        "status": "ESCALATE",
        "message": "This situation needs professional medical supervision.",
        "next_step": "Please contact a certified doctor or nearby emergency service.",
        "reason": reason,
    }


def ai_healthcare_pipeline(user_query: str) -> Dict[str, object]:
    risk = classify_risk(user_query)

    if risk == "SEVERE":
        return doctor_escalation_handler("Severe risk detected from symptoms")

    retrieved_docs = search_medical_knowledge(user_query)
    safety_result = medication_safety_check(user_query, retrieved_docs)

    if safety_result["status"] == "ESCALATE":
        return doctor_escalation_handler(str(safety_result["reason"]))

    context = build_llm_context(retrieved_docs)
    llm_text = simulated_llm_response(context, user_query)

    return {
        "status": "SAFE",
        "risk_level": risk,
        "response": llm_text,
        "safe_medications": safety_result.get("medications", []),
        "retrieved_docs": retrieved_docs,
        "note": "This is decision support only, not a medical diagnosis.",
    }


def detect_primary_symptom(user_input: str) -> Optional[str]:
    text = user_input.lower()

    symptom_keywords = {
        "fever": ["fever", "temperature"],
        "headache": ["headache", "head pain"],
        "acidity": ["acidity", "acid reflux", "burning stomach"],
        "cold": ["cold", "runny nose", "sneezing", "sore throat"],
        "body pain": ["body pain", "muscle pain"],
    }

    for symptom, keywords in symptom_keywords.items():
        if any(keyword in text for keyword in keywords):
            return symptom

    return None


def start_interview(user_query: str, state: InterviewState) -> str:
    symptom = detect_primary_symptom(user_query)

    if symptom is None:
        return "Please describe your symptoms in a bit more detail so I can guide you safely."

    state.symptom = symptom
    state.questions = SYMPTOM_QUESTIONS[symptom]
    state.answers = []
    state.current_question = 0

    return state.questions[0]


def answer_question(user_answer: str, state: InterviewState) -> str:
    state.answers.append(user_answer)
    state.current_question += 1

    if state.current_question < len(state.questions):
        return state.questions[state.current_question]

    return "Thank you. Analyzing your symptoms..."


def healthcare_chat(user_input: str, state: InterviewState) -> Dict[str, object]:
    if state.symptom is None:
        return {
            "stage": "INTERVIEW",
            "message": start_interview(user_input, state),
            "question_number": state.current_question + 1 if state.questions else 0,
            "total_questions": len(state.questions),
        }

    response = answer_question(user_input, state)

    if response == "Thank you. Analyzing your symptoms...":
        full_query = f"{state.symptom} {' '.join(state.answers)}".strip()
        result = ai_healthcare_pipeline(full_query)
        state.reset()
        return {"stage": "RESULT", "analysis": result}

    return {
        "stage": "INTERVIEW",
        "message": response,
        "question_number": state.current_question + 1,
        "total_questions": len(state.questions),
    }
