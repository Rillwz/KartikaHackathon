import asyncio, ipaddress, json, socket, sys
from pathlib import Path
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Query

SCRIPT = Path(__file__).with_name("checkphising.py")
TIMEOUT, MAX_PARALLEL = 30, 4
_slots = asyncio.Semaphore(MAX_PARALLEL)

app = FastAPI()


def _safe_host(host: str) -> bool:
    """True only if every address the host resolves to is public."""
    infos = socket.getaddrinfo(host, None)
    return all(ipaddress.ip_address(i[4][0]).is_global for i in infos)


async def _check(url: str) -> dict:
    async with _slots:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, str(SCRIPT), "--", url,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        try:
            out, err = await asyncio.wait_for(proc.communicate(), TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise HTTPException(504, "check timed out")

    if proc.returncode != 0:
        print(f"checkphising failed ({proc.returncode}): {err.decode(errors='replace')}")
        raise HTTPException(500, "check failed")

    try:
        return json.loads(out)
    except json.JSONDecodeError:
        raise HTTPException(502, "checker returned no JSON")


@app.get("/api/check")
async def check_phishing(url: str = Query(..., max_length=2048)):
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        raise HTTPException(400, "url must be http(s)")
    try:
        # ponytail: guards the URL we hand over, not redirects the checker follows — re-validate there if it follows them
        ok = await asyncio.to_thread(_safe_host, p.hostname)
    except OSError:
        raise HTTPException(400, "host does not resolve")
    if not ok:
        raise HTTPException(400, "url resolves to a non-public address")
    return await _check(url)


if __name__ == "__main__":
    assert not _safe_host("127.0.0.1")
    assert not _safe_host("169.254.169.254")
    assert _safe_host("example.com")
    print("self-check ok")
