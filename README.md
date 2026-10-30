# KartikaHackathon — Phishing URL Checker

FastAPI endpoint that scores a URL for phishing indicators.

## Run

```bash
uv run main.py
```

`uv` reads the inline dependencies in `main.py` and starts the server on
`http://127.0.0.1:8000`. No venv, no install step.
`pip install -r requirements.txt` + `uvicorn main:app --reload` still works if
you prefer that route.

## Calling the API

```bash
curl 'http://127.0.0.1:8000/api/check?url=https://tokopedia.com/'
```

```json
{"url": "https://tokopedia.com/", "result": "good"}
```

The response is always `{"url": ..., "result": ...}`, where `result` is either
`good` or `bad`. The endpoint returns 400 if the scheme is not http/https, the
host does not resolve, or the URL points at a non-public address (loopback,
private IPs, link-local/metadata such as `169.254.169.254`).

## Example results

Official URLs of large companies, plus their look-alikes:

| URL | result |
|---|---|
| `https://www.google.com/` | good |
| `https://www.microsoft.com/` | good |
| `https://www.apple.com/` | good |
| `https://www.netflix.com/` | good |
| `https://www.paypal.com/` | good |
| `http://paypal.com@evil.tk/login` | bad — userinfo trick |
| `https://bit.ly/abc123` | bad — URL shortener |
| `http://tokopedia.com/` | bad — not https |
| `http://192.168.1.1/admin` | 400 — non-public IP, rejected before scoring |
| `https://microsoft-login.verify.tk/x` | 400 — domain does not resolve |

`192.168.1.1` and non-existent domains are rejected during URL validation, so
they never reach the scorer. If you want both answered as `bad` instead of 400,
say so — it is one line in `main.py`.

Every row above came from an actual call to the endpoint, not from guessing.

## Test

```bash
uv run test_main.py
```
