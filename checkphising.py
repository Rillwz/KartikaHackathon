"""Mockup phishing checker. Usage: python checkphising.py -- <url>  -> JSON on stdout."""
import argparse, json, re, sys
from urllib.parse import urlparse

BRANDS = ("paypal", "google", "microsoft", "apple", "netflix", "bank", "dhl")
SHORTENERS = ("bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd")


def score(url: str) -> dict:
    p = urlparse(url)
    host = (p.hostname or "").lower()
    reasons = []

    if any(s in host for s in SHORTENERS):
        reasons.append("url shortener hides the real destination")
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host):
        reasons.append("raw IP address instead of domain")
    if host.count(".") > 3:
        reasons.append("excessive subdomains")
    if any(b in host for b in BRANDS) and not any(
        host == b or host.endswith("." + b + ".com") or host.endswith("." + b) for b in BRANDS
    ):
        reasons.append("brand name outside its real domain")
    if host.count("-") >= 2:
        reasons.append("many hyphens in host")
    if len(url) > 100:
        reasons.append("unusually long url")
    if "@" in p.netloc:
        reasons.append("userinfo trick in url")
    if p.scheme != "https":
        reasons.append("not https")
    if re.search(r"\.(zip|mov|tk|top|xyz|click|rest)$", host):
        reasons.append("high-abuse tld")

    result = "bad" if reasons else "good"
    return {"url": url, "result": result}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    args = ap.parse_args()
    print(json.dumps(score(args.url)))
