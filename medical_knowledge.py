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
        symptoms=["fever", "body pain", "headache", "temperature"],
        description="Fever is commonly caused by infection and should be monitored over time.",
        otc_medications=["Paracetamol"],
        safety_notes="Consult a doctor if fever lasts more than 3 days or becomes high.",
    ),
    MedicalDocument(
        condition="Headache",
        symptoms=["headache", "head pain", "pressure", "mild dizziness"],
        description="Headache may be associated with stress, dehydration, poor sleep, or minor illness.",
        otc_medications=["Paracetamol"],
        safety_notes="Seek medical attention if headache is severe, sudden, or persistent.",
    ),
    MedicalDocument(
        condition="Acidity",
        symptoms=["acidity", "acid reflux", "stomach burning", "indigestion"],
        description="Acidity can occur because of excess stomach acid or food triggers.",
        otc_medications=["Antacids"],
        safety_notes="Avoid spicy or oily food. Consult a doctor if symptoms are frequent.",
    ),
    MedicalDocument(
        condition="Common Cold",
        symptoms=["cold", "runny nose", "sneezing", "sore throat", "cough"],
        description="Common cold is a mild viral infection that often improves with rest and hydration.",
        otc_medications=["Cetirizine", "Paracetamol"],
        safety_notes="Seek medical attention if breathing difficulty or persistent high fever occurs.",
    ),
]
