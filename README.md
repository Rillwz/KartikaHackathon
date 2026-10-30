# KartikaHackathon — Phishing URL Checker

FastAPI endpoint that scores a URL for phishing indicators.

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install fastapi uvicorn
.venv/bin/uvicorn main:app --reload
curl 'http://localhost:8000/api/check?url=https://www.paypal.com/signin'
```

```json
{"url": "https://www.paypal.com/signin", "verdict": "safe", "score": 0.0, "reasons": []}
```

## How it works

`main.py` validates the URL (http/https, resolves to a public IP) then runs
`checkphising.py` as a subprocess, capped at 4 concurrent checks and 30s each.
`checkphising.py` is a heuristic mockup — no network calls, no model. Swap its
`score()` for a real classifier and the API stays the same.
