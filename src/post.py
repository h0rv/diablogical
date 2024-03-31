import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import List, TypedDict

from .audio_file import AudioFile
from .db import JSONDatabase


@dataclass
class Post:
    id: str
    title: str
    url: str
    date: datetime
    summary: str
    access_count: int = 0
    audio_files: List[AudioFile] = field(default_factory=list)

    def add_audio_file(self, audio_file: AudioFile) -> None:
        self.audio_files.append(
            {"file_name": f"{audio_file.file_name}.json", "audio_file": audio_file}
        )

    def get_audio_file_metadata(self, file_name: str) -> AudioFile:
        # Implement logic to retrieve audio file metadata from storage
        pass

    def store_json(self, db: JSONDatabase) -> None:
        """
        Store the Post instance in the database.

        Args:
            db (JSONDatabase): The database instance to use for storing the post.
        """
        post_dict = asdict(self)
        post_dict["date"] = self.date.isoformat()

        db.set(self.id, post_dict)

        for audio_file_info in self.audio_files:
            file_name = audio_file_info["file_name"]
            base_name, _ = os.path.splitext(file_name)
            audio_file_metadata = self.get_audio_file_metadata(base_name)

            if audio_file_metadata:
                audio_file_dict = asdict(audio_file_metadata)
                audio_file_dict["generated_date"] = (
                    audio_file_metadata.generated_date.isoformat()
                )
                db.set(file_name, audio_file_dict)
            else:
                print(f"Warning: Failed to retrieve metadata for {file_name}")
