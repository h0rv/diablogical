# import torch
from TTS.api import TTS

# Get device
device = "cpu"
# device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
# print(str(TTS().list_models()))

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# # Run TTS
# # ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# # Text to speech list of amplitude values as output
# wav = tts.tts(text="Hello world!", speaker_wav="output/audio.wav", language="en")
# Text to speech to a file
tts.tts_to_file(
    text="Hello world!",
    speaker_wav="output/audio.wav",
    language="en",
    file_path="output.wav",
)
