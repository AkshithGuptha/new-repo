import io
import os
import threading
from typing import Any

import fitz
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from PIL import Image, ImageOps
from paddleocr import PaddleOCR

app = FastAPI(title="OCR Go — PaddleOCR", version="1.0.0")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp", "application/pdf"}
_ocr_engine = None
_ocr_lock = threading.Lock()


def get_ocr() -> Any:
    global _ocr_engine
    if _ocr_engine is None:
        with _ocr_lock:
            if _ocr_engine is None:
                _ocr_engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    return _ocr_engine


def image_arrays(data: bytes, content_type: str) -> list[np.ndarray]:
    if content_type == "application/pdf":
        try:
            document = fitz.open(stream=data, filetype="pdf")
            if document.page_count > 10:
                raise HTTPException(413, "PDFs are limited to 10 pages per upload.")
            arrays = []
            for page in document:
                pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                arrays.append(np.array(image))
            document.close()
            return arrays
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(400, "Could not read this PDF.") from exc

    try:
        image = Image.open(io.BytesIO(data))
        image = ImageOps.exif_transpose(image).convert("RGB")
        return [np.array(image)]
    except Exception as exc:
        raise HTTPException(400, "Could not read this image.") from exc


@app.get("/health")
def health():
    return {"status": "ok", "ocr_loaded": _ocr_engine is not None}


