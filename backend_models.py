from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


RiskLevel = Literal["MILD", "MODERATE", "SEVERE", "UNKNOWN"]


@dataclass
class InterviewSession:
    session_id: str
    initial_input: str
    symptom: Optional[str] = None
    questions: List[str] = field(default_factory=list)
    answers: List[str] = field(default_factory=list)
    current_index: int = 0

    @property
    def completed(self) -> bool:
        return self.current_index >= len(self.questions)

    def build_combined_query(self) -> str:
        parts = [self.symptom or self.initial_input, *self.answers]
        return " ".join(part for part in parts if part).strip()


class ChatStartRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatReplyRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)


class HealthCheckResponse(BaseModel):
    status: str
    service: str


class ResultPayload(BaseModel):
    status: Literal["ok", "doctor_required"]
    risk_level: Optional[RiskLevel] = None
    condition: Optional[str] = None
    confidence: Optional[int] = None
    medication: List[str] = Field(default_factory=list)
    advice: Optional[str] = None
    reason: Optional[str] = None
    note: Optional[str] = None
    knowledge: List[str] = Field(default_factory=list)


class InterviewResponse(BaseModel):
    stage: Literal["interview"]
    session_id: str
    question: str
    question_number: int
    total_questions: int


class ResultResponse(BaseModel):
    stage: Literal["result"]
    session_id: str
    result: ResultPayload


class ErrorResponse(BaseModel):
    stage: Literal["error"]
    message: str
