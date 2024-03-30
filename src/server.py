import os
from urllib.parse import unquote
import re

from fastapi import FastAPI, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .tts import Piper
from .utils import url_to_filename, url_to_text

app = FastAPI()

templates = Jinja2Templates(directory="src/templates")


OUTPUT_DIR = "./output"

piper: Piper


@app.on_event("startup")
async def startup_event():
    global piper
    piper = Piper()


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="HTML file not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/file_list", response_class=HTMLResponse)
async def file_list(request: Request):
    try:
        files = [
            filename
            for filename in os.listdir(OUTPUT_DIR)
            if os.path.isfile(os.path.join(OUTPUT_DIR, filename))
        ]
        print("File list retrieved successfully")
        return templates.TemplateResponse(
            "file_list.html", {"request": request, "files": files}
        )
    except FileNotFoundError:
        print("Output directory not found")
        raise HTTPException(status_code=404, detail="Output directory not found")
    except Exception as e:
        print(f"Error retrieving file list: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/play/{filename}")
async def play(filename: str):
    print(f"Requested file: {filename}")
    try:
        # Sanitize filename
        filename = os.path.basename(filename)
        audio_file_path = os.path.join(OUTPUT_DIR, filename)

        # Check if file exists
        if not os.path.exists(audio_file_path):
            print(f"Audio file not found: {filename}")
            raise HTTPException(status_code=404, detail="Audio file not found")

        # Stream audio file
        print(f"Streaming audio file: {filename}")
        with open(audio_file_path, "rb") as audio_file:
            file_content = audio_file.read()
        return Response(content=file_content, media_type="audio/wav")

    except Exception as e:
        print(f"Error streaming audio file: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def is_valid_url(url: str) -> bool:
    return re.match(r"^(https?|www)\:\/\/", url) is not None


def clean_url(url: str) -> str:
    # Implement your URL cleaning logic here
    return url


@app.post("/process_url")
async def process_url_form(request: Request, url: str = Form(...)):
    return RedirectResponse(url=f"/{url}")

@app.get("/{url:path}")
async def process_url(request: Request, url: str):
    global piper
    try:
        # Clean url
        url = clean_url(unquote(url))
        if not is_valid_url(url):
            raise HTTPException(status_code=400, detail="Invalid URL format")
        print(f"URL: {url}")
        text = url_to_text(url)
        filename = url_to_filename(url)
        generated_audio_file = piper.tts(text, filename)
        return templates.TemplateResponse(
            "file_list.html", {"request": request, "files": [generated_audio_file]}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
