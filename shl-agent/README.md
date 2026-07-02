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

## Before you submit — please do these
1. **Run `scripts/scrape_catalog.py` yourself** from a machine with normal internet
   access and diff its output against `data/catalog.json`. I built the bundled
   catalog from a community scrape (disclosed in `APPROACH.md`) because this dev
   sandbox can't reach shl.com — the CSS selectors in that script are my best
   reconstruction of the page structure and should be verified against the live DOM.
2. **Smoke-test a real LLM call.** I could not reach Gemini or Anthropic's APIs from
   this sandbox, so `GeminiLLM`/`AnthropicLLM` are implementation-complete but
   untested against the live API. Run the curl command above with a real key before
   deploying.
3. **Run the 10 provided conversation traces** against your deployed endpoint — I
   didn't have access to that zip file to test against directly.

## Deploy to Render
1. Push this repo to GitHub.
2. In Render: New → Blueprint → point at the repo (it will read `render.yaml`).
3. Set the `GOOGLE_API_KEY` env var in the Render dashboard (marked `sync: false`
   in render.yaml, so it won't be committed).
4. Deploy. First `/health` call may take up to ~2 min on the free tier (cold start).
5. Confirm both endpoints are reachable:
   ```bash
   curl https://<your-app>.onrender.com/health
   ```

## Environment variables
| Var | Required | Default | Notes |
|---|---|---|---|
| `LLM_PROVIDER` | no | `gemini` | `gemini`, `anthropic`, or `mock` |
| `GOOGLE_API_KEY` | if provider=gemini | — | https://aistudio.google.com/apikey |
| `GEMINI_MODEL` | no | `gemini-2.0-flash` | |
| `ANTHROPIC_API_KEY` | if provider=anthropic | — | |
| `ANTHROPIC_MODEL` | no | `claude-sonnet-4-5` | |
