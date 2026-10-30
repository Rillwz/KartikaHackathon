# KartikaHackathon — Phishing URL Checker

FastAPI endpoint that scores a URL for phishing indicators.

## Run

```bash
uv run main.py
```

`uv` membaca dependency inline di `main.py` dan menyalakan server di
`http://127.0.0.1:8000`. Tanpa venv, tanpa langkah install.
`pip install -r requirements.txt` + `uvicorn main:app --reload` masih bisa
kalau lebih suka cara itu.

## Cara memanggil

```bash
curl 'http://127.0.0.1:8000/api/check?url=https://tokopedia.com/'
```

```json
{"url": "https://tokopedia.com/", "result": "good"}
```

Respons selalu `{"url": ..., "result": ...}` dengan `result` bernilai `good`
atau `bad`. Endpoint menolak dengan 400 kalau skema bukan http/https, host
tidak bisa di-resolve, atau URL mengarah ke alamat non-publik (loopback,
IP privat, link-local/metadata seperti `169.254.169.254`).

## Contoh hasil

Situs perusahaan besar (URL resmi), dan tiruannya:

| URL | result |
|---|---|
| `https://www.google.com/` | good |
| `https://www.microsoft.com/` | good |
| `https://www.apple.com/` | good |
| `https://www.netflix.com/` | good |
| `https://www.paypal.com/` | good |
| `https://www.dhl.com/` | good |
| `https://tokopedia.com/` | good |
| `https://www.blibli.com/` | good |
| `https://www.bankmandiri.co.id/` | good |
| `https://bca.co.id/` | good |
| `https://tokopediaa.com/` | bad — brand di luar domain asli |
| `http://paypal.com@evil.tk/login` | bad — trik userinfo |
| `https://bit.ly/abc123` | bad — URL shortener |
| `http://tokopedia.com/` | bad — bukan https |
| `http://192.168.1.1/admin` | 400 — IP non-publik (ditolak sebelum dinilai) |
| `https://microsoft-login.verify.tk/x` | 400 — domain tidak resolve |

`192.168.1.1` dan domain yang tidak ada ditolak di validasi URL, jadi tidak
pernah sampai ke scorer. Kalau butuh keduanya dijawab `bad` (bukan 400),
bilang saja — satu baris di `main.py`.

Data di atas diambil dari pemanggilan sungguhan ke endpoint, bukan karangan.

## Cara kerja

`main.py` memvalidasi URL (http/https, dan host harus resolve ke IP publik)
lalu menjalankan `checkphising.py` sebagai subprocess — maksimal 4 pengecekan
paralel, 30 detik per pengecekan. `checkphising.py` adalah mockup heuristik:
tanpa panggilan jaringan, tanpa model. Tukar fungsi `score()` dengan
classifier sungguhan dan API-nya tidak perlu berubah.

Aturan yang dipakai `score()`:

- brand muncul di host tapi bukan domain resminya (`tokopediaa.com`)
- URL shortener (`bit.ly`)
- IP mentah, bukan domain
- subdomain berlebihan, banyak tanda hubung, URL terlalu panjang
- trik userinfo (`https://paypal.com@evil.tk`)
- bukan https
- TLD rawan abuse (`.tk`, `.top`, `.xyz`, `.click`, `.zip`, `.mov`, `.rest`)

Satu alasan saja sudah cukup untuk `bad`.
