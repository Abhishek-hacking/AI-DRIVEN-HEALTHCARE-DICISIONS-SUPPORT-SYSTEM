from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class MedicalDocument:
    condition: str
    symptoms: List[str]
    description: str
    otc_medications: List[str]
    safety_notes: str

    def to_text(self) -> str:
        return (
            f"Condition: {self.condition}\n"
            f"Symptoms: {', '.join(self.symptoms)}\n"
            f"Description: {self.description}\n"
            f"OTC Medication: {', '.join(self.otc_medications)}\n"
            f"Safety Notes: {self.safety_notes}"
        )


MEDICAL_DOCUMENTS = [
    MedicalDocument(
        condition="Fever",
        symptoms=[
            "fever",
            "high temperature",
            "temperature",
            "body pain",
            "headache",
            "chills",
            "warm body",
            "feeling hot",
        ],
        description="Fever is commonly linked to infection or inflammation and should be monitored over time along with hydration and rest.",
        otc_medications=["Paracetamol"],
        safety_notes="Consult a doctor if fever lasts more than 3 days, becomes very high, or is associated with confusion, breathing trouble, or severe weakness.",
    ),
    MedicalDocument(
        condition="Viral Fever",
        symptoms=[
            "viral fever",
            "fever with body ache",
            "fatigue",
            "body pain",
            "low appetite",
            "weakness",
        ],
        description="Viral fever often causes fever, weakness, generalized body ache, and tiredness that improve gradually with rest and fluids.",
        otc_medications=["Paracetamol", "ORS"],
        safety_notes="Seek doctor review if symptoms are worsening, fever is persistent, vomiting prevents fluids, or signs of dehydration appear.",
    ),
    MedicalDocument(
        condition="Headache",
        symptoms=[
            "headache",
            "head pain",
            "pressure",
            "mild dizziness",
            "forehead pain",
            "whole head pain",
            "head heaviness",
        ],
        description="Headache may be associated with stress, dehydration, poor sleep, eye strain, or minor illness.",
        otc_medications=["Paracetamol"],
        safety_notes="Seek medical attention if headache is severe, sudden, persistent, associated with vomiting, fainting, vision change, or weakness.",
    ),
    MedicalDocument(
        condition="Tension Headache",
        symptoms=[
            "tension headache",
            "band like headache",
            "stress headache",
            "tightness around head",
            "poor sleep",
            "screen strain",
        ],
        description="Tension headache commonly presents as a pressing or tight headache and may be related to stress, poor posture, or lack of sleep.",
        otc_medications=["Paracetamol"],
        safety_notes="If headaches become frequent, unusually severe, or interfere with daily activities, a doctor evaluation is recommended.",
    ),
    MedicalDocument(
        condition="Acidity",
        symptoms=[
            "acidity",
            "acid reflux",
            "stomach burning",
            "indigestion",
            "chest burning after meals",
            "sour burps",
            "heartburn",
        ],
        description="Acidity can occur because of excess stomach acid, irregular meals, or food triggers such as spicy or oily food.",
        otc_medications=["Antacids"],
        safety_notes="Avoid spicy or oily food and late-night meals. Consult a doctor if symptoms are frequent, severe, or associated with vomiting or weight loss.",
    ),
    MedicalDocument(
        condition="Indigestion",
        symptoms=[
            "indigestion",
            "bloating",
            "fullness after meals",
            "burping",
            "mild stomach discomfort",
            "upper stomach heaviness",
        ],
        description="Indigestion usually causes bloating, fullness, burping, or discomfort after eating and often improves with dietary moderation.",
        otc_medications=["Antacids"],
        safety_notes="Seek doctor advice if symptoms are recurrent, progressively worsening, or associated with black stools or repeated vomiting.",
    ),
    MedicalDocument(
        condition="Stomach Irritation",
        symptoms=[
            "stomach pain",
            "stomach irritation",
            "stomach discomfort",
            "burning in stomach",
            "pain after spicy food",
            "gastric discomfort",
        ],
        description="Mild stomach irritation can occur after irregular meals, spicy foods, excess tea or coffee, or temporary digestive upset.",
        otc_medications=["Antacids"],
        safety_notes="Consult a doctor if stomach pain is severe, localized strongly to one side, or associated with fever, vomiting, or blood in stool.",
    ),
    MedicalDocument(
        condition="Common Cold",
        symptoms=[
            "cold",
            "runny nose",
            "sneezing",
            "sore throat",
            "cough",
            "stuffy nose",
            "nasal congestion",
            "mild fever",
        ],
        description="Common cold is a mild viral infection that often improves with rest, hydration, and supportive care.",
        otc_medications=["Cetirizine", "Paracetamol"],
        safety_notes="Seek medical attention if breathing difficulty, chest pain, persistent high fever, or symptoms lasting beyond a week occur.",
    ),
    MedicalDocument(
        condition="Allergic Rhinitis",
        symptoms=[
            "allergy",
            "allergic cold",
            "runny nose",
            "sneezing",
            "itchy nose",
            "itchy eyes",
            "watery eyes",
            "dust allergy",
        ],
        description="Allergic rhinitis often causes repeated sneezing, runny nose, and itching, especially after dust or seasonal exposure.",
        otc_medications=["Cetirizine"],
        safety_notes="Doctor review is advised if wheezing, breathing discomfort, or prolonged symptoms are present.",
    ),
    MedicalDocument(
        condition="Sore Throat",
        symptoms=[
            "sore throat",
            "throat pain",
            "pain while swallowing",
            "throat irritation",
            "scratchy throat",
        ],
        description="Sore throat can occur with viral illness, dryness, voice strain, or cold symptoms and may improve with rest and fluids.",
        otc_medications=["Paracetamol"],
        safety_notes="Seek medical advice if swallowing becomes difficult, voice changes significantly, or symptoms persist beyond several days.",
    ),
    MedicalDocument(
        condition="Mild Cough",
        symptoms=[
            "cough",
            "dry cough",
            "mild cough",
            "throat tickle",
            "cough at night",
            "cough with cold",
        ],
        description="Mild cough may occur with a common cold, throat irritation, or post-nasal drip and often improves with hydration and rest.",
        otc_medications=["Cetirizine"],
        safety_notes="Consult a doctor if cough is persistent, associated with breathing difficulty, chest pain, blood, or high fever.",
    ),
    MedicalDocument(
        condition="Sinus Congestion",
        symptoms=[
            "sinus pressure",
            "stuffy nose",
            "facial pressure",
            "nasal congestion",
            "forehead heaviness",
            "blocked nose",
        ],
        description="Sinus congestion can cause facial pressure, blocked nose, and headache, often with cold or allergy symptoms.",
        otc_medications=["Cetirizine", "Paracetamol"],
        safety_notes="Doctor review is advised if facial pain becomes severe, swelling develops, or symptoms are prolonged.",
    ),
    MedicalDocument(
        condition="Body Pain",
        symptoms=[
            "body pain",
            "body ache",
            "muscle pain",
            "back ache",
            "leg pain",
            "generalized pain",
            "fatigue",
        ],
        description="Body pain can happen with viral illness, fatigue, strain, poor sleep, or dehydration and often improves with rest and fluids.",
        otc_medications=["Paracetamol"],
        safety_notes="Consult a doctor if pain is severe, one-sided, associated with swelling, injury, or persistent weakness.",
    ),
    MedicalDocument(
        condition="Mild Dehydration",
        symptoms=[
            "dehydration",
            "dry mouth",
            "dizziness",
            "lightheadedness",
            "low energy",
            "weakness",
            "reduced fluid intake",
        ],
        description="Mild dehydration may cause weakness, dizziness, low energy, and dry mouth, especially after fever, poor intake, or heat exposure.",
        otc_medications=["ORS"],
        safety_notes="Seek doctor help if dizziness is severe, fainting occurs, vomiting prevents fluids, or urine output is very low.",
    ),
    MedicalDocument(
        condition="Mild Diarrhea",
        symptoms=[
            "diarrhea",
            "loose stools",
            "watery stool",
            "frequent stool",
            "stomach cramps",
            "stomach upset",
        ],
        description="Mild diarrhea can result from temporary infection or food-related irritation and often requires hydration support.",
        otc_medications=["ORS"],
        safety_notes="Doctor review is needed if diarrhea is persistent, severe, bloody, or associated with strong dehydration signs.",
    ),
    MedicalDocument(
        condition="Nausea",
        symptoms=[
            "nausea",
            "queasy feeling",
            "uneasy stomach",
            "feeling like vomiting",
            "loss of appetite",
        ],
        description="Nausea may happen with indigestion, mild viral illness, dehydration, or food-related stomach upset.",
        otc_medications=["ORS"],
        safety_notes="Seek medical advice if vomiting is frequent, fluids cannot be retained, or severe stomach pain accompanies nausea.",
    ),
    MedicalDocument(
        condition="Fatigue and Weakness",
        symptoms=[
            "weakness",
            "tiredness",
            "fatigue",
            "low energy",
            "sleepiness",
            "lack of energy",
        ],
        description="Fatigue and weakness may be associated with poor sleep, mild infection, dehydration, stress, or recovery from illness.",
        otc_medications=["ORS", "Paracetamol"],
        safety_notes="Consult a doctor if weakness is severe, sudden, one-sided, or associated with chest symptoms, fainting, or prolonged fever.",
    ),
]
