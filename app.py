import io
import threading

import fitz
import gradio as gr
import numpy as np
from PIL import Image, ImageOps
from paddleocr import PaddleOCR

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
_ocr_engine = None
_ocr_lock = threading.Lock()


def get_ocr():
    global _ocr_engine
    if _ocr_engine is None:
        with _ocr_lock:
            if _ocr_engine is None:
                _ocr_engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    return _ocr_engine


def to_images(file_path):
    if not file_path:
        raise gr.Error("Upload an image or PDF first.")
    with open(file_path, "rb") as handle:
        data = handle.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise gr.Error("The uploaded file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise gr.Error("Maximum upload size is 10 MB.")

    if file_path.lower().endswith(".pdf"):
        try:
            doc = fitz.open(stream=data, filetype="pdf")
            if doc.page_count > 10:
                doc.close()
                raise gr.Error("PDFs are limited to 10 pages per upload.")
            images = []
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
                images.append(np.array(Image.frombytes("RGB", [pix.width, pix.height], pix.samples)))
            doc.close()
            return images
        except gr.Error:
            raise
        except Exception as exc:
            raise gr.Error("Could not read this PDF.") from exc

    try:
        image = Image.open(io.BytesIO(data))
        return [np.array(ImageOps.exif_transpose(image).convert("RGB"))]
    except Exception as exc:
        raise gr.Error("Could not read this image.") from exc


def extract_text(file_path):
    images = to_images(file_path)
    try:
        engine = get_ocr()
        all_pages = []
        for page_number, image in enumerate(images, start=1):
            raw = engine.ocr(image, cls=True)
            lines = []
            if raw and raw[0]:
                for item in raw[0]:
                    if len(item) > 1 and item[1]:
                        lines.append((item[1][0], float(item[1][1])))
            page_text = "\n".join(text for text, _ in lines)
            all_pages.append((page_number, page_text, lines))

        output = []
        for page_number, page_text, _ in all_pages:
            output.append(f"--- Page {page_number} ---\n{page_text}" if len(all_pages) > 1 else page_text)
        text_result = "\n\n".join(output).strip()
        total_lines = sum(len(lines) for _, _, lines in all_pages)
        detail = f"Processed {len(all_pages)} page(s) · {total_lines} text line(s)"
        return text_result or "No readable text was found in this file.", detail
    except gr.Error:
        raise
    except Exception as exc:
        raise gr.Error("OCR processing failed. Please retry; the Space logs may contain details.") from exc


with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"), title="OCR Go — PaddleOCR", css="""
.gradio-container {max-width: 1000px !important; margin: auto !important}
#hero {text-align:center; padding: 22px 0 12px}
#hero h1 {font-size: clamp(2.1rem, 5vw, 3.5rem); letter-spacing:-1.5px}
#hero p {color: var(--body-text-color-subdued)}
#result textarea {font-family: ui-monospace, SFMono-Regular, Consolas, monospace}
""") as demo:
    gr.HTML("""
    <div id="hero">
      <p style="letter-spacing:3px;font-weight:700;color:#73a7ff">DOCUMENT INTELLIGENCE</p>
      <h1>OCR Go — Make every word searchable.</h1>
      <p>Extract text from images and PDFs with PaddleOCR. Free CPU demo.</p>
    </div>
    """)
    with gr.Row():
        with gr.Column(scale=1):
            upload = gr.File(label="Upload image or PDF", file_types=[".png", ".jpg", ".jpeg", ".webp", ".pdf"], type="filepath")
            gr.Markdown("**Limits:** 10 MB per file · PDFs up to 10 pages · English OCR")
            run = gr.Button("Extract text", variant="primary")
        with gr.Column(scale=2):
            result = gr.Textbox(label="Extracted text", lines=16, max_lines=30, elem_id="result", placeholder="Your extracted text will appear here.")
            details = gr.Markdown("Upload a file to get started.")
            with gr.Row():
                copy_hint = gr.Markdown("Select the result text to copy, or download it as a text file.")
    run.click(fn=extract_text, inputs=upload, outputs=[result, details])

if __name__ == "__main__":
    demo.queue(default_concurrency_limit=1).launch(server_name="0.0.0.0", server_port=7860)
