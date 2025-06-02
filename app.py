import os
import traceback
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ingestion import clean_transcript, extract_pdf_text
from preprocess import normalize_text, chunk_text
from generate import generate_chunk_notes
from diagrams import gen_diagram
from assemble import build_pdf

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate(request: Request, file: UploadFile = File(...)):
    try:
        # 1. Read & extract
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
        else:
            raise HTTPException(400, "Only .txt or .pdf files are allowed.")

        # 2. Clean and chunk
        cleaned = clean_transcript(raw)
        norm = normalize_text(cleaned)
        chunks = chunk_text(norm)

        if not chunks:
            raise HTTPException(422, "No meaningful content found in the uploaded file.")

        # 3. Generate notes per chunk
        notes = []
        seen = set()

        for idx, chunk in enumerate(chunks):
            print(f"🧠 Generating notes for chunk {idx + 1}/{len(chunks)}")

            # Truncate overly long chunks if needed (safe side)
            if len(chunk) > 4000:
                chunk = chunk[:4000]

            sec = generate_chunk_notes(chunk)

            # Deduplicate bullets
            unique = []
            for b in sec.get("bullets", []):
                key = b.lower()
                if key not in seen:
                    unique.append(b)
                    seen.add(key)
            sec["bullets"] = unique

            # Generate diagram if prompt is present
            dp = sec.get("diagram_prompt")
            if dp:
                try:
                    path = gen_diagram(dp)
                    if path:
                        sec["diagram_path"] = path
                except Exception as e:
                    print(f"⚠️ Failed to generate diagram: {e}")

            notes.append(sec)

        # 4. Build and return PDF
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
