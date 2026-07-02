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

# 📁 Project Structure

```
app/
    agent.py
    catalog.py
    guardrails.py
    llm.py
    main.py
    schemas.py

data/
    catalog.json

scripts/
    scrape_catalog.py

tests/
    test_agent.py

requirements.txt
runtime.txt
README.md
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

(https://abhikancharla.vercel.app/)

---

# ⭐ Acknowledgements

Built for the SHL AI Research Internship Assignment.
