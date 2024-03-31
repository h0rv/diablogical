import base64
import os
import re
from os import path
from typing import List, Optional

import html2text
import trafilatura

OUTPUT_DIR = "./output"
SITE_PREFIXES = ["http", "https", "www"]


def is_valid_url(url: str) -> bool:
    return re.match(r"^(https?|www)\:\/\/", url) is not None


def clean_url(url: str) -> str:
    # Implement your URL cleaning logic here
    return url


def url_to_text(url: str) -> str:
    html = trafilatura.fetch_url(url)
    text = trafilatura.extract(html)

    with open(path.join("debug", "extracted_text.txt"), "w", encoding="utf-8") as f:
        f.write(text)

    return text


def url_to_markdown(url: str) -> str:
    html = trafilatura.fetch_url(url)

    converter = html2text.HTML2Text()
    markdown_text = converter.handle(html)

    with open(path.join("debug", "extracted_text.md"), "w", encoding="utf-8") as f:
        f.write(markdown_text)

    return markdown_text


def remove_prefixes(string: str, prefixes: List[str]) -> str:
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


def generate_uid_from_url(url):
    # Encode the URL string to bytes
    url_bytes = url.encode("utf-8")

    # Encode the URL bytes using Base64
    uid_bytes = base64.b64encode(url_bytes)

    # Convert the Base64 encoded bytes to a string
    uid = uid_bytes.decode("utf-8")

    return uid


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
