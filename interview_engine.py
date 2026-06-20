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
    "cough": [
        "Is the cough dry or with mucus?",
        "Do you also have fever or sore throat?",
        "Is the cough worse at night or after cold exposure?",
    ],
    "sore_throat": [
        "How long have you had the sore throat?",
        "Is it painful to swallow?",
        "Do you also have fever, cough, or runny nose?",
    ],
    "allergy": [
        "Do you have sneezing with itchy nose or eyes?",
        "Is this worse around dust, weather change, or strong smells?",
        "Do you have breathing difficulty or wheezing?",
    ],
    "stomach_pain": [
        "Where exactly is the stomach pain located?",
        "Did the pain start after meals or outside food?",
        "Do you also have vomiting, loose stools, or acidity?",
    ],
    "diarrhea": [
        "How many loose stools have you had today?",
        "Are you able to drink fluids normally?",
        "Do you also have fever, vomiting, or stomach cramps?",
    ],
    "nausea": [
        "How long have you felt nauseated?",
        "Have you vomited or only felt like vomiting?",
        "Are you able to keep fluids down?",
    ],
    "dehydration": [
        "Do you feel dry mouth, dizziness, or reduced urination?",
        "Have you had fever, vomiting, diarrhea, or low fluid intake?",
        "Are you able to drink ORS or water comfortably?",
    ],
    "body_pain": [
        "Is the body pain generalized or limited to one area?",
        "Did it start after fever, strain, or poor sleep?",
        "Do you also feel weakness or tiredness?",
    ],
    "weakness": [
        "How long have you felt weakness or low energy?",
        "Did it begin after fever, poor sleep, stress, or low food intake?",
        "Do you also feel dizziness, dry mouth, or body pain?",
    ],
    "dizziness": [
        "Is the dizziness mild, moderate, or severe?",
        "Did it happen after low food intake, fever, or dehydration?",
        "Do you also have weakness, vomiting, or headache?",
    ],
}


def detect_primary_symptom(user_input: str) -> str | None:
    text = user_input.lower()
    symptom_keywords = {
        "fever": ["fever", "temperature", "high temperature", "feeling hot", "chills"],
        "headache": ["headache", "head pain", "head heaviness", "pressure in head"],
        "acidity": ["acidity", "acid reflux", "stomach burning", "heartburn", "chest burning after meals"],
        "cold": ["cold", "runny nose", "sneezing", "nasal congestion", "stuffy nose"],
        "cough": ["cough", "dry cough", "mild cough", "throat tickle"],
        "sore_throat": ["sore throat", "throat pain", "pain while swallowing", "scratchy throat"],
        "allergy": ["allergy", "allergic cold", "itchy nose", "itchy eyes", "watery eyes", "dust allergy"],
        "stomach_pain": ["stomach pain", "stomach discomfort", "stomach irritation", "gastric discomfort"],
        "diarrhea": ["diarrhea", "loose stools", "watery stool", "frequent stool"],
        "nausea": ["nausea", "queasy", "uneasy stomach", "feeling like vomiting"],
        "dehydration": ["dehydration", "dry mouth", "reduced urination", "lightheadedness"],
        "body_pain": ["body pain", "body ache", "muscle pain", "generalized pain"],
        "weakness": ["weakness", "low energy", "fatigue", "tiredness", "lack of energy"],
        "dizziness": ["dizziness", "lightheadedness", "feeling dizzy"],
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
