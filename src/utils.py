import re
from os import path

import trafilatura


def url_to_text(url: str) -> str:
    html = trafilatura.fetch_url(url)
    text = trafilatura.extract(html)

    with open(path.join("debug", "extracted_text.txt"), "w", encoding="utf-8") as f:
        f.write(text)

    return text


def remove_prefixes(string: str, prefixes: [str]) -> str:
    return string.lstrip(
        tuple(prefix for prefix in prefixes if string.startswith(prefix))
    )


def url_to_filename(url: str) -> str:
    filename = re.sub(r"\W+", "_", url)
    filename = filename.strip("_")
    filename = remove_prefixes(filename, ["http", "https", "www"])
    filename = filename.strip("_")
    filename = filename[:255]

    return filename
