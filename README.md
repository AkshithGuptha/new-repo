---
title: OCR Go — PaddleOCR
emoji: 🔎
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# OCR Go — PaddleOCR

A deployable OCR web application powered by [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR).

## Features

- Upload PNG, JPG/JPEG, WEBP, or PDF files.
- Extract text with PaddleOCR's English OCR model.
- Process PDFs up to 10 pages (rendered page-by-page).
- Copy extracted text or download it as a .txt file.
- No database or permanent file storage.
- FastAPI backend and a responsive single-page interface.

## Deploy to Hugging Face Spaces

1. Create a new Space and select **Docker** as the SDK.
2. Connect this repository in the Space settings.
3. The Space builds from the root `Dockerfile` and listens on port `7860`.
4. Wait for the initial build and OCR model download. The first OCR request can take longer while the model initializes.

## Run locally

Requires Python 3.10 and system libraries used by PaddlePaddle/OpenCV.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```

Open http://localhost:7860. Health check: http://localhost:7860/health.

## Limits and notes

- Upload limit: 10 MB; PDF limit: 10 pages.
- This image uses CPU inference. Cold starts and model downloads may be slow on free hardware.
- The included OCR configuration targets English. Configure additional PaddleOCR language models for other languages.
- The upstream PaddleOCR project is distributed under Apache License 2.0. Review upstream and model licenses before redistribution or commercial use.

---

## Existing Vite starter notes

The original React + Vite starter README is preserved below.

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
