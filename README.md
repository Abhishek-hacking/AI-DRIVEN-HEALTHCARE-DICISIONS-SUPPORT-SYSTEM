# AI-Driven Healthcare Decision Support System

This project is a full-stack healthcare decision support prototype built with Streamlit, FastAPI, FAISS, Sentence Transformers, and a local Ollama model.

## Features

- Conversational symptom intake
- Structured follow-up interview
- Medical knowledge base retrieval
- Risk classification
- Safety-first OTC medication guidance
- Prescription and unsafe medication blocking
- Doctor escalation flow
- Doctor booking interface

## Tech Stack

- Frontend: Streamlit
- Backend: FastAPI
- AI: Ollama (`tinydolphin`)
- Retrieval: FAISS
- Embeddings: Sentence Transformers
- Language: Python

## Project Files

- `app.py` - Streamlit entrypoint
- `figma_frontend.py` - Main frontend UI
- `api.py` - FastAPI backend
- `healthcare_engine.py` - Core healthcare decision logic
- `interview_engine.py` - Follow-up interview flow
- `knowledge_base.py` - Retrieval layer
- `medical_knowledge.py` - Healthcare knowledge base
- `safety_engine.py` - Safety rules
- `llm_client.py` - Ollama integration
- `run_api.py` - Backend runner

## How To Run

### 1. Create virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Pull Ollama model

```powershell
ollama pull tinydolphin
```

### 4. Start backend

```powershell
python run_api.py
```

### 5. Start frontend

In another terminal:

```powershell
streamlit run app.py
```

Then open:

`http://localhost:8501`

## Notes

- This system is a healthcare decision support prototype, not a substitute for professional diagnosis.
- Only safe OTC medication suggestions are allowed.
- High-risk and uncertain cases are escalated for doctor review.
