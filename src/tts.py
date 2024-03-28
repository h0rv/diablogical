import os
import platform
import subprocess
import tarfile
import urllib.request

# import ffmpeg


class Piper:
    """
    Code derived from https://github.com/OpenInterpreter/01/blob/dd415dbd9426a69ba8f83e29690adea63d77be6e/software/source/server/services/tts/piper/tts.py#L80
    """

    piper_download_url = "https://github.com/rhasspy/piper/releases/latest/download/"
    phonemize_download_url = (
        "https://github.com/rhasspy/piper-phonemize/releases/latest/download/"
    )

    voice_url = (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/"
    )
    voice_name = "en_US-lessac-high.onnx"

    piper_dir: str
    output_dir: str
    bin_path: str

    def __init__(self, piper_dir: str = "data", output_dir: str = "output"):
        self.piper_dir = piper_dir
        self.output_dir = output_dir
        self.bin_path = os.path.join(self.piper_dir, "piper", "piper")
        self.model_path = os.path.join(self.piper_dir, self.voice_name)
        self.install()

    def tts(self, text: str, filename: str, file_type="wav") -> str:
        output_file = f"{filename}.{file_type}"
        output_path = os.path.join(self.output_dir, output_file)

        os.makedirs(self.output_dir, exist_ok=True)

        print(f"Starting text-to-speech conversion. Output file: {output_path}")
        self.piper(text, output_path)

        return output_file

    def piper(self, text, output_path) -> None:
        try:
            command = [
                self.bin_path,
                "--model",
                self.model_path,
                "--output_file",
                output_path,
            ]
            subprocess_arguments = {
                "input": text,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "text": True,
            }

            subprocess.run(command, **subprocess_arguments)

            print("Text-to-speech conversion completed successfully.")
        except Exception as e:
            print(f"Text-to-speech conversion failed: {e}")

    def install(self):
        if not os.path.isdir(self.piper_dir):
            os.makedirs(self.piper_dir, exist_ok=True)

            # Determine OS and architecture
            OS = platform.system()
            ARCH = platform.machine()
            if OS == "Darwin":
                OS = "macos"
                if ARCH == "arm64":
                    ARCH = "aarch64"
                elif ARCH == "x86_64":
                    ARCH = "x64"
                else:
                    print("Piper: unsupported architecture")
                    return
            elif OS == "Windows":
                if ARCH == "AMD64":
                    ARCH = "x64"
                else:
                    print("Piper: unsupported architecture")
                    return

            piper_asset_name = f"piper_{OS}_{ARCH}.tar.gz"
            piper_asset_path = os.path.join(self.piper_dir, piper_asset_name)
            piper_asset_url = f"{self.piper_download_url}{piper_asset_name}"

            if OS == "windows":
                piper_asset_url = piper_asset_url.replace(".tar.gz", ".zip")

            # Download and extract Piper
            urllib.request.urlretrieve(piper_asset_url, piper_asset_path)

            # Extract the downloaded file
            if OS == "windows":
                import zipfile

                with zipfile.ZipFile(piper_asset_path, "r") as zip_ref:
                    zip_ref.extractall(path=self.piper_dir)
            else:
                with tarfile.open(piper_asset_path, "r:gz") as tar:
                    tar.extractall(path=self.piper_dir)

            # Download voice model and its json file
            urllib.request.urlretrieve(
                f"{self.voice_url}{self.voice_name}",
                os.path.join(self.piper_dir, self.voice_name),
            )
            urllib.request.urlretrieve(
                f"{self.voice_url}{self.voice_name}.json",
                os.path.join(self.piper_dir, f"{self.voice_name}.json"),
            )

            # Additional setup for macOS
            if OS == "macos":
                if ARCH == "x64":
                    subprocess.run(
                        ["softwareupdate", "--install-rosetta", "--agree-to-license"]
                    )

                phonemize_asset_name = f"piper-phonemize_{OS}_{ARCH}.tar.gz"
                phonemize_asset_path = (
                    os.path.join(self.piper_dir, phonemize_asset_name),
                )
                phonemize_asset_url = (
                    f"{self.phonemize_download_url}{phonemize_asset_name}"
                )
                urllib.request.urlretrieve(
                    phonemize_asset_url,
                    phonemize_asset_path,
                )

                with tarfile.open(
                    phonemize_asset_path,
                    "r:gz",
                ) as tar:
                    tar.extractall(path=self.piper_dir)

                subprocess.run(
                    [
                        "install_name_tool",
                        "-change",
                        "@rpath/libespeak-ng.1.dylib",
                        f"{self.piper_dir}/piper-phonemize/lib/libespeak-ng.1.dylib",
                        f"{self.piper_dir}/piper",
                    ]
                )
                subprocess.run(
                    [
                        "install_name_tool",
                        "-change",
                        "@rpath/libonnxruntime.1.14.1.dylib",
                        f"{self.piper_dir}/piper-phonemize/lib/libonnxruntime.1.14.1.dylib",
                        f"{self.piper_dir}/piper",
                    ]
                )
                subprocess.run(
                    [
                        "install_name_tool",
                        "-change",
                        "@rpath/libpiper_phonemize.1.dylib",
                        f"{self.piper_dir}/piper-phonemize/lib/libpiper_phonemize.1.dylib",
                        f"{self.piper_dir}/piper",
                    ]
                )

            print("Piper setup completed.")
        else:
            print("Piper already set up. Skipping download.")
