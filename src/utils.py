import re
from os import path

import requests
from bs4 import BeautifulSoup


def clean_url(url: str) -> str:
    cleaned_url = url

    if url.startswith("http://") or url.startswith("https://"):
        cleaned_url = cleaned_url.split("://")[-1]

    return cleaned_url


def clean_html(html):
    # Remove script and style tags
    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()

    # Get text with preserved line breaks
    text = soup.get_text(separator="\n")

    # Collapse multiple consecutive newlines into a single newline
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def url_to_text(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful

        cleaned_text = clean_html(response.text)

        cleaned_text_file = path.join("debug", "cleaned_text.txt")
        with open(cleaned_text_file, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        return cleaned_text

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return ""


def url_to_filename(url):
    filename = re.sub(r"\W+", "_", url)
    filename = filename.strip("_")
    filename = filename[:255]

    return filename
