import re
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .tts import Piper
from .utils import get_audio_file_path, get_audio_files, url_to_filename, url_to_text

app = FastAPI()

templates = Jinja2Templates(directory="src/templates")

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
        files = get_audio_files()
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
        file_path = get_audio_file_path(filename)
        # Stream audio file
        if not file_path:
            raise HTTPException(status_code=404, detail="Audio file not found")

        print(f"Streaming audio file: {file_path}")
        with open(file_path, "rb") as audio_file:
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
async def process_form_url(request: Request):
    try:
        form_data = await request.form()
        url = form_data.get("url")
        if not isinstance(url, str):
            raise
        return await process_url(request, url)
    except Exception as e:
        print(f"Error processing form URL: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/{url:path}")
async def process_url(request: Request, url: str):
    global piper
    try:
        # Clean url
        print(f"Uncleaned URL: {url}")
        url = clean_url(unquote(url))
        if not is_valid_url(url):
            raise HTTPException(status_code=400, detail="Invalid URL format")
        print(f"Cleaned URL: {url}")
        text = url_to_text(url)
        filename = url_to_filename(url)
        generated_audio_file = piper.tts(text, filename)
        print(f"Generated audio file to {generated_audio_file}")
        response = await file_list(request)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
