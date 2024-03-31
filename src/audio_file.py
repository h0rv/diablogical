from dataclasses import dataclass
from datetime import datetime


@dataclass
class AudioFile:
    model_name: str
    model_voice: str

    file_name: str
    content_type: str
    duration: float
    size: int
    language: str
    text_segment: str
    generated_date: datetime

    access_count: int = 0
