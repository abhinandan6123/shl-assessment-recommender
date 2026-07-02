# SHL Assessment Recommender

Conversational agent that recommends SHL Individual Test Solutions through dialogue.
See `APPROACH.md` for the design write-up (read it first — it includes an important
disclosure about how the bundled catalog data was sourced).

## Project layout
```
app/
  main.py       FastAPI app: GET /health, POST /chat
  agent.py       System prompt construction, LLM call + retry, turn-cap logic
  llm.py          Gemini / Anthropic / mock provider abstraction
  catalog.py       Loads data/catalog.json, formats for prompt, validates LLM output
  guardrails.py     Keyword-based prompt-injection pre-filter
  schemas.py         Pydantic models matching the exact required API schema
data/catalog.json    346 scraped Individual Test Solutions (see APPROACH.md)
scripts/scrape_catalog.py   First-party scraper — RUN THIS YOURSELF before submitting
tests/test_agent.py  Offline unit tests (no network/API key needed)
```

## Local setup
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in GOOGLE_API_KEY (or ANTHROPIC_API_KEY)
```

### Run the offline tests (no API key required)
```bash
LLM_PROVIDER=mock python tests/test_agent.py
```

### Run the server locally
```bash
export LLM_PROVIDER=gemini
export GOOGLE_API_KEY=your-key-here   # free tier: https://aistudio.google.com/apikey
uvicorn app.main:app --reload --port 8000
```
Then:
```bash
curl localhost:8000/health
curl -X POST localhost:8000/chat -H "Content-Type: application/json" -d '{
  "messages": [{"role": "user", "content": "Hiring a mid-level Java developer who also works with stakeholders"}]
}'
```

To use Anthropic instead, set `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY`.
# 🚀 SHL Assessment Recommender

> Production-ready Conversational AI Agent for recommending SHL Individual Test Solutions using FastAPI, Google Gemini, grounded catalog validation, and stateless conversational reasoning.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-green)
![Gemini](https://img.shields.io/badge/LLM-Google%20Gemini%202.0%20Flash-orange)
![Render](https://img.shields.io/badge/Deployment-Render-success)
![License](https://img.shields.io/badge/Status-Completed-success)

---

# 🌐 Live Demo

### Public API

https://shl-assessment-recommender-2-61vr.onrender.com

### Swagger UI

https://shl-assessment-recommender-2-61vr.onrender.com/docs

### OpenAPI

https://shl-assessment-recommender-2-61vr.onrender.com/openapi.json

### Health

https://shl-assessment-recommender-2-61vr.onrender.com/health

---

# 📌 Overview

This project implements a conversational AI agent capable of helping recruiters and hiring managers discover appropriate SHL Individual Test Solutions through natural conversation.

Instead of relying on keyword search, the assistant:

- asks clarifying questions
- recommends assessments
- refines recommendations
- compares assessments
- rejects prompt injection
- refuses off-topic requests

The project was built as part of the SHL AI Research Internship assignment.

---

# ✨ Features

✅ Conversational AI

✅ FastAPI Backend

✅ Google Gemini 2.0 Flash

✅ Prompt Guardrails

✅ Grounded Recommendations

✅ Stateless API

✅ Assessment Comparison

✅ Recommendation Refinement

✅ Catalog Validation

✅ Swagger Documentation

✅ Render Deployment

---

# 🏗 Architecture

User

↓

FastAPI

↓

Conversation Agent

↓

Guardrails

↓

Gemini

↓

Catalog Validation

↓

Grounded Response

---

## Environment variables
| Var | Required | Default | Notes |
|---|---|---|---|
| `LLM_PROVIDER` | no | `gemini` | `gemini`, `anthropic`, or `mock` |
| `GOOGLE_API_KEY` | if provider=gemini | — | https://aistudio.google.com/apikey |
| `GEMINI_MODEL` | no | `gemini-2.0-flash` | |
| `ANTHROPIC_API_KEY` | if provider=anthropic | — | |
| `ANTHROPIC_MODEL` | no | `claude-sonnet-4-5` | |

```

---

# ⚙️ Tech Stack

| Category | Technology |
|------------|------------|
| Backend | FastAPI |
| Language | Python 3.11 |
| LLM | Google Gemini 2.0 Flash |
| Validation | Pydantic |
| Deployment | Render |
| Documentation | Swagger/OpenAPI |
| Version Control | GitHub |

---

# 🚀 API

## Health

GET

```
/health
```

Response

```json
{
  "status":"ok"
}
```

---

## Chat

POST

```
/chat
```

Example

```json
{
 "messages":[
   {
      "role":"user",
      "content":"Hiring a Java developer with 4 years experience."
   }
 ]
}
```

---

# 🧠 Capabilities

The agent supports:

- Clarification
- Recommendation
- Refinement
- Comparison
- Refusal
- Prompt Injection Protection

---

# 🔒 Guardrails

- Prompt Injection Detection
- Scope Restriction
- Catalog Validation
- Hallucination Prevention

---

# 🧪 Testing

Validated using:

- Swagger
- Manual conversations
- Mock LLM
- Unit Tests
- Deployment verification

---

# 🌍 Deployment

Hosted on Render

Public URL

https://shl-assessment-recommender-2-61vr.onrender.com

---

# 📄 Documentation

Approach

APPROACH.md

---

# 📷 Screenshots

Swagger

(Add screenshot)

Conversation Example

(Add screenshot)

Deployment

(Add screenshot)

---

# 🔮 Future Improvements

- Hybrid Retrieval
- Vector Search
- FAISS
- Redis Cache
- Docker
- CI/CD
- Kubernetes

---

# 👨‍💻 Author

**Abhinandan Kancharla**

AI Backend Engineer

GitHub

https://github.com/abhinandan6123

Portfolio
https://abhikancharla.vercel.app/


---

# ⭐ Acknowledgements

Built for the SHL AI Research Internship Assignment.



