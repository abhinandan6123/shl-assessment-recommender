# Approach Document — SHL Assessment Recommender

## Data source (please read — important disclosure)
My dev sandbox has no network access to shl.com (egress allowlist only covers pypi/npm/github/etc.). To make progress under the deadline, I bootstrapped `data/catalog.json` (346 Individual Test Solutions) from a public community scrape of the same SHL catalog page (GitHub: `singhsourav0/SHL_Recommendation`), then cleaned it myself: mapped SHL's test-type text to the official single-letter codes, dropped ~19 non-test entries that had slipped in (pre-packaged "…Solution" bundles, standalone PDF reports/guides like "OPQ User Report" wrappers with no assigned type, profiler cards), and manually re-typed ~14 legitimate items the source left blank (e.g. Microsoft Excel/Word/PowerPoint 365, SHL Verify Interactive reasoning tests, Global Skills Assessment).

**I've included `scripts/scrape_catalog.py`, a first-party scraper you should run yourself from a machine with normal internet access before final submission**, and use its output instead if it disagrees with the bundled `catalog.json`. I did not fabricate or guess at any catalog entries — every row traces back to a real scrape of shl.com — but I want to be upfront that the *scrape itself* wasn't run by me directly against the live site this time.

## Architecture
```
FastAPI (/health, /chat)
   → guardrails.py   (keyword prompt-injection pre-filter, runs before any LLM call)
   → agent.py         (builds system prompt with full catalog + turn budget, calls LLM, validates output)
   → llm.py            (pluggable: Gemini / Anthropic / mock — same JSON-schema contract)
   → catalog.py         (loads catalog.json, formats for prompt, grounds/validates LLM output)
```

## Key design decisions

**Full-catalog-in-context instead of a vector DB.** 346 items formatted as one compact line each (~7K tokens) fits comfortably in any modern context window. I chose this over embeddings/FAISS deliberately: at this catalog size, giving the LLM the *entire* list and letting it select removes an entire failure mode — retrieval recall loss from a similarity search that ranks the wrong items highly. A vector store starts paying for itself past roughly a few thousand catalog items; below that it's extra infrastructure with no real relevance-quality upside, and it's harder to reason about/debug than "the model can see everything." If SHL's real catalog (1000+ items across both Individual and Job Solutions) needs to be handled, I'd switch to embedding-based retrieval + rerank at that point.

**Grounding is enforced by code, not just prompt wording.** The system prompt tells the LLM to only use catalog items, but I don't trust that alone. Every `(name, url)` pair the LLM returns is looked up against the real catalog after the call (`catalog.lookup`, URL-first then exact name match); anything that doesn't resolve is silently dropped rather than surfaced to the user. This is what actually prevents hallucinated URLs — tested in `tests/test_agent.py::test_drops_hallucinated_recommendation`.

**Stateless refine/compare via natural-language memory.** The API stores no per-conversation state, and critically, the *response's* structured `recommendations` field never comes back to me on the next turn — only the plain-text `messages` history does. So the system prompt explicitly instructs the model to name assessments in its prose reply whenever it recommends, not just in the structured field, so that a later "actually, add personality tests" can be resolved by re-reading the conversation transcript. This is a real constraint of the spec's stateless design, not an implementation shortcut.

**Turn-cap handling.** Each system prompt is told its own turn number out of the max (8) and gets escalating instructions: plenty of room → free to clarify; near the cap → prefer recommending; at/past turn 7 → must commit to a shortlist, no more questions. This prevents the agent from clarifying forever and timing out the harness.

**Defense-in-depth for refusals.** Off-topic/legal/prompt-injection refusal is primarily the LLM's job (it's in the system prompt), but I added a small regex-based pre-filter (`guardrails.py`) that catches obvious injection phrasing ("ignore previous instructions", "reveal your system prompt", "jailbreak", etc.) and short-circuits before any LLM call. This means even a single successful jailbreak in an 8-turn conversation can't cascade — the cheap check runs every turn regardless of what the model does.

**Never break schema compliance.** `run_chat` catches LLM/parsing errors and falls back to a safe clarifying response rather than raising; `main.py` has a top-level exception handler that still returns a valid `ChatResponse` shape with HTTP 200 rather than a 500. Given the hard-eval explicitly checks schema compliance on *every* response, I treated "never return something that fails validation" as more important than "always get a great answer."

## What I tested
- Unit tests (`tests/test_agent.py`, no network) for the validation/grounding layer: hallucinated URLs dropped, >10 recommendations truncated, URL-based matching canonicalizes slightly-off names, empty replies get a fallback, turn-guidance text changes correctly near the cap.
- End-to-end smoke tests against the FastAPI app using a deterministic `LLM_PROVIDER=mock` backend (no API key needed) covering: vague query → clarify; sufficiently detailed query → recommend; off-topic → refuse; injection attempt → refuse; empty message list; 9-turn conversation still returns 200 with valid schema.
- I could **not** test live LLM calls in this sandbox (no route to Gemini/Anthropic APIs here), so `GeminiLLM`/`AnthropicLLM` are implementation-complete and match each SDK's current (non-deprecated) API, but need to be smoke-tested by you with a real key before submission — I'd genuinely want to do this myself given more time, and would flag it as the single biggest risk in this submission if asked in the technical interview.
- I did not have access to the assignment's 10 labeled conversation traces (the PDF's download link wasn't extractable as clickable text) — please run those against the deployed endpoint before submitting; if any fail I'd expect it to be catalog-completeness gaps (missing descriptions beyond name/type/duration) rather than plumbing issues.

## What didn't work / trade-offs I'd revisit with more time
- The bundled catalog has no free-text description per assessment (the source scrape only captured name/type/duration/remote/adaptive) — comparisons ("what's the difference between X and Y") are grounded in those structural fields only, not richer content descriptions, which caps how insightful `compare` answers can be. Scraping each assessment's individual page for its description paragraph would meaningfully improve both `compare` quality and semantic recall.
- Keyword-based injection detection is a blunt instrument; a small classifier or a second cheap LLM call would catch more paraphrased attacks, at the cost of latency/complexity I didn't think was worth it for an 8-turn, 30s-budget conversation.

## Stack
FastAPI + Pydantic, Gemini 2.0 Flash (free tier, per assignment's suggestion) as default LLM with Anthropic as a swappable alternative, no vector DB (see above), deployed on Render. AI-assisted development: I used Claude (this conversation) to write the implementation from a design I directed turn-by-turn — data cleaning heuristics, grounding/validation strategy, turn-cap logic, and guardrail approach were my calls; boilerplate (FastAPI wiring, SDK integration syntax) was largely generated.
