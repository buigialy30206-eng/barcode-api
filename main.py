"""
Barcode Generator API
Generate barcode images (Code128, EAN13, EAN8).
"""

import io, base64, tempfile, os
from typing import Optional

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from pydantic import BaseModel
import barcode
from barcode.writer import ImageWriter

import time as _t, threading as _th
_rl_win, _rl_max, _rl_hits, _rl_lk = 60, 60, {}, _th.Lock()

async def _rate_limit(request):
    from fastapi import Request, HTTPException
    ip = (request.headers.get('X-Forwarded-For','') or request.headers.get('X-Real-IP','') or (request.client.host if request.client else '127.0.0.1')).split(',')[0].strip()
    now = _t.time()
    with _rl_lk:
        e = _rl_hits.get(ip)
        if e:
            if now - e['s'] > _rl_win: e['s'], e['c'] = now, 1
            else:
                e['c'] += 1
                if e['c'] > _rl_max: raise HTTPException(429, 'Too many requests')
        else: _rl_hits[ip] = {'s': now, 'c': 1}
    return True

app = FastAPI(title="Barcode Generator API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}


FORMATS = {"code128": barcode.Code128, "ean13": barcode.EAN13, "ean8": barcode.EAN8}


):
    if fmt not in FORMATS:
        fmt = "code128"

    bc = FORMATS[fmt](data, writer=ImageWriter())
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    bc.save(tmp_path[:-4])  # .save() adds .png automatically
    png_path = tmp_path[:-4] + ".png"

    with open(png_path, "rb") as f:
        img_data = f.read()
    os.unlink(png_path)

    if output == "base64":
        return {"barcode": "data:image/png;base64," + base64.b64encode(img_data).decode()}
    return Response(content=img_data, media_type="image/png")
