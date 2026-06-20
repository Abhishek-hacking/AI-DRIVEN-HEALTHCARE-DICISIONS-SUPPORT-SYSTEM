from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Iterable

from medical_knowledge import MedicalDocument


DEFAULT_MODEL = os.getenv("HEALTHCARE_LLM_MODEL", "phi3")
LLM_TIMEOUT_SECONDS = int(os.getenv("HEALTHCARE_LLM_TIMEOUT", "12"))


def build_context(documents: Iterable[MedicalDocument]) -> str:
    return "\n\n".join(doc.to_text() for doc in documents)


def _fallback_response(condition: str | None, risk_level: str, advice: str) -> str:
    if condition:
        return (
            f"Based on the medical knowledge base, this may be related to {condition}. "
            f"Risk level appears to be {risk_level.lower()}. {advice}"
        )
    return (
        f"Based on the available medical knowledge, the current risk appears to be "
        f"{risk_level.lower()}. {advice}"
    )


class LocalHealthcareLLM:
    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        self.model_name = model_name
        try:
            import ollama  # type: ignore
        except ImportError:
            self.ollama = None
        else:
            self.ollama = ollama

    def generate_response(
        self,
        user_query: str,
        documents: list[MedicalDocument],
        condition: str | None,
        risk_level: str,
        advice: str,
    ) -> tuple[str, str]:
        if self.ollama is None:
            return _fallback_response(condition, risk_level, advice), "fallback"

        prompt = f"""
You are a healthcare decision support assistant.

Rules:
- Use only the provided medical knowledge.
- Do not suggest prescription medication.
- Do not suggest harmful or restricted drugs.
- If information is uncertain, keep advice conservative and recommend doctor review.
- Keep the answer short and practical.

Medical Knowledge:
{build_context(documents)}

Patient Query:
{user_query}

Known Condition:
{condition or "Unknown"}

Risk Level:
{risk_level}

Safe Advice:
{advice}
"""

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self.ollama.chat,
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                )
                response = future.result(timeout=LLM_TIMEOUT_SECONDS)
            return response["message"]["content"], f"ollama:{self.model_name}"
        except FutureTimeoutError:
            return _fallback_response(condition, risk_level, advice), "fallback-timeout"
        except Exception:
            return _fallback_response(condition, risk_level, advice), "fallback"
