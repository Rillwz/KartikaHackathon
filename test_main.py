# /// script
# dependencies = ["fastapi", "uvicorn", "httpx"]
# ///
"""Run: uv run test_main.py"""
from fastapi.testclient import TestClient
from main import app, _safe_host
from checkphising import score

c = TestClient(app)

# SSRF guard
assert not _safe_host("127.0.0.1")
assert not _safe_host("169.254.169.254")
assert _safe_host("example.com")

# scorer
assert score("https://www.paypal.com/signin")["result"] == "good"
assert score("http://paypal.com@evil.tk/x")["result"] == "bad"
assert score("http://192.168.1.1/login")["result"] == "bad"
assert set(score("https://a.com")["result"] for _ in [0]) <= {"good", "bad"}

# endpoint contract
r = c.get("/api/check", params={"url": "ftp://a.com"})
assert r.status_code == 400, r.text
r = c.get("/api/check", params={"url": "http://169.254.169.254/latest/meta-data/"})
assert r.status_code == 400 and "non-public" in r.text, r.text
r = c.get("/api/check", params={"url": "http://does-not-exist-xyz123.invalid/"})
assert r.status_code == 400, r.text  # known: unresolvable -> 400, not "bad"

# happy path, real subprocess
r = c.get("/api/check", params={"url": "https://example.com/"})
assert r.status_code == 200 and set(r.json()) == {"url", "result"}, r.text
assert r.json()["result"] in ("good", "bad")

print("all tests passed")
