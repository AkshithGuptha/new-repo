import io
import os
import threading

import fitz
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps
from paddleocr import PaddleOCR
import uvicorn

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_PDF_PAGES = 10
_engine = None
_engine_lock = threading.Lock()
_ocr_lock = threading.Lock()

app = FastAPI(title="OCR Go API", docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def get_engine():
    global _engine
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                _engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    return _engine


def decode_file(filename: str, data: bytes):
    if not data:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Maximum upload size is 10 MB.")

    if filename.lower().endswith(".pdf"):
        try:
            doc = fitz.open(stream=data, filetype="pdf")
            if doc.page_count > MAX_PDF_PAGES:
                doc.close()
                raise HTTPException(413, "PDFs are limited to 10 pages.")
            images = []
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                images.append(np.array(Image.frombytes("RGB", [pix.width, pix.height], pix.samples)))
            doc.close()
            return images
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(400, "This PDF could not be read.") from exc

    try:
        image = Image.open(io.BytesIO(data))
        return [np.array(ImageOps.exif_transpose(image).convert("RGB"))]
    except Exception as exc:
        raise HTTPException(400, "Upload a valid PNG, JPG, WEBP, or PDF file.") from exc


@app.get("/")
def home():
    return {"name": "OCR Go", "status": "ok", "message": "OCR API is running. Use POST /api/ocr to extract text."}


@app.get("/health")
def health():
    return {"status": "ok", "engine_loaded": _engine is not None}


@app.post("/api/ocr")
async def run_ocr(file: UploadFile = File(...)):
    filename = file.filename or "upload"
    if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".pdf")):
        raise HTTPException(415, "Supported formats: PNG, JPG, WEBP, PDF.")
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    images = decode_file(filename, data)
    try:
        # Keep CPU inference serial on the free instance to avoid memory spikes.
        with _ocr_lock:
            engine = get_engine()
            pages = []
            for number, image in enumerate(images, start=1):
                raw = engine.ocr(image, cls=True)
                lines = []
                if raw and raw[0]:
                    for item in raw[0]:
                        if len(item) > 1 and item[1]:
                            lines.append({
                                "text": str(item[1][0]),
                                "confidence": round(float(item[1][1]), 4),
                            })
                pages.append({"page": number, "text": "\n".join(line["text"] for line in lines), "lines": lines})
        text = "\n\n".join(
            (f"--- Page {p['page']} ---\n" if len(pages) > 1 else "") + p["text"] for p in pages
        ).strip()
        return {"filename": filename, "text": text, "pages": pages,
                "page_count": len(pages), "line_count": sum(len(p["lines"]) for p in pages)}
    except HTTPException:
        raise
    except Exception as exc:
        print(f"OCR failed for {filename}: {type(exc).__name__}: {exc}", flush=True)
        raise HTTPException(500, "OCR failed on this file. Try a clearer image or a smaller PDF.") from exc


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "10000")), workers=1)
