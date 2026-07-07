"""
Barcode Generator API
Generate barcode images (Code128, EAN13, EAN8).
"""

import io, base64, tempfile, os
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from pydantic import BaseModel
import barcode
from barcode.writer import ImageWriter

app = FastAPI(title="Barcode Generator API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

FORMATS = {"code128": barcode.Code128, "ean13": barcode.EAN13, "ean8": barcode.EAN8}


@app.get("/health")
async def health(): return {"status": "ok"}


@app.get("/")
async def root(): return {"service": "Barcode Generator API", "version": "1.0.0"}


@app.get("/generate")
async def generate(
    data: str = Query(..., description="Barcode content (numbers for EAN)"),
    fmt: str = Query("code128", description="Format: code128, ean13, ean8"),
    output: str = Query("png", description="Output: png or base64"),
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