@app.post("/api/ocr")
async def run_ocr(file: UploadFile = File(...)):
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Upload a PNG, JPG, WEBP, or PDF file.")
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Maximum upload size is 10 MB.")

    pages = image_arrays(data, content_type)
    try:
        engine = get_ocr()
        output = []
        for page_number, image in enumerate(pages, start=1):
            raw = engine.ocr(image, cls=True)
            lines = []
            if raw and raw[0]:
                for item in raw[0]:
                    if len(item) > 1 and item[1]:
                        text, confidence = item[1][0], float(item[1][1])
                        lines.append({"text": text, "confidence": round(confidence, 4)})
            output.append({"page": page_number, "lines": lines,
                           "text": "\n".join(line["text"] for line in lines)})
        return {
            "filename": file.filename or "upload",
            "pages": output,
            "text": "\n\n".join(
                f"--- Page {page['page']} ---\n{page['text']}" if len(output) > 1 else page["text"]
                for page in output
            ),
            "line_count": sum(len(page["lines"]) for page in output),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, "OCR processing failed. Check the Space logs for details.") from exc


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OCR Go — Extract text from anything</title>
<style>
:root{color-scheme:dark;--bg:#090b10;--panel:#11151e;--line:#262c3a;--muted:#98a2b3;--blue:#73a7ff;--white:#f4f7ff}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 50% -25%,#1c3156 0,transparent 55%),var(--bg);color:var(--white);font:15px/1.5 Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;min-height:100vh}
main{width:min(920px,calc(100% - 32px));margin:0 auto;padding:28px 0 60px}.nav{display:flex;align-items:center;justify-content:space-between;color:var(--muted);font-size:13px}.brand{font-size:18px;color:white;font-weight:750;letter-spacing:-.5px}.brand span{color:var(--blue)}.pill{border:1px solid var(--line);border-radius:99px;padding:6px 10px}
.hero{text-align:center;padding:66px 0 30px}.eyebrow{color:var(--blue);font-size:12px;letter-spacing:2px;font-weight:750}.hero h1{font-size:clamp(36px,6vw,58px);letter-spacing:-2px;line-height:1.06;margin:14px 0}.hero p{color:var(--muted);font-size:16px;margin:0 auto;max-width:540px}
.panel{background:rgba(17,21,30,.9);border:1px solid var(--line);border-radius:20px;padding:22px;box-shadow:0 20px 70px #0004}.drop{min-height:230px;border:1px dashed #46516a;border-radius:14px;display:flex;align-items:center;justify-content:center;text-align:center;padding:24px;cursor:pointer;transition:.2s}.drop:hover,.drop.over{border-color:var(--blue);background:#18243a}.upload-icon{font-size:34px}.drop h2{font-size:18px;margin:10px 0 4px}.sub{font-size:13px;color:var(--muted)}button{border:0;border-radius:10px;background:var(--blue);color:#08101f;font-weight:750;padding:12px 18px;cursor:pointer;font-size:14px}button:disabled{opacity:.5;cursor:wait}.actions{display:flex;justify-content:center;margin-top:18px}.status{margin-top:14px;text-align:center;color:var(--muted);font-size:13px;min-height:20px}.results{margin-top:18px;display:none}.result-head{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:12px}.result-head h2{font-size:17px;margin:0}.smallbtn{background:#202a3c;color:var(--white);padding:9px 12px}.result-text{white-space:pre-wrap;overflow-wrap:anywhere;min-height:150px;max-height:480px;overflow:auto;background:#090c12;border:1px solid var(--line);padding:18px;border-radius:12px;color:#dce5f5;font:14px/1.7 ui-monospace,SFMono-Regular,Consolas,monospace}.meta{color:var(--muted);font-size:12px;margin-top:9px}.footer{text-align:center;color:#667085;font-size:12px;margin-top:22px}input{display:none}
@media(max-width:560px){.hero{padding-top:48px}.panel{padding:13px}.drop{min-height:200px}.pill{display:none}}
</style></head>
<body><main>
<nav class="nav"><div class="brand">OCR<span>GO</span></div><div class="pill">Powered by PaddleOCR</div></nav>
<header class="hero"><div class="eyebrow">DOCUMENT INTELLIGENCE</div><h1>Make every word<br>searchable.</h1><p>Extract text from images and PDFs in seconds. Upload a file and let OCR do the heavy lifting.</p></header>
<section class="panel">
<label class="drop" id="drop" for="file"><div><div class="upload-icon">↥</div><h2 id="fileTitle">Drop your file here</h2><div class="sub" id="fileSub">or click to browse · PNG, JPG, WEBP, PDF</div><div class="sub" style="margin-top:8px">Maximum 10 MB · PDF up to 10 pages</div></div></label>
<input id="file" type="file" accept="image/png,image/jpeg,image/webp,application/pdf">
<div class="actions"><button id="run" disabled>Extract text →</button></div><div class="status" id="status" role="status"></div>
<div class="results" id="results"><div class="result-head"><h2>Extracted text</h2><div><button class="smallbtn" id="copy">Copy text</button> <button class="smallbtn" id="download">Download .txt</button></div></div><div class="result-text" id="output"></div><div class="meta" id="meta"></div></div>
</section><div class="footer">Your file is processed for this request and is not saved by this app.</div>
</main>
<script>
const fileInput=document.getElementById('file'),drop=document.getElementById('drop'),run=document.getElementById('run'),statusEl=document.getElementById('status');let selected=null,resultText='';
function selectFile(file){if(!file)return;selected=file;document.getElementById('fileTitle').textContent=file.name;document.getElementById('fileSub').textContent=(file.size/1024/1024).toFixed(2)+' MB · Ready to process';run.disabled=false;statusEl.textContent='';document.getElementById('results').style.display='none'}
fileInput.addEventListener('change',()=>selectFile(fileInput.files[0]));['dragenter','dragover'].forEach(e=>drop.addEventListener(e,x=>{x.preventDefault();drop.classList.add('over')}));['dragleave','drop'].forEach(e=>drop.addEventListener(e,x=>{x.preventDefault();drop.classList.remove('over')}));drop.addEventListener('drop',e=>selectFile(e.dataTransfer.files[0]));
run.addEventListener('click',async()=>{if(!selected)return;run.disabled=true;statusEl.textContent='Loading OCR engine and reading your file… first run may take a little longer.';try{const data=new FormData();data.append('file',selected);const response=await fetch('/api/ocr',{method:'POST',body:data});const payload=await response.json();if(!response.ok)throw new Error(payload.detail||'OCR failed');resultText=payload.text||'';document.getElementById('output').textContent=resultText||'No readable text was found in this file.';document.getElementById('meta').textContent=payload.line_count+' text lines · '+payload.pages.length+' page(s)';document.getElementById('results').style.display='block';statusEl.textContent='Done.'}catch(e){statusEl.textContent=e.message||'Something went wrong.'}finally{run.disabled=false}});
document.getElementById('copy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(resultText);statusEl.textContent='Text copied.'}catch(e){statusEl.textContent='Clipboard access unavailable; select the text to copy.'}});
document.getElementById('download').addEventListener('click',()=>{const blob=new Blob([resultText],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=(selected?.name||'ocr-result').replace(/\.[^.]+$/,'')+'.txt';a.click();URL.revokeObjectURL(url)});
</script></body></html>""")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "7860")))
