import os
import re
from os import path
from typing import List, Optional, Any

import trafilatura


OUTPUT_DIR = "./output"
SITE_PREFIXES = ["http", "https", "www"]


def url_to_text(url: str) -> str:
    html = trafilatura.fetch_url(url)
    text = trafilatura.extract(html)

    with open(path.join("debug", "extracted_text.txt"), "w", encoding="utf-8") as f:
        f.write(text)

    return text


def remove_prefixes(string: str, prefixes: [str]) -> str:
    return string.lstrip(
        str(tuple(prefix for prefix in prefixes if string.startswith(prefix)))
    )


def remove_site_prefixes(string: str) -> str:
    return remove_prefixes(string, SITE_PREFIXES)


def url_to_filename(url: str) -> str:
    filename = re.sub(r"\W+", "_", url)
    filename = filename.strip("_")
    filename = remove_site_prefixes(filename)
    filename = filename.strip("_")
    filename = filename[:255]

    return filename


def get_audio_files() -> List[str]:
    files = [
        filename
        for filename in os.listdir(OUTPUT_DIR)
        if os.path.isfile(os.path.join(OUTPUT_DIR, filename))
    ]
    return files


def get_audio_file_path(filename: str) -> Optional[str]:
    # Sanitize filename
    filename = os.path.basename(filename)
    audio_file_path = os.path.join(OUTPUT_DIR, filename)

    # Check if file exists
    if not os.path.exists(audio_file_path):
        None

    return audio_file_path
