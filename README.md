# KartikaHackathon — Phishing URL Checker

FastAPI endpoint that scores a URL for phishing indicators.

## Run

```bash
uv run main.py
```

`uv` reads the inline dependencies in `main.py` and starts the server on
:8000. No venv, no install step. `pip install -r requirements.txt` +
`uvicorn main:app --reload` still works if you prefer it.

```json
{"url": "https://www.paypal.com/signin", "result": "good"}
```

## How it works

`main.py` validates the URL (http/https, resolves to a public IP) then runs
`checkphising.py` as a subprocess, capped at 4 concurrent checks and 30s each.
`checkphising.py` is a heuristic mockup — no network calls, no model. Swap its
`score()` for a real classifier and the API stays the same.
