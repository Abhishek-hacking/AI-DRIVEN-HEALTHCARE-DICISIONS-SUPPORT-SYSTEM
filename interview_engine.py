from __future__ import annotations

from uuid import uuid4

from backend_models import InterviewSession


SYMPTOM_QUESTIONS = {
    "fever": [
        "How long have you had the fever?",
        "Do you also have body pain or headache?",
        "Have you measured your temperature?",
    ],
    "headache": [
        "Where exactly is the headache located?",
        "How severe is the headache?",
        "Have you had stress or poor sleep recently?",
    ],
    "acidity": [
        "Do you feel burning in the stomach or chest?",
        "Did you eat spicy or oily food recently?",
        "Is the discomfort worse after meals?",
    ],
    "cold": [
        "Do you have a runny nose or sneezing?",
        "Do you have a sore throat?",
        "Do you feel weakness or tiredness?",
    ],
}


def detect_primary_symptom(user_input: str) -> str | None:
    text = user_input.lower()
    symptom_keywords = {
        "fever": ["fever", "temperature"],
        "headache": ["headache", "head pain"],
        "acidity": ["acidity", "acid reflux", "stomach burning"],
        "cold": ["cold", "runny nose", "sneezing", "sore throat", "cough"],
    }
    for symptom, keywords in symptom_keywords.items():
        if any(keyword in text for keyword in keywords):
            return symptom
    return None


def start_interview(user_input: str) -> InterviewSession:
    symptom = detect_primary_symptom(user_input)
    questions = SYMPTOM_QUESTIONS.get(symptom or "", [])
    return InterviewSession(
        session_id=str(uuid4()),
        initial_input=user_input,
        symptom=symptom,
        questions=questions,
        answers=[],
        current_index=0,
    )


def append_answer(session: InterviewSession, answer: str) -> InterviewSession:
    session.answers.append(answer)
    session.current_index += 1
    return session
