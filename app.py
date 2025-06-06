import os
import traceback
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ingestion import clean_transcript, extract_pdf_text
from preprocess import normalize_text, chunk_text
from generate import generate_chunk_notes
from assemble import build_pdf  # must support new format

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate_notes(
    request: Request,
    file: UploadFile = File(None),
    raw_text: str = Form(None)
):
    try:
        # 1. Read input
        if file:
            suffix = os.path.splitext(file.filename)[1].lower()
            data = await file.read()

            if suffix == ".txt":
                raw = data.decode("utf-8", errors="ignore")
            elif suffix == ".pdf":
                tmp = "tmp_upload.pdf"
                with open(tmp, "wb") as f:
                    f.write(data)
                raw = extract_pdf_text(tmp)
                os.remove(tmp)
            elif suffix in [".text", ".md"]:
                raw = data.decode("utf-8", errors="ignore")
            else:
                raise HTTPException(400, "Only .txt, .text or .pdf files are allowed.")
        elif raw_text:
            raw = raw_text
        else:
            raise HTTPException(400, "No input text or file provided.")

        # 2. Clean and chunk
        cleaned = clean_transcript(raw)
        norm = normalize_text(cleaned)
        chunks = chunk_text(norm)

        if not chunks:
            raise HTTPException(422, "No meaningful content found in the input.")

        # 3. Generate freeform notes per chunk
        notes = []

        for idx, chunk in enumerate(chunks):
            print(f"🧠 Generating notes for chunk {idx + 1}/{len(chunks)}")
            section = generate_chunk_notes(chunk)  # returns dict with title + content
            notes.append(section)

        # 4. Build final PDF (expects notes = [{title: ..., content: ...}, ...])
        print(notes)
        out = "notes_output.pdf"
        build_pdf(notes, out)

        return FileResponse(
            out,
            filename="your_notes.pdf",
            media_type="application/pdf"
        )

    except Exception as e:
        traceback.print_exc()
        return PlainTextResponse(f"❌ Error:\n{e}", status_code=500)
