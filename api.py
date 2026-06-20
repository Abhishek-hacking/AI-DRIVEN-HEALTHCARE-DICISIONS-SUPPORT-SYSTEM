from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend_models import (
    ChatReplyRequest,
    ChatStartRequest,
    ErrorResponse,
    HealthCheckResponse,
    InterviewResponse,
    ResultResponse,
)
from healthcare_engine import HealthcareDecisionEngine
from interview_engine import append_answer, start_interview


app = FastAPI(title="Healthcare Decision Support API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = HealthcareDecisionEngine()
SESSIONS = {}


@app.get("/health", response_model=HealthCheckResponse)
def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(status="ok", service="healthcare-decision-support-api")


@app.post("/chat/start", responses={400: {"model": ErrorResponse}})
def chat_start(payload: ChatStartRequest):
    session = start_interview(payload.message)
    if not session.symptom or not session.questions:
        result = engine.analyze(payload.message)
        return ResultResponse(stage="result", session_id=session.session_id, result=result)

    SESSIONS[session.session_id] = session
    return InterviewResponse(
        stage="interview",
        session_id=session.session_id,
        question=session.questions[0],
        question_number=1,
        total_questions=len(session.questions),
    )


@app.post("/chat/reply", responses={404: {"model": ErrorResponse}})
def chat_reply(payload: ChatReplyRequest):
    session = SESSIONS.get(payload.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    append_answer(session, payload.answer)
    if not session.completed:
        return InterviewResponse(
            stage="interview",
            session_id=session.session_id,
            question=session.questions[session.current_index],
            question_number=session.current_index + 1,
            total_questions=len(session.questions),
        )

    result = engine.analyze(session.build_combined_query())
    del SESSIONS[payload.session_id]
    return ResultResponse(stage="result", session_id=session.session_id, result=result)
