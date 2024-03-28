import os
import re

from fastapi import FastAPI, HTTPException, Response

from .tts import Piper
from .utils import url_to_filename, url_to_text

app = FastAPI()

piper: Piper


OUTPUT_DIR = "./output"


@app.on_event("startup")
async def startup_event():
    global piper
    piper = Piper()


@app.get("/", response_class=Response, include_in_schema=False)
async def index():
    try:
        # Fetch the list of audio files using the /file_list route
        response = await file_list()
        audio_files = response["files"]
        html_audio_files_list = "\n".join(
            [
                f"<li><a href='#' onclick='playAudio(\"{audio_file}\")'>{audio_file}</a></li>"
                for audio_file in audio_files
            ]
        )
        # Generate HTML dynamically with audio file links
        html = f"""
        <!DOCTYPE html>
        <html lang="en" color-mode="user">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta name="color-scheme" content="light dark" />
            <title>Diablogical</title>
            <style>
                body {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 8rem;
                    margin-left: 16rem;
                    padding: 0;
                }}
                .container {{
                    max-height: 80vh;
                    overflow: auto;
                    padding: 4rem;
                    width: 100%;
                }}
                .audio-container {{
                    position: fixed;
                    bottom: 0;
                    left: 0;
                    width: 100%;
                    background-color: #1b1a1c;
                    padding: 1.25rem;
                    text-align: center;
                    .audio {{
                        width: 100%;
                    }}
                }}
                .audio-container audio {{
                    width: 80%;
                }}
                .audio-list {{
                    max-height: 200px; /* Adjust as needed */
                    overflow-y: auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Diablogical</h1>
                <input type="text" id="textInput" placeholder="Blog URL">
                <button onclick="submitText()">Submit</button>
                <div class="audio-list">
                    <ul>
                        {html_audio_files_list}
                    </ul>
                </div>
            <div class="audio-container">
                <audio id="audioPlayer" controls> </audio>
                <br>
                <label for="playbackSpeedSlider">Playback Speed:</label>
                <input type="range" id="playbackSpeedSlider" min="0.0" max="2" step="0.05" value="1">
                <span id="playbackSpeedValue">1</span>
            </div>

            <script>
                const audioPlayer = document.getElementById('audioPlayer');
                const playbackSpeedSlider = document.getElementById('playbackSpeedSlider');
                const playbackSpeedValue = document.getElementById('playbackSpeedValue');

                function playAudio(audioSrc) {{
                    audioPlayer.src = '/play/' + audioSrc;  // Changed to use /play route
                    audioPlayer.play();
                }}
                playbackSpeedSlider.addEventListener('input', () => {{
                    audioPlayer.playbackRate = playbackSpeedSlider.value;
                    playbackSpeedValue.textContent = playbackSpeedSlider.value;
                }});
            </script>
        </body>
        </html>
        """

        return Response(content=html, media_type="text/html")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/file_list")
async def file_list():
    try:
        files = [
            filename
            for filename in os.listdir(OUTPUT_DIR)
            if os.path.isfile(os.path.join(OUTPUT_DIR, filename))
        ]
        print("File list retrieved successfully")
        return {"files": files}
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


@app.get("/{url:path}")
def url_path(url: str) -> str:
    global piper

    # url = clean_url(url)
    if not re.match(r"^(https?|www)\:\/\/", url):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    print(f"URL: {url}")

    text = url_to_text(url)
    filename = url_to_filename(url)

    output_file = piper.tts(text, filename)

    return output_file
