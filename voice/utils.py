import re
import os
from typing import Optional


def download_kokoro_models(cache_dir: Optional[str] = None) -> tuple[str, str]:
    import urllib.request

    if cache_dir is None:
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "kokoro-onnx")

    os.makedirs(cache_dir, exist_ok=True)

    base_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
    files = {
        "kokoro-v1.0.onnx": os.path.join(cache_dir, "kokoro-v1.0.onnx"),
        "voices-v1.0.bin": os.path.join(cache_dir, "voices-v1.0.bin"),
    }

    for filename, filepath in files.items():
        if not os.path.exists(filepath):
            url = f"{base_url}/{filename}"
            print(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, filepath)
            print(f"Downloaded {filename}")

    return files["kokoro-v1.0.onnx"], files["voices-v1.0.bin"]


def clean_for_speech(text: str) -> str:
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[#*_~|><\[\]{}\\^]', '', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
